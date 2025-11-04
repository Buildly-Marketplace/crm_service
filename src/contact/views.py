from rest_framework import viewsets, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from rest_framework import permissions

from .models import Contact, StateRecord
from .permissions import ContactPermission  # ContactPermission
from .serializers import ContactSerializer, StateRecordSerializer
from .utils.state_record import StateRecordUtil


class ContactViewSet(viewsets.ModelViewSet):
    """
    User's contacts.
    """

    def list(self, request):
        # Use this or the ordering filter won't work
        queryset = self.filter_queryset(self.get_queryset())
        queryset = queryset.filter()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def perform_create(self, serializer):
        user_uuid = self.request.session.get('jwt_user_uuid')
        serializer.save(user_uuid=user_uuid)

    def update(self, request, *args, **kwargs):
        kwargs['partial'] = True
        return super(ContactViewSet, self).update(request, *args, **kwargs)

    ordering_fields = ('first_name',)
    filter_backends = (filters.OrderingFilter,)
    queryset = Contact.objects.all()
    serializer_class = ContactSerializer
    permission_classes = (ContactPermission,)


class StateRecordViewSet(viewsets.ModelViewSet):
    """
    User's contacts.
    """

    def get_queryset(self):
        return super(StateRecordViewSet, self).get_queryset()[:50]

    def perform_create(self, serializer):
        serializer.save()

    def update(self, request, *args, **kwargs):
        kwargs['partial'] = True
        return super(StateRecordViewSet, self).update(request, *args, **kwargs)

    @action(detail=False, methods=['POST'], url_path='import-records')
    def import_records(self, request):
        uploaded_file = request.FILES.get('file')

        # check if file is uploaded
        if not uploaded_file:
            return Response({"error": "No file uploaded"}, status=status.HTTP_400_BAD_REQUEST)

        # process file data
        state_record = StateRecordUtil()
        try:
            results = state_record.process_state_file(uploaded_file)
            return Response(results, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    ordering_fields = ('first_name',)
    filter_backends = (filters.OrderingFilter,)
    queryset = StateRecord.objects.all()
    serializer_class = StateRecordSerializer
    permission_classes = (permissions.IsAuthenticated,)
