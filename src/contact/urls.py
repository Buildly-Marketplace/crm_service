from rest_framework import routers

from contact.views import StateRecordViewSet, ContactViewSet

# add urls
router = routers.SimpleRouter()

router.register(r'state-records', StateRecordViewSet)
router.register(r'contact', ContactViewSet)

urlpatterns = router.urls
