from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated, AllowAny
from .models import Order
from .serializers import OrderSerializer
from rest_framework.response import Response
from rest_framework import status


class OrderViewSet(ModelViewSet):
    queryset = Order.objects.all()
    permission_classes = [IsAuthenticated]
    serializer_class = OrderSerializer

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if 'updated_by_store' in request.data:
            instance.updated_by_store = request.data['updated_by_store']
        else:
            instance.updated_by_store = False
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)
