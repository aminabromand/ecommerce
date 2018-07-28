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

	def charge(self, order_obj, card=None):
		return Charge.objects.do(self, order_obj, card)


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
	def add_new(self, billing_profile, token):
		if token:
			customer = stripe.Customer.retrieve(billing_profile.customer_id)
			card_response = customer.sources.create(source=token)
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


class ChargeManager(models.Manager):
	def do(self, billing_profile, order_obj, card=None): # Charge.objects.do()
		card_obj = card
		if card_obj is None:
			cards = billing_profile.card_set.filter(default=True) # reverse relationship of card_obj.billing_profile
			if cards.exists():
				card_obj = cards.first()
		if card_obj is None:
			return False, "No cards available"

		c = stripe.Charge.create(
					amount = int(order_obj.total * 100), # 39.19 --> 3919
					currency = "eur",
					customer = billing_profile.customer_id,
					source = card_obj.stripe_id,
					metadata = {
							'order_id': order_obj.order_id,
						}
				)
		if c.outcome is None:
			new_charge_obj = self.model(
						billing_profile = billing_profile,
						stripe_id = c.id,
						paid = c.paid,
						refunded = c.refunded,
						outcome = c.outcome,
					)
		else:
			new_charge_obj = self.model(
						billing_profile = billing_profile,
						stripe_id = c.id,
						paid = c.paid,
						refunded = c.refunded,
						outcome = c.outcome,
						outcome_type = c.outcome['type'],
						seller_message = c.outcome.get('seller_message'),
						risk_level = c.outcome.get('risk_level'),
					)
		new_charge_obj.save()
		return new_charge_obj.paid, new_charge_obj.seller_message

class Charge(models.Model):
	billing_profile 		= models.ForeignKey(BillingProfile)
	stripe_id				= models.CharField(max_length=120)
	paid					= models.BooleanField(default=False)
	refunded				= models.BooleanField(default=False)
	outcome					= models.TextField(null=True, blank=True)
	outcome_type			= models.CharField(max_length=120, null=True, blank=True)
	seller_message			= models.CharField(max_length=120, null=True, blank=True)
	risk_level				= models.CharField(max_length=120, null=True, blank=True)

	objects = ChargeManager()

	def __str__(self):
		return "{} {}".format(self.stripe_id, self.paid)
