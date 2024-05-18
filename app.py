import secrets
import logging

from flask import Flask, render_template, request, redirect, url_for, session, flash

from functions.create_delivery import *
from models.city import *
from models.client import *
from models.post import Post
from functions.calc_delivery import *
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import current_user, LoginManager, login_user, logout_user

app = Flask(__name__)
app.secret_key = secrets.token_hex()
login_manager = LoginManager(app)


@app.route('/')
def index():
    return render_template('index.html', current_user=current_user)


@login_manager.user_loader
def load_user(user_id):
    return Client.get_by_id(user_id)


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        if not Client.select().where(Client.email == form.email.data).exists() and \
                not Client.select().where(Client.phone == form.phone.data).exists():
            hashed_password = generate_password_hash(form.password.data)
            Client.create(
                firstname=form.firstname.data,
                lastname=form.lastname.data,
                midname=form.midname.data,
                phone=form.phone.data,
                email=form.email.data,
                password=hashed_password
            )
            flash('Користувача успішно зареєстровано!', 'success')
            return redirect(url_for('login'))
        elif Client.select().where(Client.phone == form.phone.data).exists():
            flash('Користувач з цим номером телефону вже існує.', 'danger')
        else:
            flash('Користувач з цією електронною адресою вже існує.', 'danger')
            return render_template('register.html', form=form)
    return render_template('register.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data

        user = Client.get_or_none(Client.email == email)
        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('index'))
        else:
            flash('Невірна електронна адреса або пароль.', 'danger')
    return render_template('login.html', form=form)


@app.route('/profile', methods=['GET', 'POST'])
def profile():
    if request.method == 'POST':
        if 'save-changes' in request.form:
            current_user.firstname = request.form['firstname']
            current_user.lastname = request.form['lastname']
            current_user.midname = request.form['midname']
            current_user.phone = request.form['phone']
            current_user.email = request.form['email']
            current_user.address = request.form['address']
            current_user.save()
    return render_template('profile.html', current_user=current_user)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/calc-page', methods=['GET', 'POST'])
def calc_page():
    cities = City.select()
    tariffs = DeliveryTariff.select()
    if request.method == 'POST':
        data = calc_delivery_data(request)
        if data is None:
            flash('Введено помилкові дані!', 'danger')
            return redirect(url_for('calc_page'))
        cost_package = calculate_cost(data)
        return render_template('calc_page.html', current_user=current_user, cities=cities, tariffs=tariffs,
                               cost_package=cost_package)

    return render_template('calc_page.html', current_user=current_user, cities=cities, tariffs=tariffs)


@app.route('/create-page', methods=['GET', 'POST'])
def create_page():
    cities = City.select()
    posts = Post.select()
    tariffs = DeliveryTariff.select()
    if request.method == 'POST':
        data = create_delivery_data(request)
        if data is None:
            flash('Введено помилкові дані!', 'danger')
            return redirect(url_for('create_page'))
        try:
            create_delivery(data)
            flash('Бандеролька успішно відправлена!', 'success')
        except Exception as e:
            flash(f'При відправлені бандерольки сталася помилка: {e}', 'danger')

        return redirect(url_for('create_page'))

    return render_template('create_page.html', current_user=current_user, cities=cities, posts=posts,
                           tariffs=tariffs)


@app.route('/locate-package')
def locate_package():
    return render_template('locate_package.html', current_user=current_user)


@app.route('/locate-posts')
def locate_posts():
    return render_template('locate_posts.html', current_user=current_user)


if __name__ == '__main__':
    app.run()
