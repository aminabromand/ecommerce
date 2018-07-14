from django.http import JsonResponse
from django.shortcuts import render, redirect

from apps.addresses.forms import AddressForm
from apps.addresses.models import Address
from apps.accounts.forms import LoginForm, GuestForm
from apps.accounts.models import GuestEmail
from apps.billing.models import BillingProfile
from apps.orders.models import Order
from products.models import Product
from .models import Cart

# Create your views here.

def cart_detail_api_view(request):
	cart_obj, new_obj = Cart.objects.new_or_get(request)
	products = [{"name": x.name, "price": x.price} for x in cart_obj.products.all()]
	# products_list = []
	# for x in cart_obj.producst.all():
	# 	products_list.append(
	# 			{"name": x.name, "price": x.price}
	# 		)
	cart_data = {"products": products,
				 "subtotal": cart_obj.subtotal,
				 "total": cart_obj.total}
	return JsonResponse(cart_data)

def cart_home(request):
	cart_obj, new_obj = Cart.objects.new_or_get(request)

	return render(request, 'carts/home.html', {'cart': cart_obj})


def cart_update(request):
	print(request.POST)
	product_id = request.POST.get('product_id')
	if product_id is not None:
		try:
			product_obj = Product.objects.get(id=product_id)
		except Product.DoesNotExist:
			print('Show message to user, product is gone?')
			return redirect('cart:home')
		cart_obj, new_obj = Cart.objects.new_or_get(request)
		if product_obj in cart_obj.products.all():
			cart_obj.products.remove(product_obj)
			added = False
		else:
			cart_obj.products.add(product_obj) # cart_obj.products.add(product_id)
			added = True
		request.session['cart_items'] = cart_obj.products.count()
	# return redirect(product_obj.get_absolute_url())
		if request.is_ajax(): # Asynchronous JavaScript And XML / JSON
			print('Ajax request')
			json_data = {
				"added": added,
				"removed": not added,
				"cart_item_count": cart_obj.products.count(),
			}
			return JsonResponse(json_data)
	return redirect('cart:home')


def checkout_home(request):
	cart_obj, cart_created = Cart.objects.new_or_get(request)
	order_obj = None
	if cart_created or cart_obj.products.count() == 0:
		return redirect('cart:home')
	login_form = LoginForm()
	guest_form = GuestForm()
	address_form = AddressForm()
	billing_address_id = request.session.get('billing_address_id', None)
	shipping_address_id = request.session.get('shipping_address_id', None)
	# billing_address_form = AddressForm()

	billing_profile, billing_profile_created = BillingProfile.objects.new_or_get(request)
	# billing_profile = None
	# user = request.user
	# guest_email_id = request.session.get('guest_email_id')
	# if user.is_authenticated():
	# 	'''logged in user checkout; remember payment stuff'''
	# 	if user.email:
	# 		billing_profile, billing_profile_created = BillingProfile.objects.get_or_create(
	# 														user=user, email=user.email)
	# 	else:
	# 		raise Exception('user has no email!')
	# elif guest_email_id is not None:
	# 	'''guest user checkout; auto reload payment stuff'''
	# 	guest_email_obj = GuestEmail.objects.get(id=guest_email_id)
	# 	billing_profile, billing_profile_created = BillingProfile.objects.get_or_create(
	# 														email=guest_email_obj.email)
	# else:
	# 	pass
	# 	# raise Exception('no user and no email provided!')

	address_qs = None
	if billing_profile is not None:
		if request.user.is_authenticated():
			address_qs = Address.objects.filter(billing_profile=billing_profile)
		# shipping_address_qs 	= address_qs.filter(address_type='shipping')
		# billing_address_qs 		= address_qs.filter(address_type='billing')
		order_obj, order_obj_created = Order.objects.new_or_get(billing_profile, cart_obj)
		# order_qs = Order.objects.filter(billing_profile=billing_profile, cart=cart_obj, active=True)
		# if order_qs.count() == 1:
		# 	order_obj = order_qs.first()
		# else:
		# 	order_obj = Order.objects.create(billing_profile=billing_profile, cart=cart_obj)
		if shipping_address_id:
			order_obj.shipping_address = Address.objects.get(id=shipping_address_id)
			del request.session['shipping_address_id']
		if billing_address_id:
			order_obj.billing_address = Address.objects.get(id=billing_address_id)
			del request.session['billing_address_id']
		if billing_address_id or shipping_address_id:
			order_obj.save()

	if request.method == 'POST':
		# check that order is done
		is_done = order_obj.check_done()
		if is_done:
			order_obj.mark_paid()
			request.session['cart_items'] = 0
			del request.session['cart_id']
			return redirect('cart:success')

	context = {
		'object': order_obj,
		'billing_profile': billing_profile,
		'login_form': login_form,
		'guest_form': guest_form,
		'address_form': address_form,
		'address_qs': address_qs,
		# 'billing_address_form': billing_address_form,
	}
	return render(request, 'carts/checkout.html', context)


def checkout_done_view(request):
	return render(request, 'carts/checkout-done.html', {})
