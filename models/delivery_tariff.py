from peewee import *


mysql_db = MySQLDatabase('postdb', user='root', password='', host='localhost', port=3306)


class BaseModel(Model):
    class Meta:
        database = mysql_db


class DeliveryTariff(BaseModel):
    tariff_id = AutoField(primary_key=True)
    tariff_name = CharField(max_length=30)
    tariff_min_cost = DecimalField(max_digits=10, decimal_places=2)
    delivery_min_time = IntegerField()
    delivery_max_time = IntegerField()
