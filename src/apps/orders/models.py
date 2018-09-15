import math
from django.db import models
from django.db.models import Count, Sum, Avg
from django.db.models.signals import pre_save, post_save
from django.contrib.auth import get_user_model
from django.core.urlresolvers import reverse

from apps.addresses.models import Address
from apps.billing.models import BillingProfile
from apps.carts.models import Cart
from ecommerce.utils import unique_order_id_generator
from products.models import Product


ORDER_STATUS_CHOICES = (
	('created', 'Created'),
	('paid', 'Paid'),
	('shipped', 'Shipped'),
	('refunded', 'Refunded'),
)

User = get_user_model()

# Create your models here.

class OrderManagerQuerySet(models.query.QuerySet):

	def recent(self):
		return self.order_by('-update', '-timestamp')

	def totals_data(self):
		return self.aggregate(Sum('total'), Avg('total'))

	def cart_data(self):
		return self.aggregate(
							Sum('cart__products__price'),
							Avg('cart__products__price'),
							Count('cart__products'))

	def by_status(self, status='shipped'):
		return self.filter(status=status)

	def not_refunded(self):
		return self.exclude(status='refunded')

	def by_request(self, request):
		billing_profile, _ = BillingProfile.objects.new_or_get(request)
		return self.filter(billing_profile=billing_profile)

	def not_created(self):
		return self.exclude(status='created')


class OrderManager(models.Manager):
	def get_queryset(self):
		return OrderManagerQuerySet(self.model, using=self._db)

	def by_request(self, request):
		return self.get_queryset().by_request(request)

	def new_or_get(self, billing_profile, cart_obj):
		created = False
		qs = self.get_queryset().filter(billing_profile=billing_profile,
										cart=cart_obj,
										active=True,
										status='created')
		if qs.count() == 1:
			obj = qs.first()
		else:
			obj = self.model.objects.create(billing_profile=billing_profile, cart=cart_obj)
			created = True
		return obj, created


# Random, Unique
class Order(models.Model):
	# pk / id is in there anyway
	order_id 			= models.CharField(max_length=120, blank=True) # business order id
	billing_profile 	= models.ForeignKey(BillingProfile, null=True, blank=True)
	shipping_address 	= models.ForeignKey(Address, related_name='shipping_address', null=True, blank=True)
	billing_address 	= models.ForeignKey(Address, related_name='billing_address', null=True, blank=True)
	cart 				= models.ForeignKey(Cart)
	status 				= models.CharField(max_length=120, default='created', choices=ORDER_STATUS_CHOICES)
	shipping_total 		= models.DecimalField(default=5.99, max_digits=100, decimal_places=2)
	total 				= models.DecimalField(default=0.00, max_digits=100, decimal_places=2)
	active 				= models.BooleanField(default=True)

	timestamp 			= models.DateTimeField(auto_now_add=True)
	update 				= models.DateTimeField(auto_now=True)

	def __str__(self):
		return self.order_id

	objects = OrderManager()

	class Meta:
		ordering = ['-timestamp', '-update']

	def get_absolute_url(self):
		return reverse('orders:detail', kwargs={'order_id': self.order_id})

	def get_status(self):
		if self.status == 'refunded':
			return 'Refunded order'
		if self.status == 'shipped':
			return 'Shipped'
		return 'Shipping soon'

	# generate order_id
	# generate order total

	def update_total(self):
		cart_total = self.cart.total
		shipping_total = self.shipping_total
		new_total = math.fsum([cart_total, shipping_total])
		# new_total = Decimal(math.fsum([cart_total, shipping_total]))
		# print(Decimal(new_total))
		formatted_total = format(new_total, '.2f')
		self.total = formatted_total
		self.save()
		return new_total

	def check_done(self):
		shipping_address_required = not self.cart.is_digital
		shipping_done = False
		if not shipping_address_required or self.shipping_address:
			shipping_done = True

		print(shipping_done)
		billing_profile = self.billing_profile
		billing_address = self.billing_address
		total = self.total
		if billing_profile and shipping_done and billing_address and total > 0:
			return True
		return False

	def update_purchases(self):
		for p in self.cart.products.all():
			obj, created = ProductPurchase.objects.get_or_create(
					order_id=self.order_id,
					product=p,
					billing_profile=self.billing_profile,
				)
		return ProductPurchase.objects.filter(order_id=self.order_id).count()

	def mark_paid(self):
		if self.status != 'paid':
			if self.check_done:
				self.status = 'paid'
				self.save()
				self.update_purchases()
		return self.status


def pre_save_create_order_id(sender, instance, *args, **kwargs):
	if not instance.order_id:
		instance.order_id = unique_order_id_generator(instance)
	qs = Order.objects.filter(cart=instance.cart).exclude(billing_profile=instance.billing_profile)
	if qs.exists():
		qs.update(active=False)

pre_save.connect(pre_save_create_order_id, sender=Order)


def post_save_cart_total(sender, instance, created, *args, **kwargs):
	if not created:
		cart_obj = instance
		cart_total = cart_obj.total
		cart_id = cart_obj.id
		qs = Order.objects.filter(cart__id=cart_id)
		if qs.count() == 1:
			order_obj = qs.first()
			order_obj.update_total()

post_save.connect(post_save_cart_total, sender=Cart)


def post_save_order(sender, instance, created, *args, **kwargs):
	print('running')
	if created:
		print('updating... first')
		instance.update_total()

post_save.connect(post_save_order, sender=Order)


class ProductPurchaseQuerySet(models.query.QuerySet):
	def active(self):
		return self.filter(refunded=False)

	def digital(self):
		return self.filter(product__is_digital=True)

	def by_request(self, request):
		billing_profile, _ = BillingProfile.objects.new_or_get(request)
		return self.filter(billing_profile=billing_profile)


class ProductPurchaseManager(models.Manager):
	def get_queryset(self):
		return ProductPurchaseQuerySet(self.model, using=self._db)

	def all(self):
		return self.get_queryset().active()

	def digital(self):
		return self.all().digital()

	def by_request(self, request):
		return self.get_queryset().by_request(request)

	def products_by_id(self, request):
		qs = self.by_request(request).digital()
		ids_ = [_.product.id for _ in qs]
		return ids_

	def products_by_request(self, request):
		ids_ = self.products_by_id(request)
		products_qs = Product.objects.filter(id__in=ids_).distinct()
		return products_qs


class ProductPurchase(models.Model):
	order_id 			= models.CharField(max_length=120)
	billing_profile 	= models.ForeignKey(BillingProfile) # billingprofile.productpurchase_set.all()
	product 			= models.ForeignKey(Product) # product.productpurchase_set.count()
	refunded 			= models.BooleanField(default=False)
	updated 			= models.DateTimeField(auto_now=True)
	timestamp 			= models.DateTimeField(auto_now_add=True)

	objects = ProductPurchaseManager()

	def __str__(self):
		return self.product.title
