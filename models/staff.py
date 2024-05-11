from peewee import *
from models.post import Post


mysql_db = MySQLDatabase('postdb', user='root', password='', host='localhost', port=3306)


class BaseModel(Model):
    class Meta:
        database = mysql_db


class Staff(BaseModel):
    worker_id = AutoField(primary_key=True)
    post_id = ForeignKeyField(Post, backref='staff')
    firstname = CharField(max_length=50)
    lastname = CharField(max_length=50)
    midname = CharField(max_length=50)
