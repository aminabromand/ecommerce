import stripe

from django.shortcuts import render

# Create your views here.


stripe.api_key = 'sk_test_o4XI58CtPtGfa8SfvrU2tr04'
STRIPE_PUB_KEY = 'pk_test_pBdBgd2GUxEfz7tmxuewrTgZ'


def payment_method_view(request):
	if request.method == "POST":
		print(request.POST)
	return render(request, 'billing/payment-method.html', {'publish_key': STRIPE_PUB_KEY})
