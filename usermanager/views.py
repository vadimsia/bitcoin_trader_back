from rest_framework.response import Response
from django.contrib.auth.models import User
from django.contrib.auth import logout
from rest_framework import serializers
from rest_framework.views import APIView

from .models import UserProfile
from terminal.models import Order

class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'balance']

    balance = serializers.SerializerMethodField()

    def get_balance(self, obj):
        profile = UserProfile.objects.get_or_create(user=obj)
        return profile[0].balance



class UserViewSet(APIView):
    def get(self, request):
        queryset = request.user
        if not request.user.is_authenticated:
            return Response(status=401)

        serializer_for_queryset = UserSerializer(
            instance=queryset, # Передаём набор записей
        )
        return Response(serializer_for_queryset.data)

class GetBalanceViewSet(APIView):
    def get(self, request):
        if not request.user.is_authenticated:
            return Response(status=401)

        profile = UserProfile.objects.get_or_create(user=request.user)[0] 
        if profile.balance > 5 or Order.objects.filter(user=request.user, state__in=[1,2,3]):
            return Response(status=501)
        
        UserProfile.objects.filter(user=request.user).update(balance=100)

class LogoutViewSet(APIView):
    def get(self, request):
        logout(request)
        return Response()