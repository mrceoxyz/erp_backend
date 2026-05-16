from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from .models import Product, ProductAudit


@receiver(post_save, sender=Product)
def product_created(sender, instance, created, **kwargs):
    if created:
        ProductAudit.objects.create(
            product=instance,
            action='created',
            new_value=f'Price: {instance.price}, Stock: {instance.stock_quantity}',
        )


@receiver(pre_save, sender=Product)
def product_updated(sender, instance, **kwargs):
    if not instance.pk:
        return

    previous = Product.objects.get(pk=instance.pk)

    # Price change
    if previous.price != instance.price:
        ProductAudit.objects.create(
            product=instance,
            action='price_change',
            previous_value=str(previous.price),
            new_value=str(instance.price),
        )

    # Stock change
    if previous.stock_quantity != instance.stock_quantity:
        diff = instance.stock_quantity - previous.stock_quantity

        ProductAudit.objects.create(
            product=instance,
            action='stock_in' if diff > 0 else 'stock_out',
            quantity=abs(diff),
            previous_value=str(previous.stock_quantity),
            new_value=str(instance.stock_quantity),
        )
