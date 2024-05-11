from peewee import *


mysql_db = MySQLDatabase('postdb', user='root', password='', host='localhost', port=3306)


class BaseModel(Model):
    class Meta:
        database = mysql_db


class City(BaseModel):
    city_id = AutoField(primary_key=True)
    city_name = CharField(max_length=50)
