from django.shortcuts import render

from .models import Cart

# Create your views here.

def cart_home(request):
	cart_obj = Cart.objects.new_or_get(request)
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
	return render(request, 'carts/home.html', {})
