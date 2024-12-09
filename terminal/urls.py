
from django.urls import path 
from . import views 

urlpatterns = [
    path('orders', views.OrderViewSet.as_view()),
    path('open_position', views.OpenOrderViewSet.as_view()),
    path('cancel_position', views.CancelPositionViewSet.as_view()),
    path('close_position', views.ClosePositionViewSet.as_view())
]