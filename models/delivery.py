from peewee import *
from models.client import Client
from models.delivery_tariff import DeliveryTariff
from models.post import Post


mysql_db = MySQLDatabase('postdb', user='root', password='', host='localhost', port=3306)


class BaseModel(Model):
    class Meta:
        database = mysql_db


class Delivery(BaseModel):
    delivery_id = AutoField(primary_key=True)
    sender_id = ForeignKeyField(Client, backref='sender_deliveries')
    receiver_id = ForeignKeyField(Client, backref='receiver_deliveries')
    sender_post_id = ForeignKeyField(Post, backref='sender_post_deliveries')
    receiver_post_id = ForeignKeyField(Post, backref='receiver_post_deliveries')
    tariff_id = ForeignKeyField(DeliveryTariff, backref='deliveries')
    delivery_status = CharField(max_length=50)
    sending_date = DateField()
    receiving_date = DateField()
    delivery_cost = DecimalField(max_digits=10, decimal_places=2)
