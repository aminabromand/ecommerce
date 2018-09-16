import datetime
from django.contrib.auth.mixins import LoginRequiredMixin
#from django.db.models import Count, Sum, Avg
from django.http import HttpResponse, JsonResponse
from django.views.generic import TemplateView, View
from django.shortcuts import render
from django.utils import timezone

from apps.orders.models import Order

# Create your views here.

class SalesAjaxView(LoginRequiredMixin, View):
	def get(self, request, *args, **kwargs):
		data = {}
		if request.user.is_staff:
			if request.GET.get('type') == 'week':
				data['labels'] = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
				data['data'] = [12, 19, 3, 5, 2, 3, 69]
			if request.GET.get('type') == '4weeks':
				data['labels'] = ["Last week", "2 weeks ago", "3 weeks ago", "4 weeks ago"]
				data['data'] = [12, 19, 3, 5]
		return JsonResponse(data)


class SalesView(LoginRequiredMixin, TemplateView):
	template_name = 'analytics/sales.html'

	def dispatch(self, *args, **kwargs):
		user = self.request.user
		if not user.is_staff:
			return render(self.request, "400.html", {})
		return super(SalesView, self).dispatch(*args, **kwargs)

	def get_context_data(self, *args, **kwargs):
		context = super(SalesView, self).get_context_data(*args, **kwargs)
		qs = Order.objects.all().by_weeks_range(weeks_ago=10, number_of_weeks=10)
		context['today'] = qs.by_range(timezone.now().date()).get_sales_breakdown()
		context['this_week'] = Order.objects.all().by_weeks_range(weeks_ago=1, number_of_weeks=1).get_sales_breakdown()
		context['last_four_weeks'] = Order.objects.all().by_weeks_range(weeks_ago=5, number_of_weeks=4).get_sales_breakdown()

		return context
