from django.conf.urls import url
from . import views


urlpatterns = [
    url(r'^test$', views.TestViewSet.as_view(), name='test'),
    url(r'^game/cancel$', views.GameCancelViewSet.as_view(), name='game-cancel'),
    url(r'^game$', views.GameViewSet.as_view(), name='game'),
    url(r'^dart/cancel$', views.DartCancelViewSet.as_view(), name='dart-cancel'),
    url(r'^dart$', views.DartViewSet.as_view(), name='dart'),
    url(r'^status$', views.StatusViewSet.as_view(), name='status'),
    url(r'^ui/paolo$', views.ui_paolo, name='ui-paolo'),
    url(r'^ui/rodrigo$', views.ui_rodrigo, name='ui-rodrigo'),
    url(r'^ui$', views.ui, name='ui'),
]

