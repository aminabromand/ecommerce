from django.db import models
from django.db.models.signals import pre_save

from ecommerce.utils import unique_order_id_generator
from apps.carts.models import Cart


ORDER_STATUS_CHOICES = (
	('created', 'Created'),
	('paid', 'Paid'),
	('shipped', 'Shipped'),
	('refunded', 'Refunded'),
)

# Create your models here.

# Random, Unique
class Order(models.Model):
	# pk / id is in there anyway
	order_id = models.CharField(max_length=120, blank=True) # business order id
	# billing_profile = ?
	# shipping_adress
	# billing_address
	cart = models.ForeignKey(Cart)
	status = models.CharField(max_length=120, default='created', choices=ORDER_STATUS_CHOICES)
	shipping_total = models.DecimalField(default=5.99, max_digits=100, decimal_places=2)
	total = models.DecimalField(default=0.00, max_digits=100, decimal_places=2) 

	def __str__(self):
		return self.order_id

	# generate order_id
	# generate order total


def pre_save_create_order_id(sender, instance, *args, **kwargs):
	if not instance.order_id:
		instance.order_id = unique_order_id_generator(instance)


pre_save.connect(pre_save_create_order_id, sender=Order)
