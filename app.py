import secrets
import logging

from flask import Flask, render_template, request, redirect, url_for, session, flash

from functions.create_delivery import *
from models.city import *
from models.client import *
from models.post import Post
from models.staff import Staff
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
    tab = request.args.get('tab', 'profile')
    delivery_id = request.args.get('delivery_id', None)

    if request.method == 'POST' and tab == 'profile':
        if 'save-changes' in request.form:
            current_user.firstname = request.form['firstname']
            current_user.lastname = request.form['lastname']
            current_user.midname = request.form['midname']
            current_user.phone = request.form['phone']
            current_user.email = request.form['email']
            current_user.address = request.form['address']
            current_user.save()

    if 'receive-button' in request.form:
        delivery = Delivery.get(Delivery.delivery_id == delivery_id)
        delivery.delivery_status = 'Отримано'
        delivery.receiving_date = datetime.now().date()
        delivery.save()

        return redirect(url_for('profile', tab=tab, delivery_id=delivery_id))

    sent_deliveries = None
    received_deliveries = None
    delivery_details = None

    if delivery_id:
        sender_post = Post.alias('sender_post')
        receiver_post = Post.alias('receiver_post')

        delivery_details = (Delivery
                            .select(Delivery, Package, Dimension, DeliveryTariff, sender_post, receiver_post, Client)
                            .join(Package, on=(Delivery.delivery_id == Package.delivery_id))
                            .join(Dimension, on=(Package.dimension_id == Dimension.dimension_id))
                            .join(DeliveryTariff, on=(Delivery.tariff_id == DeliveryTariff.tariff_id))
                            .join(Client, on=(Delivery.sender_id == Client.client_id))
                            .switch(Delivery)
                            .join(sender_post, on=(Delivery.sender_post_id == sender_post.post_id))
                            .switch(Delivery)
                            .join(receiver_post, on=(Delivery.receiver_post_id == receiver_post.post_id))
                            .where(Delivery.delivery_id == delivery_id)
                            .dicts().get())

        sender_post_details = (sender_post
                               .select()
                               .where(sender_post.post_id == delivery_details['sender_post_id'])
                               .dicts().get())

        receiver_post_details = (receiver_post
                                 .select()
                                 .where(receiver_post.post_id == delivery_details['receiver_post_id'])
                                 .dicts().get())

        delivery_details['sender_post_details'] = sender_post_details
        delivery_details['receiver_post_details'] = receiver_post_details

    if tab == 'send':
        sent_deliveries = Delivery.select().where(Delivery.sender_id == current_user.client_id)
    elif tab == 'receive':
        received_deliveries = Delivery.select().where(Delivery.receiver_phone.contains(current_user.phone))

    return render_template('profile.html', current_user=current_user, tab=tab, sent_deliveries=sent_deliveries,
                           received_deliveries=received_deliveries, delivery_details=delivery_details)


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
        tariff_name = request.form['tariff']
        if data is None:
            flash('Введено помилкові дані!', 'danger')
            return redirect(url_for('calc_page'))
        cost_package = calculate_cost(data)
        return render_template('calc_page.html', current_user=current_user, cities=cities, tariffs=tariffs,
                               cost_package=cost_package, tariff_name=tariff_name, from_city=data['from_city_name'],
                               to_city=data['to_city_name'], weight=data['weight'], width=int(data['width']),
                               height=int(data['height']), length=int(data['length']),
                               estimated_val=data['estimated_val'])

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


from peewee import DoesNotExist


@app.route('/locate-package', methods=['GET'])
def locate_package():
    delivery_id = request.args.get('delivery_id', None)

    delivery_details = None

    if delivery_id:
        sender_post = Post.alias('sender_post')
        receiver_post = Post.alias('receiver_post')

        delivery_details = (Delivery
                            .select(Delivery, Package, Dimension, DeliveryTariff, sender_post, receiver_post,
                                    Client)
                            .join(Package, on=(Delivery.delivery_id == Package.delivery_id))
                            .join(Dimension, on=(Package.dimension_id == Dimension.dimension_id))
                            .join(DeliveryTariff, on=(Delivery.tariff_id == DeliveryTariff.tariff_id))
                            .join(Client, on=(Delivery.sender_id == Client.client_id))
                            .switch(Delivery)
                            .join(sender_post, on=(Delivery.sender_post_id == sender_post.post_id))
                            .switch(Delivery)
                            .join(receiver_post, on=(Delivery.receiver_post_id == receiver_post.post_id))
                            .where(Delivery.delivery_id == delivery_id)
                            .dicts().first())

        if not delivery_details:
            return render_template('locate_package.html', current_user=current_user, delivery_id=delivery_id)

        sender_post_details = (sender_post
                               .select()
                               .where(sender_post.post_id == delivery_details['sender_post_id'])
                               .dicts().get())

        receiver_post_details = (receiver_post
                                 .select()
                                 .where(receiver_post.post_id == delivery_details['receiver_post_id'])
                                 .dicts().get())

        delivery_details['sender_post_details'] = sender_post_details
        delivery_details['receiver_post_details'] = receiver_post_details

    return render_template('locate_package.html', current_user=current_user, delivery_details=delivery_details,
                           delivery_id=delivery_id)


@app.route('/locate-posts', methods=['GET'])
def locate_posts():
    cities = City.select()
    selected_city = None
    posts = None
    staff = None
    post = None

    selected_city_name = request.args.get('city_name')
    post_id = request.args.get('post_id')

    if selected_city_name:
        selected_city = City.get_or_none(City.city_name == selected_city_name)
        if selected_city:
            posts = Post.select().where(Post.city_id == selected_city.city_id)

    if post_id:
        post = Post.get_or_none(Post.post_id == post_id)
        if post:
            staff = Staff.select().where(Staff.post_id == post.post_id)

    return render_template('locate_posts.html', current_user=current_user, cities=cities, posts=posts,
                           selected_city=selected_city, post=post, staff=staff)


if __name__ == '__main__':
    app.run()
