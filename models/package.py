from peewee import *
from models.delivery import Delivery
from models.dimension import Dimension


mysql_db = MySQLDatabase('postdb', user='root', password='', host='localhost', port=3306)


class BaseModel(Model):
    class Meta:
        database = mysql_db


class Package(BaseModel):
    package_id = AutoField(primary_key=True)
    delivery_id = ForeignKeyField(Delivery, backref='packages')
    dimension_id = ForeignKeyField(Dimension, backref='packages')
    description = CharField(max_length=255)
    estimated_value = DecimalField(max_digits=10, decimal_places=2)
    weight = DecimalField(max_digits=10, decimal_places=2)
