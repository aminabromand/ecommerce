from django.shortcuts import render, redirect

from products.models import Product
from .models import Cart

# Create your views here.

def cart_home(request):

	# Old Code
	# cart_id = request.session.get('cart_id', None)
	# qs = Cart.objects.filter(id=cart_id)
	# if qs.exists() and qs.count() == 1:
	# 	cart_obj = qs.first()
	# 	print('Cart ID exists {0}'.format(cart_id))
	# 	if request.user.is_authenticated() and cart_obj.user is None:
	# 		cart_obj.user = request.user
	# 		cart_obj.save()
	# else:
	# 	cart_obj = Cart.objects.new(user=request.user)
	# 	request.session['cart_id'] = cart_obj.id

	cart_obj, new_obj = Cart.objects.new_or_get(request)
	products = cart_obj.products.all()
	total = 0
	for x in products:
		total += x.price
	print(total)
	cart_obj.total = total
	cart_obj.save()
	return render(request, 'carts/home.html', {})


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
		else:
			cart_obj.products.add(product_obj) # cart_obj.products.add(product_id)
	# return redirect(product_obj.get_absolute_url())
	return redirect('cart:home')
