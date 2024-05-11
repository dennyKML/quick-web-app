from peewee import *
from models.city import City


mysql_db = MySQLDatabase('postdb', user='root', password='', host='localhost', port=3306)


class BaseModel(Model):
    class Meta:
        database = mysql_db


class Post(BaseModel):
    post_id = AutoField(primary_key=True)
    city_id = ForeignKeyField(City, backref='posts')
    postcode = CharField(max_length=20)
    address = CharField(max_length=255)
