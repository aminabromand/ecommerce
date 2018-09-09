from decimal import Decimal
from django.conf import settings
from django.db import models
from django.db.models.signals import pre_save, post_save, m2m_changed

from products.models import Product


User = settings.AUTH_USER_MODEL

# Create your models here.

class CartManager(models.Manager):
	def new_or_get(self, request):
		cart_id = request.session.get('cart_id', None)
		qs = self.get_queryset().filter(id=cart_id)
		if qs.exists() and qs.count() == 1:
			new_obj = False
			cart_obj = qs.first()
			print('Cart ID exists {0}'.format(cart_id))
			if cart_obj.user is None and request.user is not None:
				if request.user.is_authenticated():
					cart_obj.user = request.user
					cart_obj.save()
		else:
			new_obj = True
			cart_obj = self.new(user=request.user)
			request.session['cart_id'] = cart_obj.id
		return cart_obj, new_obj

	def new(self, user=None):
		user_obj = None
		if user is not None:
			if user.is_authenticated():
				user_obj = user
		return self.model.objects.create(user=user_obj)

class Cart(models.Model):
	user = models.ForeignKey(User, null=True, blank=True)
	products = models.ManyToManyField(Product, blank=True)
	subtotal = models.DecimalField(default=0.00, max_digits=100, decimal_places=2)
	total = models.DecimalField(default=0.00, max_digits=100, decimal_places=2)
	updated = models.DateTimeField(auto_now=True)
	timestamp = models.DateTimeField(auto_now_add=True)

	objects = CartManager()

	def __str__(self):
		return str(self.id)

	@property
	def is_digital(self):
		qs = self.products.all() # every product
		new_qs = qs.filter(is_digital=False) # every product that is not digital
		if new_qs.exists():
			return False
		return True
	


def m2m_changed_cart_receiver(sender, instance, action, *args, **kwargs):
	# print('action')
	if action == 'post_add' or action == 'post_remove' or action == 'post_clear':
		# print(instance.products.all())
		# print(instance.total)
		products = instance.products.all()
		total = 0
		for x in products:
			total += x.price
		# print(total)
		if instance.subtotal != total:
			instance.subtotal = total
			instance.save()

m2m_changed.connect(m2m_changed_cart_receiver, sender=Cart.products.through)


def pre_save_cart_receiver(sender, instance, *args, **kwargs):
	if instance.subtotal > 0:
		instance.total = Decimal(instance.subtotal) * Decimal(1.19) # 19 % tax
	else:
		instance.total = 0.00

pre_save.connect(pre_save_cart_receiver, sender=Cart)
