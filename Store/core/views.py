import jwt
from Store import settings
from rest_framework import status
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from .models import Order, Warehouse
from .serializers import OrderSerializer, WarehouseSerializer
from rest_framework.response import Response


class OrderViewSet(ModelViewSet):
    queryset = Order.objects.all()
    permission_classes = [IsAuthenticated]
    serializer_class = OrderSerializer

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if 'updated_by_warehouse' in request.data:
            instance.updated_by_warehouse = request.data['updated_by_warehouse']
        else:
            instance.updated_by_warehouse = False
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)


class WarehouseViewSet(ModelViewSet):
    queryset = Warehouse.objects.all()
    permission_classes = [IsAdminUser]
    serializer_class = WarehouseSerializer

    def create(self, request, *args, **kwargs):
        print(request.user)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.data
        token = jwt.encode({'number': data['number']}, settings.SECRET_KEY, algorithm='HS256')
        Warehouse.objects.create(number=data['number'], token=token, host=data['host'], port=data['port'])
        response = {'token': token}
        return Response(response)
