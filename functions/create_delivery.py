from flask_login import current_user

import random
from models.city import *
from decimal import Decimal
from models.post import Post
from datetime import datetime
from models.package import Package
from models.delivery import Delivery
from models.dimension import Dimension
from models.delivery_tariff import DeliveryTariff
from functions.check_number import is_valid_number
from functions.calc_delivery import calculate_delivery_cost


def create_delivery_data(request):
    data = {
        'receiver_fullname': request.form['receiver_fullname'],
        'receiver_phone': request.form['receiver_phone'],
        'from_city_id': request.form['from-city'],
        'to_city_id': request.form['to-city'],
        'from_post_address': request.form['from-post'],
        'to_post_address': request.form['to-post'],
        'description': request.form['description'],
        'tariff_id': request.form['tariff']
    }

    for field in ['weight', 'width', 'height', 'length', 'estimated_val']:
        value = request.form[field]
        if not is_valid_number(value):
            return None
        data[field] = float(value)

    return data


def create_delivery(data):
    from_city_name = City.get(City.city_id == data['from_city_id']).city_name
    to_city_name = City.get(City.city_id == data['to_city_id']).city_name
    from_post_id = Post.get(Post.address == data['from_post_address']).post_id
    to_post_id = Post.get(Post.address == data['to_post_address']).post_id
    tariff = DeliveryTariff.get(DeliveryTariff.tariff_id == data['tariff_id'])
    tariff_day_min = tariff.delivery_min_time
    tariff_day_max = tariff.delivery_max_time
    tariff_cost = tariff.tariff_min_cost
    random_delivery_time = random.randint(tariff_day_min, tariff_day_max)
    current_datetime = datetime.utcnow()
    sending_date = current_datetime.date()
    delivery_cost = calculate_delivery_cost(from_city_name, to_city_name, data['weight'], data['width'], data['height'],
                                            data['length'], data['estimated_val'], tariff_cost)

    with mysql_db.atomic():
        dimension = Dimension.create(width=data['width'], height=data['height'], length=data['length'])

        delivery = Delivery.create(sender_id=current_user.client_id,
                                   receiver_fullname=data['receiver_fullname'],
                                   receiver_phone=data['receiver_phone'],
                                   sender_post_id=from_post_id,
                                   receiver_post_id=to_post_id,
                                   delivery_status='Відправлено',
                                   sending_date=sending_date,
                                   receiving_days=random_delivery_time,
                                   delivery_cost=Decimal(delivery_cost),
                                   tariff_id=data['tariff_id'])

        package = Package.create(delivery_id=delivery.delivery_id,
                                 dimension_id=dimension.dimension_id,
                                 description=data['description'],
                                 estimated_value=Decimal(data['estimated_val']),
                                 weight=Decimal(data['weight']))

        delivery.package = package
        delivery.save()
