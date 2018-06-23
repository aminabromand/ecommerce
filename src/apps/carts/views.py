from django.shortcuts import render

# Create your views here.

def cart_home(request):
	# print(request.session) # session object
	# print(dir(request.session)) # class methods and stuff
	# request.session.set_expiry(300)
	# key = request.session.session_key
	# print(key)
	#
	request.session['first_name'] = 'Justin'
	request.session['user'] = request.user.username
	return render(request, 'carts/home.html', {})
