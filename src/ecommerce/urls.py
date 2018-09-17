"""ecommerce URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""

from django.conf import settings
from django.conf.urls.static import static

from django.conf.urls import url, include
from django.contrib import admin
from django.contrib.auth.views import LogoutView
from django.views.generic import TemplateView, RedirectView

# from products.views import (
#     ProductListView,
#     product_list_view, 
#     ProductDetailView,
#     ProductDetailSlugView,
#     product_detail_view,
#     ProductFeaturedListView,
#     ProductFeaturedDetailView,
#     )

# from apps.accounts.views import # guest_register_view, login_page, register_page
from apps.accounts.views import RegisterView, LoginView, GuestRegisterView
from apps.addresses.views import checkout_address_create_view, checkout_address_reuse_view
from apps.analytics.views import SalesView, SalesAjaxView
from apps.billing.views import payment_method_view, payment_method_createview
from apps.carts.views import cart_detail_api_view
from apps.marketing.views import MarketingPreferenceUpdateView, MailchimpWebhookView
from apps.orders.views import LibraryView
from .views import home_page, about_page, contact_page

urlpatterns = [
    url(r'^$', home_page, name='home'),
    url(r'^about/$', about_page, name='about'),
    url(r'^contact/$', contact_page, name='contact'),
    
    url(r'^checkout/address/create/$', checkout_address_create_view, name='checkout_address_create'),
    url(r'^checkout/address/reuse/$', checkout_address_reuse_view, name='checkout_address_reuse'),
    url(r'^logout/$', LogoutView.as_view(), name='logout'),

    # url(r'^login/$', login_page, name='login'),
    url(r'^login/$', LoginView.as_view(), name='login'),
    # url(r'^register/$', register_page, name='register'),
    url(r'^register/guest/$', GuestRegisterView.as_view(), name='guest_register'),
    url(r'^register/$', RegisterView.as_view(), name='register'),
    url(r'^account/', include("apps.accounts.urls", namespace='account')),
    # url(r'^accounts/', RedirectView.as_view(url='/account')),
    url(r'^accounts/', include("apps.accounts.passwords.urls")),

    url(r'^analytics/sales/data/', SalesAjaxView.as_view(), name='sales-analytics-data'),
    url(r'^analytics/sales/', SalesView.as_view(), name='sales-analytics'),

    url(r'^billing/payment-method/create/$', payment_method_createview, name='billing-payment-method-endpoint'),
    url(r'^billing/payment-method/$', payment_method_view, name='billing-payment-method'),

    url(r'^api/cart/', cart_detail_api_view, name='api-cart'),
    url(r'^cart/', include("apps.carts.urls", namespace='cart')),

    url(r'^bootstrap/$', TemplateView.as_view(template_name='bootstrap/example.html')),
    url(r'^orders/', include("apps.orders.urls", namespace='orders')),
    url(r'^products/', include("products.urls", namespace='products')),
    url(r'^search/', include("search.urls", namespace='search')),

    # url(r'^featured/$', ProductFeaturedListView.as_view()),
    # url(r'^featured/(?P<pk>\d+)/$', ProductFeaturedDetailView.as_view()),
    # url(r'^products/$', ProductListView.as_view()),
    # url(r'^products-fbv/$', product_list_view),
    # #url(r'^products/(?P<pk>\d+)/$', ProductDetailView.as_view()),
    # url(r'^products/(?P<slug>[\w-]+)/$', ProductDetailSlugView.as_view()),
    # url(r'^products-fbv/(?P<pk>\d+)/$', product_detail_view),

    url(r'^library/', LibraryView.as_view(), name='library'),
    url(r'^settings/email/$', MarketingPreferenceUpdateView.as_view(), name='marketing-pref'),
    url(r'^settings/', RedirectView.as_view(url='/account')),
    url(r'^webhooks/mailchimp/$', MailchimpWebhookView.as_view(), name='webhooks-mailchimp'),
    url(r'^admin/', admin.site.urls),
]


if settings.DEBUG:
    urlpatterns = urlpatterns + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns = urlpatterns + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
