from peewee import *
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo
from flask_login import UserMixin


mysql_db = MySQLDatabase('postdb', user='root', password='', host='localhost', port=3306)


class BaseModel(Model):
    class Meta:
        database = mysql_db


class Client(BaseModel, UserMixin):
    client_id = AutoField(primary_key=True)
    firstname = CharField(max_length=50)
    lastname = CharField(max_length=50)
    midname = CharField(max_length=50)
    phone = CharField(max_length=20, unique=True)
    email = CharField(max_length=100, unique=True)
    address = CharField(max_length=255)
    password = CharField(max_length=255)

    def is_active(self):
        return True


class RegistrationForm(FlaskForm):
    firstname = StringField('Ім\'я', validators=[DataRequired()])
    lastname = StringField('Прізвище', validators=[DataRequired()])
    midname = StringField('По батькові')
    phone = StringField('Телефон', validators=[DataRequired()])
    email = StringField('Електронна пошта', validators=[DataRequired(), Email()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    submit = SubmitField('Зареєструватися')


class LoginForm(FlaskForm):
    email = StringField('Електронна пошта', validators=[DataRequired(), Email()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    submit = SubmitField('Увійти')
