from rest_framework.response import Response
from rest_framework import serializers
from rest_framework.views import APIView

from .models import Order
from usermanager.models import UserProfile


class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = '__all__'


class OrderViewSet(APIView):
    def get(self, request):
        if not request.user.is_authenticated:
            return Response(status=401)

        queryset = Order.objects.filter(user=request.user).order_by('-id')[:10]
        serializer_for_queryset = OrderSerializer(
            instance=queryset, # Передаём набор записей
            many=True
        )
        return Response(serializer_for_queryset.data)


class OpenOrderViewSet(APIView):

    def post(self, request):
        if not request.user.is_authenticated:
            return Response(status=401)

        data = request.data
        profile = UserProfile.objects.get(user=request.user)
        if profile.balance < float(data['amount']):
            return Response(status=501)

        profile.balance -= float(data['amount'])
        profile.save()

        Order.objects.create(
            user=request.user,
            order_type=data['order_type'],
            state=data['state'],
            amount=data['amount'],
            entry_price=data['entry_price'],
            leverage=data['leverage'],
            take_profit=data['take_profit'],
            stop_loss=data['stop_loss']
        )

        return Response()


class CancelPositionViewSet(APIView):
    
    def post(self, request):
        if not request.user.is_authenticated:
            return Response(status=401)

        data = request.data
        Order.objects.filter(user=request.user, id=data['id'], state=1).update(state=5) # CANCELED 
        return Response()


class ClosePositionViewSet(APIView):

    def post(self, request):
        if not request.user.is_authenticated:
            return Response(status=401)

        data = request.data
        Order.objects.filter(user=request.user, id=data['id'], state=2).update(state=3) # TO BE CLOSED
        return Response()