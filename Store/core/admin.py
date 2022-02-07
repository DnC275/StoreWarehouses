import jwt
from .models import Order, Warehouse
from django.contrib import admin
from Store import settings


@admin.register(Warehouse)
class WarehouseAdmin(admin.ModelAdmin):
    fields = ('number', 'token', 'host', 'port')
    readonly_fields = ('token', )

    def save_model(self, request, obj, form, change):
        data = {
            'number': obj.number
        }
        obj.token = jwt.encode(data, settings.SECRET_KEY, algorithm='HS256')
        obj.save()


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    exclude = ('updated_by_warehouse', )

    def save_model(self, request, obj, form, change):
        obj.updated_by_warehouse = False
        obj.save()

    def delete_model(self, request, obj):
        obj.updated_by_warehouse = False
        obj.delete()
