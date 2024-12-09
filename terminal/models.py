from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    order_type = models.SmallIntegerField()
    state = models.SmallIntegerField()
    amount = models.FloatField()
    entry_price = models.FloatField()
    leverage = models.SmallIntegerField()
    take_profit = models.FloatField()
    stop_loss = models.FloatField()