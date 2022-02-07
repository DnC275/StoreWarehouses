import requests
import json
import logging
from django.db import models
from django.dispatch import receiver
from django.db.models import signals
from django.contrib.auth.models import User as BaseUser
from rest_framework.authtoken.models import Token

logger = logging.getLogger(__name__)


@receiver(signal=signals.post_save, sender=BaseUser)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)


class Warehouse(models.Model):
    number = models.IntegerField(primary_key=True)
    token = models.CharField(max_length=128)
    host = models.CharField(max_length=32, default='localhost')
    port = models.IntegerField(default=8001)

    class Meta:
        unique_together = ('host', 'port',)

    @property
    def is_authenticated(self):
        return True

    @property
    def is_anonymous(self):
        return False


class Order(models.Model):
    IN_PROGRESS = 'IP'
    STORED = 'ST'
    SEND = 'SE'

    STATUS_CHOICES = [
        (IN_PROGRESS, 'In progress'),
        (STORED, 'Stored'),
        (SEND, 'Send')
    ]

    order_number = models.IntegerField(primary_key=True)
    status = models.CharField(max_length=32, choices=STATUS_CHOICES, blank=True)
    warehouse = models.ForeignKey(Warehouse, on_delete=models.CASCADE, db_index=True, blank=False)
    updated_by_warehouse = models.BooleanField(default=False)


@receiver(signal=signals.post_save, sender=Order)
def send_changes_to_warehouse(sender, instance, created, **kwargs):
    if instance.updated_by_warehouse:
        return

    logger.info(f'Syncing with warehouse number {instance.warehouse.number}')

    headers = {'Content-Type': 'application/json', 'Authorization': ' '.join(['StoreToken', instance.warehouse.token])}
    payload = {'order_number': instance.order_number, 'status': instance.status}
    url = 'http://' + instance.warehouse.host + ':' + str(instance.warehouse.port)

    try:
        if created:
            response = requests.post(
                '/'.join([url, 'orders']) + '/',
                data=json.dumps(payload),
                headers=headers,
            )
        else:
            response = requests.patch(
                '/'.join([url, 'orders', str(instance.order_number)]) + '/',
                data=json.dumps(payload),
                headers=headers
            )
    except requests.exceptions.ConnectionError:
        logger.error(f'Warehouse number {instance.warehouse.number} unavailable. Syncing failed.')
        return

    if response.status_code != 200 and response.status_code != 201:
        logger.error(f"Syncing failed with message: {response.text}")
    else:
        logger.info('Syncing was successful')


@receiver(signal=signals.post_delete, sender=Order)
def delete_from_warehouse(sender, instance, **kwargs):
    if instance.updated_by_warehouse:
        return

    logger.info(f'Syncing with warehouse number {instance.warehouse.number}')

    headers = {'Authorization': ' '.join(['StoreToken', instance.warehouse.token])}
    url = 'http://' + instance.warehouse.host + ':' + str(instance.warehouse.port)

    try:
        response = requests.delete(
            '/'.join([url, 'orders', str(instance.order_number)]) + '/',
            headers=headers
        )
    except requests.exceptions.ConnectionError:
        logger.error(f'Warehouse number {instance.warehouse.number} unavailable. Syncing failed.')
        return

    if response.status_code != 204:
        logger.error(f"Syncing failed with message: {response.text}")
    else:
        logger.info('Syncing was successful')

