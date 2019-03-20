from django.db import models

# Create your models here.

class Store(models.Model):

    ROUTER = 'RTR'
    SWITCH = 'SW'
    TRANSCEIVER = 'SFP'
    CABLE = 'CABLE'
    PROJECT = 'PROJECT'
    STOCK = 'STOCK'

    ITEM_TYPE_CHOICES = (
        (ROUTER, 'Router'),
        (SWITCH, 'Switch'),
        (TRANSCEIVER, 'SFP'),
        (CABLE, 'Cable'),
    )

    ITEM_STATUS_CHOICES = (
        (PROJECT, 'Project'),
        (STOCK, 'Stock'),
    )

    item_type = models.CharField(max_length=100, choices=ITEM_TYPE_CHOICES, default=ROUTER)
    item_model = models.CharField(max_length=1000)
    item_quantity = models.IntegerField()
    item_status = models.CharField(max_length=1000, choices=ITEM_STATUS_CHOICES, default=STOCK)

    def __str__(self):
        return "{} {} {} {}".format(self.item_type, self.item_model, self.item_quantity, self.item_status)


