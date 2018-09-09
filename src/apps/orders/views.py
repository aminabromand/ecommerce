from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404, JsonResponse
from django.shortcuts import render
from django.views.generic import View, ListView, DetailView

from apps.billing.models import BillingProfile
from .models import Order, ProductPurchase

# Create your views here.

class OrderListView(LoginRequiredMixin, ListView):

	def get_queryset(self):
		return Order.objects.by_request(self.request).not_created()


class OrderDetailView(LoginRequiredMixin, DetailView):

	def get_object(self):
		# Django standard is this
		# return Order.objects.get(id=self.kwargs.get('id'))
		# or
		# return Order.objects.get(id=self.kwargs.get('slug'))
		qs = self.get_queryset().filter(order_id = self.kwargs.get('order_id'))
		if qs.count() == 1:
			return qs.first()
		raise Http404

	def get_queryset(self):
		return Order.objects.by_request(self.request).not_created()


class LibraryView(LoginRequiredMixin, ListView):
	template_name = 'orders/library.html'
	def get_queryset(self):
		return ProductPurchase.objects.products_by_request(self.request) #.by_request(self.request).digital()


class VerifyOwnership(View):
	def get(self, request, *args, **kwargs):
		if request.is_ajax():
			data = request.GET
			product_id = data.get('product_id', None)
			print(product_id)
			if product_id is not None:
				product_id = int(product_id)
				ownership_ids = ProductPurchase.objects.products_by_id(request)
				if product_id in ownership_ids:
					return JsonResponse({'owner': True})
			return JsonResponse({'owner': False})
		raise Http404
