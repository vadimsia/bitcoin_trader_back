import os
import django
import requests
import time

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "bitcoin_trader_back.settings")
django.setup()

from terminal.models import Order
from usermanager.models import UserProfile

def get_price():
    while True:
        try:
            response = requests.get('https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT', timeout=10)
            price = response.json()['price']
            return float(price)
        except:
            pass

def longLiquidation(order: Order) -> float:
    percent = 100 / order.leverage / 100
    return order.entry_price - (order.entry_price * percent)

def shortLiquidation(order: Order) -> float:
    percent = 100 / order.leverage / 100
    return order.entry_price + (order.entry_price * percent)

def longPnL(order: Order, price: float) -> float:
    percent = (price - order.entry_price) / order.entry_price
    return order.amount * order.leverage * percent

def shortPnL(order: Order, price: float) -> float:
    percent = -(price - order.entry_price) / order.entry_price
    return order.amount * order.leverage * percent


def cycle():
    price = get_price()
    waiting_orders = Order.objects.filter(state=1) # WAITING STATE

    for order in waiting_orders:
        if order.order_type == 1: # LONG
            if price > order.entry_price:
                continue

            Order.objects.filter(id=order.id).update(state=2) # OPEN STATE
        
        else: #SHORT
            if price < order.entry_price:
                continue

            Order.objects.filter(id=order.id).update(state=2) # OPEN STATE
    

    open_orders = Order.objects.filter(state=2) # OPEN STATE

    for order in open_orders:
        if order.order_type == 1: # LONG
            if order.take_profit != 0 and price >= order.take_profit:
                Order.objects.filter(id=order.id).update(state=3) # TO BECLOSED STATE
            elif order.stop_loss != 0 and price <= order.stop_loss:
                Order.objects.filter(id=order.id).update(state=3) # TO BE CLOSED STATE
            elif price <= longLiquidation(order):
                Order.objects.filter(id=order.id).update(state=4) # CLOSED STATE

        if order.order_type == 2: # SHORT
            if order.take_profit != 0 and price <= order.take_profit:
                Order.objects.filter(id=order.id).update(state=3) # TO BE CLOSED STATE
            elif order.stop_loss != 0 and price >= order.stop_loss:
                Order.objects.filter(id=order.id).update(state=3) # TO BE CLOSED STATE
            elif price <= longLiquidation(order):
                Order.objects.filter(id=order.id).update(state=4) # CLOSED STATE

    to_be_closed = Order.objects.filter(state=3) # TO BE CLOSED STATE

    for order in to_be_closed:
        profiles = UserProfile.objects.filter(user=order.user)
        if not profiles:
            continue

        profile = profiles[0]
        if order.order_type == 1: # LONG
            pnl = longPnL(order, price)
            Order.objects.filter(id=order.id).update(state=4, close_price=price) # CLOSED STATE

            profile.balance += order.amount + pnl
            profile.save()

        if order.order_type == 2: # SHORT
            pnl = shortPnL(order, price)
            Order.objects.filter(id=order.id).update(state=4, close_price=price) # CLOSED STATE

            profile.balance += order.amount + pnl
            profile.save()

while True:
    print("Run cycle")
    cycle()
    time.sleep(10)
