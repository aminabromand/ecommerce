from django.shortcuts import render

from .models import Cart

# Create your views here.

def cart_create(user=None):
	cart_obj = Cart.objects.create(user=None)
	print('new Cart ID created')

def cart_home(request):
	cart_id = request.session.get('cart_id', None)
	# if cart_id is None: # isinstance(cart_id, int):
	# 	cart_obj = cart_create()
	# 	request.session['cart_id'] = cart_obj.id
	# else:
	qs = Cart.objects.filter(id=cart_id)
	if qs.exists() and qs.count() == 1:
		cart_obj = qs.first()
		print('Cart ID exists {0}'.format(cart_id))
	else:
		cart_obj = cart_create()
		request.session['cart_id'] = cart_obj.id
	return render(request, 'carts/home.html', {})
