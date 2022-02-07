from rest_framework.serializers import ModelSerializer
from .models import Order, Warehouse


class OrderSerializer(ModelSerializer):
    class Meta:
        model = Order
        fields = '__all__'

    def is_valid(self, raise_exception=False):
        if 'updated_by_warehouse' not in self.initial_data:
            self.initial_data['updated_by_warehouse'] = False
        return super(OrderSerializer, self).is_valid()


class WarehouseSerializer(ModelSerializer):
    class Meta:
        model = Warehouse
        exclude = ['token']
