import uuid
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Account(models.Model):
    """
    Represents a company or organization account in the CRM
    """
    ACCOUNT_TYPE_CHOICES = [
        ('prospect', 'Prospect'),
        ('customer', 'Customer'), 
        ('partner', 'Partner'),
        ('vendor', 'Vendor'),
        ('competitor', 'Competitor'),
    ]
    
    INDUSTRY_CHOICES = [
        ('technology', 'Technology'),
        ('healthcare', 'Healthcare'),
        ('finance', 'Finance'),
        ('education', 'Education'),
        ('manufacturing', 'Manufacturing'),
        ('retail', 'Retail'),
        ('real_estate', 'Real Estate'),
        ('consulting', 'Consulting'),
        ('other', 'Other'),
    ]

    account_uuid = models.UUIDField(unique=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, help_text='Account name')
    account_type = models.CharField(max_length=20, choices=ACCOUNT_TYPE_CHOICES, default='prospect')
    industry = models.CharField(max_length=20, choices=INDUSTRY_CHOICES, blank=True, null=True)
    website = models.URLField(blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    billing_address = models.TextField(blank=True, null=True)
    shipping_address = models.TextField(blank=True, null=True)
    annual_revenue = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True)
    employee_count = models.PositiveIntegerField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_accounts')
    owner = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='owned_accounts')

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.name


class Lead(models.Model):
    """
    Represents a sales lead in the CRM
    """
    STATUS_CHOICES = [
        ('new', 'New'),
        ('contacted', 'Contacted'),
        ('qualified', 'Qualified'),
        ('unqualified', 'Unqualified'),
        ('converted', 'Converted'),
        ('lost', 'Lost'),
    ]
    
    SOURCE_CHOICES = [
        ('website', 'Website'),
        ('referral', 'Referral'),
        ('social_media', 'Social Media'),
        ('email_campaign', 'Email Campaign'),
        ('trade_show', 'Trade Show'),
        ('cold_call', 'Cold Call'),
        ('advertisement', 'Advertisement'),
        ('other', 'Other'),
    ]

    lead_uuid = models.UUIDField(unique=True, default=uuid.uuid4, editable=False)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    company = models.CharField(max_length=255, blank=True, null=True)
    title = models.CharField(max_length=255, blank=True, null=True)
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True, null=True)
    website = models.URLField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new')
    source = models.CharField(max_length=20, choices=SOURCE_CHOICES, blank=True, null=True)
    rating = models.CharField(max_length=10, choices=[('hot', 'Hot'), ('warm', 'Warm'), ('cold', 'Cold')], blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    converted_account = models.ForeignKey(Account, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    owner = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='owned_leads')

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.company}"


class Opportunity(models.Model):
    """
    Represents a sales opportunity in the CRM
    """
    STAGE_CHOICES = [
        ('prospecting', 'Prospecting'),
        ('qualification', 'Qualification'),
        ('needs_analysis', 'Needs Analysis'),
        ('value_proposition', 'Value Proposition'),
        ('proposal', 'Proposal'),
        ('negotiation', 'Negotiation'),
        ('closed_won', 'Closed Won'),
        ('closed_lost', 'Closed Lost'),
    ]

    opportunity_uuid = models.UUIDField(unique=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    account = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='opportunities')
    stage = models.CharField(max_length=20, choices=STAGE_CHOICES, default='prospecting')
    amount = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True)
    probability = models.PositiveIntegerField(default=0, help_text='Probability percentage (0-100)')
    close_date = models.DateField()
    description = models.TextField(blank=True, null=True)
    next_step = models.CharField(max_length=500, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    owner = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='owned_opportunities')

    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = 'Opportunities'

    def __str__(self):
        return f"{self.name} - {self.account.name}"

    @property
    def weighted_value(self):
        """Calculate weighted value based on amount and probability"""
        from decimal import Decimal
        if self.amount and self.probability:
            return self.amount * (Decimal(str(self.probability)) / Decimal('100'))
        return Decimal('0')


class Task(models.Model):
    """
    Represents a task or activity in the CRM
    """
    TASK_TYPE_CHOICES = [
        ('call', 'Call'),
        ('email', 'Email'),
        ('meeting', 'Meeting'),
        ('follow_up', 'Follow Up'),
        ('demo', 'Demo'),
        ('proposal', 'Proposal'),
        ('other', 'Other'),
    ]
    
    STATUS_CHOICES = [
        ('not_started', 'Not Started'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('deferred', 'Deferred'),
    ]

    task_uuid = models.UUIDField(unique=True, default=uuid.uuid4, editable=False)
    subject = models.CharField(max_length=255)
    task_type = models.CharField(max_length=20, choices=TASK_TYPE_CHOICES, default='call')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='not_started')
    priority = models.CharField(max_length=10, choices=[('high', 'High'), ('medium', 'Medium'), ('low', 'Low')], default='medium')
    due_date = models.DateTimeField()
    completed_date = models.DateTimeField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    
    # Related objects
    account = models.ForeignKey(Account, on_delete=models.CASCADE, null=True, blank=True, related_name='tasks')
    lead = models.ForeignKey(Lead, on_delete=models.CASCADE, null=True, blank=True, related_name='tasks')
    opportunity = models.ForeignKey(Opportunity, on_delete=models.CASCADE, null=True, blank=True, related_name='tasks')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='assigned_tasks')
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='created_tasks')

    class Meta:
        ordering = ['due_date']

    def __str__(self):
        return f"{self.subject} - {self.due_date.strftime('%Y-%m-%d')}"

    def save(self, *args, **kwargs):
        if self.status == 'completed' and not self.completed_date:
            self.completed_date = timezone.now()
        super().save(*args, **kwargs)


class Note(models.Model):
    """
    Represents notes/comments that can be attached to various CRM objects
    """
    note_uuid = models.UUIDField(unique=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255, blank=True, null=True)
    content = models.TextField()
    is_private = models.BooleanField(default=False, help_text='Only visible to the creator')
    
    # Related objects - at least one must be set
    account = models.ForeignKey(Account, on_delete=models.CASCADE, null=True, blank=True, related_name='notes')
    lead = models.ForeignKey(Lead, on_delete=models.CASCADE, null=True, blank=True, related_name='notes')
    opportunity = models.ForeignKey(Opportunity, on_delete=models.CASCADE, null=True, blank=True, related_name='notes')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_notes')

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Note by {self.created_by.username} - {self.created_at.strftime('%Y-%m-%d %H:%M')}"


class Campaign(models.Model):
    """
    Represents marketing campaigns in the CRM
    """
    CAMPAIGN_TYPE_CHOICES = [
        ('email', 'Email'),
        ('social_media', 'Social Media'),
        ('webinar', 'Webinar'),
        ('trade_show', 'Trade Show'),
        ('advertisement', 'Advertisement'),
        ('direct_mail', 'Direct Mail'),
        ('other', 'Other'),
    ]
    
    STATUS_CHOICES = [
        ('planning', 'Planning'),
        ('active', 'Active'),
        ('completed', 'Completed'),
        ('aborted', 'Aborted'),
    ]

    campaign_uuid = models.UUIDField(unique=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    campaign_type = models.CharField(max_length=20, choices=CAMPAIGN_TYPE_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='planning')
    start_date = models.DateField()
    end_date = models.DateField()
    budget = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True)
    actual_cost = models.DecimalField(max_digits=15, decimal_places=2, blank=True, null=True)
    expected_response = models.PositiveIntegerField(blank=True, null=True, help_text='Expected number of responses')
    actual_response = models.PositiveIntegerField(default=0, help_text='Actual number of responses')
    description = models.TextField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    owner = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='owned_campaigns')

    class Meta:
        ordering = ['-start_date']

    def __str__(self):
        return self.name

    @property
    def roi(self):
        """Calculate Return on Investment"""
        if self.actual_cost and self.actual_cost > 0:
            # This is a simplified ROI calculation - in practice, you'd need revenue data
            return ((self.actual_response - self.actual_cost) / self.actual_cost) * 100
        return 0