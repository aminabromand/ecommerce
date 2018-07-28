from django.conf import settings
from django.db import models
from django.db.models.signals import post_save, pre_save

import stripe

stripe.api_key = 'sk_test_o4XI58CtPtGfa8SfvrU2tr04'

from apps.accounts.models import GuestEmail

User = settings.AUTH_USER_MODEL

# Create your models here.

class BillingProfileManager(models.Manager):
	def new_or_get(self, request):
		user = request.user
		guest_email_id = request.session.get('guest_email_id')
		created = False
		obj = None
		if user.is_authenticated():
			'''logged in user checkout; remember payment stuff'''
			if user.email:
				obj, created = self.model.objects.get_or_create(user=user, email=user.email)
			else:
				raise Exception('user has no email!')
		elif guest_email_id is not None:
			'''guest user checkout; auto reload payment stuff'''
			guest_email_obj = GuestEmail.objects.get(id=guest_email_id)
			obj, created = self.model.objects.get_or_create(email=guest_email_obj.email)
		else:
			pass
			# raise Exception('no user and no email provided!')
		return obj, created

# abc@blub.com -->> 100000 billing profiles
# user abc@blub.com -->> 1 blling profile (all others have to be invalid)
class BillingProfile(models.Model):
	user = models.OneToOneField(User, null=True, blank=True)
	email = models.EmailField()
	active = models.BooleanField(default=True)
	update = models.DateTimeField(auto_now=True)
	timestamp = models.DateTimeField(auto_now_add=True)
	customer_id = models.CharField(max_length=120, null=True, blank=True) # in Stripe or Braintree

	def __str__(self):
		return self.email

	objects = BillingProfileManager()

def billing_profile_creating_receiver(sender, instance, *args, **kwargs):
	if not instance.customer_id and instance.email:
		print('ACTUAL API REQUEST Send to stripe/braintree')
		customer = stripe.Customer.create(
				email = instance.email
			)
		print(customer)
		instance.customer_id = customer.id


pre_save.connect(billing_profile_creating_receiver, sender=BillingProfile)


def user_created_receiver(sender, instance, created, *args, **kwargs):
	if created and instance.email:
		BillingProfile.objects.get_or_create(user=instance, email=instance.email)

post_save.connect(user_created_receiver, sender=User)


class CardManager(models.Manager):
	def add_new(self, billing_profile, stripe_card_response):
		if str(stripe_card_response.object) == "card":
			new_card = self.model(
						billing_profile = billing_profile,
						stripe_id = stripe_card_response.id,
						brand = stripe_card_response.brand,
						country = stripe_card_response.country,
						exp_month = stripe_card_response.exp_month,
						exp_year = stripe_card_response.exp_year,
						last4 = stripe_card_response.last4)
			new_card.save()
			return new_card
		return None


class Card(models.Model):
	billing_profile 		= models.ForeignKey(BillingProfile)
	stripe_id 				= models.CharField(max_length=120)
	brand					= models.CharField(max_length=120, null=True, blank=True)
	country 				= models.CharField(max_length=20, null=True, blank=True)
	exp_month				= models.IntegerField()
	exp_year				= models.IntegerField()
	last4 					= models.CharField(max_length=4, null=True, blank=True)
	default					= models.BooleanField(default=True)

	objects = CardManager()

	def __str__(self):
		return "{} {}".format(self.brand, self.last4)




