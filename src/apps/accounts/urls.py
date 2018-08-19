from django.conf.urls import url

from .views import (
    acount_home_view,
    AccountHomeView,
    AccountEmailActivateView,
    )

urlpatterns = [
    url(r'^test/$', acount_home_view, name='test'),
    url(r'^$', AccountHomeView.as_view(), name='home'),
    url(r'^email/confirm/(?P<key>[0-9A-Za-z]+)/$', AccountEmailActivateView.as_view(), name='email-activate'),
]

# account/email/confirm/fadsklfklj/ -> activation view