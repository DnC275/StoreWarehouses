import requests
import json
import logging
from django.db import models
from django.dispatch import receiver
from django.db.models import signals
from Warehouse import settings

logger = logging.getLogger(__name__)


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
    updated_by_store = models.BooleanField(default=False)


@receiver(signal=signals.post_save, sender=Order)
def send_changes_to_store(sender, instance, created, **kwargs):
    if instance.updated_by_store:
        return

    logger.info('Syncing with store')
    headers = {'Content-Type': 'application/json', 'Authorization': ' '.join(['WarehouseToken', settings.STORE_TOKEN])}
    payload = {'order_number': instance.order_number, 'status': instance.status}
    url = 'http://' + settings.STORE_HOST + ':' + settings.STORE_PORT
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
    if response.status_code != 200 and response.status_code != 201:
        logger.error(f"Syncing failed with message: {response.text}")
    else:
        logger.info('Syncing was successful')


@receiver(signal=signals.post_delete, sender=Order)
def delete_from_store(sender, instance, **kwargs):
    print(instance.updated_by_store)
    if instance.updated_by_store:
        return

    logger.info('Syncing with store')

    headers = {'Authorization': ' '.join(['WarehouseToken', settings.STORE_TOKEN])}
    url = 'http://' + settings.STORE_HOST + ':' + settings.STORE_PORT
    response = requests.delete(
        '/'.join([url, 'orders', str(instance.order_number)]) + '/',
        headers=headers
    )

    if response.status_code != 204:
        logger.error(f"Syncing failed with message: {response.text}")
    else:
        logger.info('Syncing was successful')
