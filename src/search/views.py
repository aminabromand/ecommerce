from django.shortcuts import render
from django.views.generic import ListView

from products.models import Product

# Create your views here.
class SearchProductView(ListView):
    #queryset = Product.objects.all()
    template_name = 'search/view.html'

    def get_context_data(self, *args, **kwargs):
    	context = super(SearchProductView, self).get_context_data(*args, **kwargs)
    	query = self.request.GET.get('q')
    	context['query'] = query
    	# SerachQuery.objects.create(query=query) # I dont have this, so it is commented out
    	return context
	
    def get_queryset(self, *args, **kwargs):
        print("request: {0}".format(self.request.GET))
        query = self.request.GET.get('q')
        if query is not None:
        	return Product.objects.filter(title__icontains=query)
        return Product.objects.featured()
