from django.urls import re_path, include
from rest_framework import routers
from rest_framework.documentation import include_docs_urls

from appointment import views as views_apppointment
from .views import (
    AccountViewSet, LeadViewSet, OpportunityViewSet,
    TaskViewSet, NoteViewSet, CampaignViewSet
)

router = routers.SimpleRouter()

# Appointment endpoints
router.register(r'appointment', views_apppointment.AppointmentViewSet)
router.register(r'appointmentnotifications',
                views_apppointment.AppointmentNotificationViewSet)

# CRM endpoints
router.register(r'accounts', AccountViewSet)
router.register(r'leads', LeadViewSet)
router.register(r'opportunities', OpportunityViewSet)
router.register(r'tasks', TaskViewSet)
router.register(r'notes', NoteViewSet)
router.register(r'campaigns', CampaignViewSet)

urlpatterns = [
    re_path(r'^docs/', include_docs_urls(title='CRM Service')),
    re_path(r'^api/', include('contact.urls')),
]

urlpatterns += router.urls
