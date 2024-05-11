from peewee import *


mysql_db = MySQLDatabase('postdb', user='root', password='', host='localhost', port=3306)


class BaseModel(Model):
    class Meta:
        database = mysql_db


class Dimension(BaseModel):
    dimension_id = AutoField(primary_key=True)
    width = IntegerField()
    height = IntegerField()
    length = IntegerField()
