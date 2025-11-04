from django.contrib import admin
from .models import Contact, StateRecord


@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    pass


@admin.register(StateRecord)
class StateRecordAdmin(admin.ModelAdmin):
    list_display = (
        'last_name',
        'first_name',
        'middle_name',
        'voter_id',
        'type',
        'original_state',
        'precinct'
    )
    search_fields = list_display
