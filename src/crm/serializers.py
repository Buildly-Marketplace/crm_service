from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Account, Lead, Opportunity, Task, Note, Campaign


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']


class AccountSerializer(serializers.ModelSerializer):
    owner = UserSerializer(read_only=True)
    created_by = UserSerializer(read_only=True)
    
    class Meta:
        model = Account
        fields = '__all__'
        read_only_fields = ['account_uuid', 'created_at', 'updated_at']

    def create(self, validated_data):
        validated_data['created_by'] = self.context['request'].user
        if 'owner' not in validated_data:
            validated_data['owner'] = self.context['request'].user
        return super().create(validated_data)


class AccountListSerializer(serializers.ModelSerializer):
    """Simplified serializer for list views"""
    owner = serializers.StringRelatedField()
    
    class Meta:
        model = Account
        fields = ['account_uuid', 'name', 'account_type', 'industry', 'phone', 'email', 'owner', 'created_at']


class LeadSerializer(serializers.ModelSerializer):
    owner = UserSerializer(read_only=True)
    converted_account = AccountListSerializer(read_only=True)
    
    class Meta:
        model = Lead
        fields = '__all__'
        read_only_fields = ['lead_uuid', 'created_at', 'updated_at']

    def create(self, validated_data):
        if 'owner' not in validated_data:
            validated_data['owner'] = self.context['request'].user
        return super().create(validated_data)


class LeadListSerializer(serializers.ModelSerializer):
    """Simplified serializer for list views"""
    owner = serializers.StringRelatedField()
    full_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Lead
        fields = ['lead_uuid', 'full_name', 'company', 'email', 'phone', 'status', 'rating', 'owner', 'created_at']
    
    def get_full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}"


class OpportunitySerializer(serializers.ModelSerializer):
    account = AccountListSerializer(read_only=True)
    account_id = serializers.PrimaryKeyRelatedField(
        queryset=Account.objects.all(),
        source='account',
        write_only=True
    )
    owner = UserSerializer(read_only=True)
    weighted_value = serializers.ReadOnlyField()
    
    class Meta:
        model = Opportunity
        fields = '__all__'
        read_only_fields = ['opportunity_uuid', 'created_at', 'updated_at']

    def create(self, validated_data):
        if 'owner' not in validated_data:
            validated_data['owner'] = self.context['request'].user
        return super().create(validated_data)


class OpportunityListSerializer(serializers.ModelSerializer):
    """Simplified serializer for list views"""
    account_name = serializers.CharField(source='account.name', read_only=True)
    owner = serializers.StringRelatedField()
    weighted_value = serializers.ReadOnlyField()
    
    class Meta:
        model = Opportunity
        fields = ['opportunity_uuid', 'name', 'account_name', 'stage', 'amount', 'probability', 'weighted_value', 'close_date', 'owner']


class TaskSerializer(serializers.ModelSerializer):
    assigned_to = UserSerializer(read_only=True)
    assigned_to_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        source='assigned_to',
        write_only=True,
        required=False
    )
    created_by = UserSerializer(read_only=True)
    account = AccountListSerializer(read_only=True)
    lead = LeadListSerializer(read_only=True)
    opportunity = OpportunityListSerializer(read_only=True)
    
    class Meta:
        model = Task
        fields = '__all__'
        read_only_fields = ['task_uuid', 'created_at', 'updated_at', 'completed_date']

    def create(self, validated_data):
        validated_data['created_by'] = self.context['request'].user
        if 'assigned_to' not in validated_data:
            validated_data['assigned_to'] = self.context['request'].user
        return super().create(validated_data)


class TaskListSerializer(serializers.ModelSerializer):
    """Simplified serializer for list views"""
    assigned_to = serializers.StringRelatedField()
    related_object = serializers.SerializerMethodField()
    
    class Meta:
        model = Task
        fields = ['task_uuid', 'subject', 'task_type', 'status', 'priority', 'due_date', 'assigned_to', 'related_object']
    
    def get_related_object(self, obj):
        if obj.account:
            return f"Account: {obj.account.name}"
        elif obj.lead:
            return f"Lead: {obj.lead.first_name} {obj.lead.last_name}"
        elif obj.opportunity:
            return f"Opportunity: {obj.opportunity.name}"
        return None


class NoteSerializer(serializers.ModelSerializer):
    created_by = UserSerializer(read_only=True)
    account = AccountListSerializer(read_only=True)
    lead = LeadListSerializer(read_only=True)
    opportunity = OpportunityListSerializer(read_only=True)
    
    class Meta:
        model = Note
        fields = '__all__'
        read_only_fields = ['note_uuid', 'created_at', 'updated_at']

    def create(self, validated_data):
        validated_data['created_by'] = self.context['request'].user
        return super().create(validated_data)

    def validate(self, data):
        """Ensure at least one related object is specified"""
        related_objects = [data.get('account'), data.get('lead'), data.get('opportunity')]
        if not any(related_objects):
            raise serializers.ValidationError("At least one related object (account, lead, or opportunity) must be specified.")
        return data


class CampaignSerializer(serializers.ModelSerializer):
    owner = UserSerializer(read_only=True)
    roi = serializers.ReadOnlyField()
    
    class Meta:
        model = Campaign
        fields = '__all__'
        read_only_fields = ['campaign_uuid', 'created_at', 'updated_at']

    def create(self, validated_data):
        if 'owner' not in validated_data:
            validated_data['owner'] = self.context['request'].user
        return super().create(validated_data)


class CampaignListSerializer(serializers.ModelSerializer):
    """Simplified serializer for list views"""
    owner = serializers.StringRelatedField()
    roi = serializers.ReadOnlyField()
    
    class Meta:
        model = Campaign
        fields = ['campaign_uuid', 'name', 'campaign_type', 'status', 'start_date', 'end_date', 'budget', 'actual_cost', 'roi', 'owner']