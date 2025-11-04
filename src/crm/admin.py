from django.contrib import admin
from .models import Account, Lead, Opportunity, Task, Note, Campaign


@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    list_display = ['name', 'account_type', 'industry', 'owner', 'created_at']
    list_filter = ['account_type', 'industry', 'created_at', 'owner']
    search_fields = ['name', 'email', 'phone']
    readonly_fields = ['account_uuid', 'created_at', 'updated_at']
    fieldsets = (
        (None, {
            'fields': ('name', 'account_type', 'industry', 'owner')
        }),
        ('Contact Information', {
            'fields': ('phone', 'email', 'website')
        }),
        ('Address Information', {
            'fields': ('billing_address', 'shipping_address')
        }),
        ('Company Details', {
            'fields': ('annual_revenue', 'employee_count', 'description')
        }),
        ('System Information', {
            'fields': ('account_uuid', 'created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )


@admin.register(Lead)
class LeadAdmin(admin.ModelAdmin):
    list_display = ['first_name', 'last_name', 'company', 'email', 'status', 'rating', 'owner', 'created_at']
    list_filter = ['status', 'rating', 'source', 'created_at', 'owner']
    search_fields = ['first_name', 'last_name', 'company', 'email', 'phone']
    readonly_fields = ['lead_uuid', 'created_at', 'updated_at']
    fieldsets = (
        (None, {
            'fields': ('first_name', 'last_name', 'title', 'company')
        }),
        ('Contact Information', {
            'fields': ('email', 'phone', 'website', 'address')
        }),
        ('Lead Details', {
            'fields': ('status', 'source', 'rating', 'owner')
        }),
        ('Description', {
            'fields': ('description',)
        }),
        ('Conversion', {
            'fields': ('converted_account',)
        }),
        ('System Information', {
            'fields': ('lead_uuid', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )


@admin.register(Opportunity)
class OpportunityAdmin(admin.ModelAdmin):
    list_display = ['name', 'account', 'stage', 'amount', 'probability', 'close_date', 'owner']
    list_filter = ['stage', 'close_date', 'created_at', 'owner']
    search_fields = ['name', 'account__name']
    readonly_fields = ['opportunity_uuid', 'weighted_value', 'created_at', 'updated_at']
    fieldsets = (
        (None, {
            'fields': ('name', 'account', 'stage', 'owner')
        }),
        ('Financial Information', {
            'fields': ('amount', 'probability', 'weighted_value')
        }),
        ('Timeline', {
            'fields': ('close_date',)
        }),
        ('Details', {
            'fields': ('description', 'next_step')
        }),
        ('System Information', {
            'fields': ('opportunity_uuid', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ['subject', 'task_type', 'status', 'priority', 'due_date', 'assigned_to']
    list_filter = ['task_type', 'status', 'priority', 'due_date', 'assigned_to']
    search_fields = ['subject', 'description']
    readonly_fields = ['task_uuid', 'created_at', 'updated_at', 'completed_date']
    fieldsets = (
        (None, {
            'fields': ('subject', 'task_type', 'status', 'priority')
        }),
        ('Assignment', {
            'fields': ('assigned_to', 'created_by')
        }),
        ('Timeline', {
            'fields': ('due_date', 'completed_date')
        }),
        ('Related Objects', {
            'fields': ('account', 'lead', 'opportunity')
        }),
        ('Description', {
            'fields': ('description',)
        }),
        ('System Information', {
            'fields': ('task_uuid', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )


@admin.register(Note)
class NoteAdmin(admin.ModelAdmin):
    list_display = ['title', 'created_by', 'created_at', 'is_private']
    list_filter = ['is_private', 'created_at', 'created_by']
    search_fields = ['title', 'content']
    readonly_fields = ['note_uuid', 'created_at', 'updated_at']
    fieldsets = (
        (None, {
            'fields': ('title', 'content', 'is_private', 'created_by')
        }),
        ('Related Objects', {
            'fields': ('account', 'lead', 'opportunity')
        }),
        ('System Information', {
            'fields': ('note_uuid', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )


@admin.register(Campaign)
class CampaignAdmin(admin.ModelAdmin):
    list_display = ['name', 'campaign_type', 'status', 'start_date', 'end_date', 'owner']
    list_filter = ['campaign_type', 'status', 'start_date', 'owner']
    search_fields = ['name', 'description']
    readonly_fields = ['campaign_uuid', 'roi', 'created_at', 'updated_at']
    fieldsets = (
        (None, {
            'fields': ('name', 'campaign_type', 'status', 'owner')
        }),
        ('Timeline', {
            'fields': ('start_date', 'end_date')
        }),
        ('Budget & Results', {
            'fields': ('budget', 'actual_cost', 'expected_response', 'actual_response', 'roi')
        }),
        ('Description', {
            'fields': ('description',)
        }),
        ('System Information', {
            'fields': ('campaign_uuid', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )