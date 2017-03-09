from django.conf.urls import url
from . import views


urlpatterns = [
    url(r'^test', views.TestViewSet.as_view(), name='test'),
]

