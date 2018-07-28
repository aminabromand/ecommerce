import stripe

from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect
from django.utils.http import is_safe_url

from .models import BillingProfile, Card

# Create your views here.


stripe.api_key = 'sk_test_o4XI58CtPtGfa8SfvrU2tr04'
STRIPE_PUB_KEY = 'pk_test_pBdBgd2GUxEfz7tmxuewrTgZ'


def payment_method_view(request):
	# if request.user.is_authenticated():
	# 	billing_profile = request.user.billingprofile
	# 	my_customer_id = billing_profile.customer_id
	billing_profile, billing_profile_created = BillingProfile.objects.new_or_get(request)
	if not billing_profile:
		return redirect('/cart')
	next_url = None
	next_ = request.GET.get('next')
	if is_safe_url(next_, request.get_host()):
		next_url = next_
	context = {
			'publish_key': STRIPE_PUB_KEY,
			'next_url': next_url,
		}
	return render(request, 'billing/payment-method.html', context)


def payment_method_createview(request):
	if request.method == "POST" and request.is_ajax():
		billing_profile, billing_profile_created = BillingProfile.objects.new_or_get(request)
		if not billing_profile:
			return HttpResponse({'message': 'Cannot find this user'}, status_code=401)
		token = request.POST.get('token')
		if token is not None:
			customer = stripe.Customer.retrieve(billing_profile.customer_id)
			card_response = customer.sources.create(source=token)
			new_card_obj = Card.objects.add_new(billing_profile, card_response)
			print(new_card_obj) # start saving our cards too!
		return JsonResponse({'message': 'Success! Your card was added.'})
	return HttpResponse('error', status_code=401)
