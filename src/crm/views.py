from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q, Sum, Avg, Count
from django.utils import timezone

from .models import Account, Lead, Opportunity, Task, Note, Campaign
from .serializers import (
    AccountSerializer, AccountListSerializer,
    LeadSerializer, LeadListSerializer,
    OpportunitySerializer, OpportunityListSerializer,
    TaskSerializer, TaskListSerializer,
    NoteSerializer,
    CampaignSerializer, CampaignListSerializer
)
from .permissions import AllowOptionsAuthentication


class AccountViewSet(viewsets.ModelViewSet):
    """ViewSet for managing accounts"""
    queryset = Account.objects.all()
    permission_classes = [AllowOptionsAuthentication]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['account_type', 'industry', 'owner']
    search_fields = ['name', 'email', 'phone']
    ordering_fields = ['name', 'created_at', 'updated_at']
    ordering = ['-created_at']

    def get_serializer_class(self):
        if self.action == 'list':
            return AccountListSerializer
        return AccountSerializer

    def get_queryset(self):
        queryset = Account.objects.all()
        if not self.request.user.is_superuser:
            # Filter to show only accounts owned by or created by the user
            queryset = queryset.filter(
                Q(owner=self.request.user) | Q(created_by=self.request.user)
            )
        return queryset

    @action(detail=True, methods=['get'])
    def summary(self, request, pk=None):
        """Get a summary of account-related data"""
        account = self.get_object()
        data = {
            'opportunities_count': account.opportunities.count(),
            'total_opportunity_value': account.opportunities.aggregate(
                total=Sum('amount')
            )['total'] or 0,
            'tasks_count': account.tasks.count(),
            'open_tasks_count': account.tasks.exclude(status='completed').count(),
            'notes_count': account.notes.count(),
        }
        return Response(data)


class LeadViewSet(viewsets.ModelViewSet):
    """ViewSet for managing leads"""
    queryset = Lead.objects.all()
    permission_classes = [AllowOptionsAuthentication]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'source', 'rating', 'owner']
    search_fields = ['first_name', 'last_name', 'company', 'email']
    ordering_fields = ['first_name', 'last_name', 'company', 'created_at']
    ordering = ['-created_at']

    def get_serializer_class(self):
        if self.action == 'list':
            return LeadListSerializer
        return LeadSerializer

    def get_queryset(self):
        queryset = Lead.objects.all()
        if not self.request.user.is_superuser:
            queryset = queryset.filter(owner=self.request.user)
        return queryset

    @action(detail=True, methods=['post'])
    def convert(self, request, pk=None):
        """Convert a lead to an account and opportunity"""
        lead = self.get_object()
        
        if lead.status == 'converted':
            return Response(
                {'error': 'Lead is already converted'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Create account
        account_data = {
            'name': lead.company or f"{lead.first_name} {lead.last_name}",
            'account_type': 'customer',
            'phone': lead.phone,
            'email': lead.email,
            'website': lead.website,
            'description': lead.description,
            'owner': lead.owner,
            'created_by': request.user,
        }
        account = Account.objects.create(**account_data)

        # Create opportunity if requested
        opportunity_data = request.data.get('opportunity', {})
        if opportunity_data:
            opportunity_data.update({
                'account': account,
                'owner': lead.owner,
                'name': opportunity_data.get('name', f"Opportunity from {lead.first_name} {lead.last_name}"),
                'close_date': opportunity_data.get('close_date', timezone.now().date()),
            })
            opportunity = Opportunity.objects.create(**opportunity_data)

        # Update lead status
        lead.status = 'converted'
        lead.converted_account = account
        lead.save()

        return Response({
            'message': 'Lead converted successfully',
            'account_uuid': str(account.account_uuid),
            'opportunity_uuid': str(opportunity.opportunity_uuid) if opportunity_data else None,
        })

    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Get lead statistics"""
        queryset = self.get_queryset()
        stats = {
            'total_leads': queryset.count(),
            'by_status': {
                status_choice[0]: queryset.filter(status=status_choice[0]).count()
                for status_choice in Lead.STATUS_CHOICES
            },
            'by_source': {
                source_choice[0]: queryset.filter(source=source_choice[0]).count()
                for source_choice in Lead.SOURCE_CHOICES
            },
            'by_rating': {
                'hot': queryset.filter(rating='hot').count(),
                'warm': queryset.filter(rating='warm').count(),
                'cold': queryset.filter(rating='cold').count(),
            }
        }
        return Response(stats)


class OpportunityViewSet(viewsets.ModelViewSet):
    """ViewSet for managing opportunities"""
    queryset = Opportunity.objects.all()
    permission_classes = [AllowOptionsAuthentication]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['stage', 'account', 'owner']
    search_fields = ['name', 'account__name']
    ordering_fields = ['name', 'amount', 'close_date', 'created_at']
    ordering = ['-created_at']

    def get_serializer_class(self):
        if self.action == 'list':
            return OpportunityListSerializer
        return OpportunitySerializer

    def get_queryset(self):
        queryset = Opportunity.objects.select_related('account')
        if not self.request.user.is_superuser:
            queryset = queryset.filter(owner=self.request.user)
        return queryset

    @action(detail=False, methods=['get'])
    def pipeline(self, request):
        """Get sales pipeline data"""
        queryset = self.get_queryset()
        pipeline = {}
        
        for stage_choice in Opportunity.STAGE_CHOICES:
            stage = stage_choice[0]
            stage_opportunities = queryset.filter(stage=stage)
            pipeline[stage] = {
                'count': stage_opportunities.count(),
                'total_value': stage_opportunities.aggregate(total=Sum('amount'))['total'] or 0,
                'weighted_value': sum(opp.weighted_value for opp in stage_opportunities),
            }
        
        return Response(pipeline)

    @action(detail=False, methods=['get'])
    def forecast(self, request):
        """Get sales forecast data"""
        queryset = self.get_queryset()
        current_month = timezone.now().replace(day=1)
        
        # Opportunities closing this month
        this_month = queryset.filter(
            close_date__gte=current_month,
            close_date__lt=current_month.replace(month=current_month.month + 1)
        )
        
        forecast = {
            'this_month': {
                'total_value': this_month.aggregate(total=Sum('amount'))['total'] or 0,
                'weighted_value': sum(opp.weighted_value for opp in this_month),
                'count': this_month.count(),
            },
            'by_stage': {}
        }
        
        for stage_choice in Opportunity.STAGE_CHOICES:
            stage = stage_choice[0]
            stage_opps = this_month.filter(stage=stage)
            forecast['by_stage'][stage] = {
                'count': stage_opps.count(),
                'total_value': stage_opps.aggregate(total=Sum('amount'))['total'] or 0,
            }
        
        return Response(forecast)


class TaskViewSet(viewsets.ModelViewSet):
    """ViewSet for managing tasks"""
    queryset = Task.objects.all()
    permission_classes = [AllowOptionsAuthentication]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['task_type', 'status', 'priority', 'assigned_to']
    search_fields = ['subject', 'description']
    ordering_fields = ['subject', 'due_date', 'created_at']
    ordering = ['due_date']

    def get_serializer_class(self):
        if self.action == 'list':
            return TaskListSerializer
        return TaskSerializer

    def get_queryset(self):
        queryset = Task.objects.select_related('assigned_to', 'account', 'lead', 'opportunity')
        if not self.request.user.is_superuser:
            queryset = queryset.filter(
                Q(assigned_to=self.request.user) | Q(created_by=self.request.user)
            )
        return queryset

    @action(detail=True, methods=['post'])
    def complete(self, request, pk=None):
        """Mark a task as completed"""
        task = self.get_object()
        task.status = 'completed'
        task.completed_date = timezone.now()
        task.save()
        
        serializer = self.get_serializer(task)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def my_tasks(self, request):
        """Get tasks assigned to the current user"""
        tasks = self.get_queryset().filter(assigned_to=request.user)
        
        # Further filter by status if provided
        status_filter = request.query_params.get('status')
        if status_filter:
            tasks = tasks.filter(status=status_filter)
        
        # Filter overdue tasks
        overdue = request.query_params.get('overdue')
        if overdue == 'true':
            tasks = tasks.filter(due_date__lt=timezone.now(), status__in=['not_started', 'in_progress'])
        
        serializer = TaskListSerializer(tasks, many=True)
        return Response(serializer.data)


class NoteViewSet(viewsets.ModelViewSet):
    """ViewSet for managing notes"""
    queryset = Note.objects.all()
    permission_classes = [AllowOptionsAuthentication]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['account', 'lead', 'opportunity', 'is_private']
    search_fields = ['title', 'content']
    ordering_fields = ['created_at', 'updated_at']
    ordering = ['-created_at']

    def get_queryset(self):
        queryset = Note.objects.select_related('created_by', 'account', 'lead', 'opportunity')
        if not self.request.user.is_superuser:
            # Show public notes and private notes created by the user
            queryset = queryset.filter(
                Q(is_private=False) | Q(created_by=self.request.user)
            )
        return queryset


class CampaignViewSet(viewsets.ModelViewSet):
    """ViewSet for managing campaigns"""
    queryset = Campaign.objects.all()
    permission_classes = [AllowOptionsAuthentication]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['campaign_type', 'status', 'owner']
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'start_date', 'end_date', 'created_at']
    ordering = ['-start_date']

    def get_serializer_class(self):
        if self.action == 'list':
            return CampaignListSerializer
        return CampaignSerializer

    def get_queryset(self):
        queryset = Campaign.objects.all()
        if not self.request.user.is_superuser:
            queryset = queryset.filter(owner=self.request.user)
        return queryset

    @action(detail=False, methods=['get'])
    def analytics(self, request):
        """Get campaign analytics"""
        queryset = self.get_queryset()
        
        analytics = {
            'total_campaigns': queryset.count(),
            'active_campaigns': queryset.filter(status='active').count(),
            'total_budget': queryset.aggregate(total=Sum('budget'))['total'] or 0,
            'total_cost': queryset.aggregate(total=Sum('actual_cost'))['total'] or 0,
            'total_responses': queryset.aggregate(total=Sum('actual_response'))['total'] or 0,
            'average_roi': queryset.aggregate(avg_roi=Avg('roi'))['avg_roi'] or 0,
            'by_type': {}
        }
        
        for campaign_type in Campaign.CAMPAIGN_TYPE_CHOICES:
            type_campaigns = queryset.filter(campaign_type=campaign_type[0])
            analytics['by_type'][campaign_type[0]] = {
                'count': type_campaigns.count(),
                'total_cost': type_campaigns.aggregate(total=Sum('actual_cost'))['total'] or 0,
                'total_responses': type_campaigns.aggregate(total=Sum('actual_response'))['total'] or 0,
            }
        
        return Response(analytics)