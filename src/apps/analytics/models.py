from django.conf import settings
from django.db import models

from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

# Create your models here.

User = settings.AUTH_USER_MODEL


class ObjectViewed(models.Model):
	user 			= models.ForeignKey(User, blank=True, null=True) # User instance
	ip_address 		= models.CharField(max_length=220, blank=True, null=True) # even though there is an IP Field
	content_type 	= models.ForeignKey(ContentType) # User, Product, Order, Cart, Address
	object_id 		= models.PositiveIntegerField() # user id, product id, order id ...
	content_object 	= GenericForeignKey('content_type', 'object_id') # object instance
	timestamp 		= models.DateTimeField(auto_now_add=True)

	def __str__(self):
		return '%s viewed %s' %(self.content_object, self.timestamp)

	class Meta:
		ordering = ['-timestamp'] # most recent saved show up first
		verbose_name = 'Object viewed'
		verbose_name_plural = 'Objects viewed'

