from django.contrib import admin
from .models import Order


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    # exclude = ('updated_by_store', )

    def save_model(self, request, obj, form, change):
        obj.updated_by_store = False
        obj.save()

    def delete_model(self, request, obj):
        obj.updated_by_store = False
        obj.delete()
