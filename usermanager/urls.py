from django.urls import path
from . import views 

urlpatterns = [
    path('profile', views.UserViewSet.as_view()),
    path('balance', views.GetBalanceViewSet.as_view()),
    path('logout', views.LogoutViewSet.as_view())
]