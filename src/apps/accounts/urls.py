from django.conf.urls import url

from .views import (
    acount_home_view,
    AccountHomeView,
    )

urlpatterns = [
    url(r'^test/$', acount_home_view, name='test'),
    url(r'^$', AccountHomeView.as_view(), name='home'),
]