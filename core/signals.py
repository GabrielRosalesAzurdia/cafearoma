from django.db.models.signals import post_save
from django.dispatch import receiver
from core.models import InventoryItem
from core.services.patterns import DjangoInventoryRepo

@receiver(post_save, sender=InventoryItem)
def check_min_stock(sender, instance: InventoryItem, **kwargs):
    repo = DjangoInventoryRepo()
    repo.ensure_min_stock(instance)
