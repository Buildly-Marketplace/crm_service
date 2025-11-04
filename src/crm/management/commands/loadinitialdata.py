from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from crm.models import Account, Lead, Opportunity, Task, Campaign
from contact.models import Contact
from datetime import datetime, timedelta
from django.utils import timezone


class Command(BaseCommand):
    help = 'Load initial data for CRM service'

    def handle(self, *args, **options):
        self.stdout.write('Loading initial data...')

        # Create sample users if they don't exist
        admin_user, created = User.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@example.com',
                'first_name': 'Admin',
                'last_name': 'User',
                'is_staff': True,
                'is_superuser': True
            }
        )
        if created:
            admin_user.set_password('admin')
            admin_user.save()
            self.stdout.write(f'Created admin user: {admin_user.username}')

        sales_user, created = User.objects.get_or_create(
            username='salesrep',
            defaults={
                'email': 'sales@example.com',
                'first_name': 'Sales',
                'last_name': 'Representative',
                'is_staff': True
            }
        )
        if created:
            sales_user.set_password('sales123')
            sales_user.save()
            self.stdout.write(f'Created sales user: {sales_user.username}')

        # Create sample accounts
        sample_accounts = [
            {
                'name': 'TechCorp Solutions',
                'account_type': 'customer',
                'industry': 'technology',
                'website': 'https://techcorp.com',
                'phone': '555-0101',
                'email': 'contact@techcorp.com',
                'annual_revenue': 5000000,
                'employee_count': 150,
                'description': 'Leading technology solutions provider',
                'owner': admin_user,
                'created_by': admin_user
            },
            {
                'name': 'HealthFirst Medical',
                'account_type': 'prospect',
                'industry': 'healthcare',
                'website': 'https://healthfirst.com',
                'phone': '555-0202',
                'email': 'info@healthfirst.com',
                'annual_revenue': 2500000,
                'employee_count': 75,
                'description': 'Regional healthcare provider',
                'owner': sales_user,
                'created_by': admin_user
            },
            {
                'name': 'EduLearn Institute',
                'account_type': 'partner',
                'industry': 'education',
                'website': 'https://edulearn.org',
                'phone': '555-0303',
                'email': 'partnership@edulearn.org',
                'annual_revenue': 1200000,
                'employee_count': 45,
                'description': 'Online education platform',
                'owner': admin_user,
                'created_by': admin_user
            }
        ]

        accounts = []
        for account_data in sample_accounts:
            account, created = Account.objects.get_or_create(
                name=account_data['name'],
                defaults=account_data
            )
            accounts.append(account)
            if created:
                self.stdout.write(f'Created account: {account.name}')

        # Create sample leads
        sample_leads = [
            {
                'first_name': 'John',
                'last_name': 'Smith',
                'company': 'StartupXYZ',
                'title': 'CEO',
                'email': 'john@startupxyz.com',
                'phone': '555-0401',
                'status': 'new',
                'source': 'website',
                'rating': 'hot',
                'description': 'Interested in our enterprise solution',
                'owner': sales_user
            },
            {
                'first_name': 'Jane',
                'last_name': 'Doe',
                'company': 'InnovateNow',
                'title': 'CTO',
                'email': 'jane@innovatenow.com',
                'phone': '555-0501',
                'status': 'contacted',
                'source': 'referral',
                'rating': 'warm',
                'description': 'Looking for consulting services',
                'owner': admin_user
            },
            {
                'first_name': 'Mike',
                'last_name': 'Johnson',
                'company': 'GrowthCo',
                'title': 'VP Sales',
                'email': 'mike@growthco.com',
                'phone': '555-0601',
                'status': 'qualified',
                'source': 'trade_show',
                'rating': 'hot',
                'description': 'Needs CRM solution for 200+ users',
                'owner': sales_user
            }
        ]

        for lead_data in sample_leads:
            lead, created = Lead.objects.get_or_create(
                email=lead_data['email'],
                defaults=lead_data
            )
            if created:
                self.stdout.write(f'Created lead: {lead.first_name} {lead.last_name}')

        # Create sample opportunities
        sample_opportunities = [
            {
                'name': 'TechCorp CRM Implementation',
                'account': accounts[0],
                'stage': 'proposal',
                'amount': 125000,
                'probability': 75,
                'close_date': timezone.now().date() + timedelta(days=30),
                'description': 'Full CRM implementation with custom integrations',
                'next_step': 'Schedule final presentation',
                'owner': admin_user
            },
            {
                'name': 'HealthFirst Consultation Project',
                'account': accounts[1],
                'stage': 'needs_analysis',
                'amount': 50000,
                'probability': 40,
                'close_date': timezone.now().date() + timedelta(days=45),
                'description': 'Healthcare workflow optimization consulting',
                'next_step': 'Conduct needs assessment meeting',
                'owner': sales_user
            },
            {
                'name': 'EduLearn Platform Integration',
                'account': accounts[2],
                'stage': 'negotiation',
                'amount': 75000,
                'probability': 90,
                'close_date': timezone.now().date() + timedelta(days=15),
                'description': 'Integration with existing learning management system',
                'next_step': 'Finalize contract terms',
                'owner': admin_user
            }
        ]

        opportunities = []
        for opp_data in sample_opportunities:
            opportunity, created = Opportunity.objects.get_or_create(
                name=opp_data['name'],
                defaults=opp_data
            )
            opportunities.append(opportunity)
            if created:
                self.stdout.write(f'Created opportunity: {opportunity.name}')

        # Create sample tasks
        sample_tasks = [
            {
                'subject': 'Call TechCorp about proposal',
                'task_type': 'call',
                'status': 'not_started',
                'priority': 'high',
                'due_date': timezone.now() + timedelta(days=1),
                'description': 'Follow up on the proposal submission',
                'account': accounts[0],
                'opportunity': opportunities[0],
                'assigned_to': admin_user,
                'created_by': admin_user
            },
            {
                'subject': 'Send demo invitation to HealthFirst',
                'task_type': 'email',
                'status': 'in_progress',
                'priority': 'medium',
                'due_date': timezone.now() + timedelta(days=2),
                'description': 'Schedule product demo for next week',
                'account': accounts[1],
                'assigned_to': sales_user,
                'created_by': sales_user
            },
            {
                'subject': 'Prepare contract for EduLearn',
                'task_type': 'other',
                'status': 'not_started',
                'priority': 'high',
                'due_date': timezone.now() + timedelta(days=3),
                'description': 'Draft final contract with negotiated terms',
                'account': accounts[2],
                'opportunity': opportunities[2],
                'assigned_to': admin_user,
                'created_by': admin_user
            }
        ]

        for task_data in sample_tasks:
            task, created = Task.objects.get_or_create(
                subject=task_data['subject'],
                defaults=task_data
            )
            if created:
                self.stdout.write(f'Created task: {task.subject}')

        # Create sample campaign
        sample_campaigns = [
            {
                'name': 'Q4 Email Marketing Campaign',
                'campaign_type': 'email',
                'status': 'active',
                'start_date': timezone.now().date() - timedelta(days=30),
                'end_date': timezone.now().date() + timedelta(days=30),
                'budget': 15000,
                'actual_cost': 8500,
                'expected_response': 500,
                'actual_response': 325,
                'description': 'Year-end promotion for enterprise solutions',
                'owner': admin_user
            },
            {
                'name': 'Healthcare Industry Webinar',
                'campaign_type': 'webinar',
                'status': 'completed',
                'start_date': timezone.now().date() - timedelta(days=60),
                'end_date': timezone.now().date() - timedelta(days=45),
                'budget': 5000,
                'actual_cost': 4200,
                'expected_response': 200,
                'actual_response': 180,
                'description': 'Educational webinar targeting healthcare professionals',
                'owner': sales_user
            }
        ]

        for campaign_data in sample_campaigns:
            campaign, created = Campaign.objects.get_or_create(
                name=campaign_data['name'],
                defaults=campaign_data
            )
            if created:
                self.stdout.write(f'Created campaign: {campaign.name}')

        self.stdout.write(
            self.style.SUCCESS('Successfully loaded initial CRM data!')
        )