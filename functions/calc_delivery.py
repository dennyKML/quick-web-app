import math

from functions.check_number import is_valid_number
from models.delivery_tariff import DeliveryTariff


def calc_delivery_data(request):
    tariff_name = request.form['tariff']
    tariff_cost = DeliveryTariff.get(DeliveryTariff.tariff_name == tariff_name).tariff_min_cost
    data = {
        'from_city_name': request.form['from-city'],
        'to_city_name': request.form['to-city'],
    }

    for field in ['weight', 'width', 'height', 'length', 'estimated_val']:
        value = request.form[field]
        if not is_valid_number(value):
            return None
        data[field] = float(value)

    data['tariff_cost'] = tariff_cost
    return data


def calculate_cost(data):
    return calculate_delivery_cost(data['from_city_name'], data['to_city_name'], data['weight'], data['width'],
                                   data['height'], data['length'], data['estimated_val'], data['tariff_cost'])


def calculate_delivery_cost(from_city_name, to_city_name, weight, width, height, length, estimated_val, tariff_cost):
    if from_city_name == to_city_name:
        cost_package = (float(tariff_cost) + (
                weight / 5 + (width * height * length)/1000000 * 10 / 100 + estimated_val / 100)) * 0.5
    else:
        cost_package = float(tariff_cost) + (weight / 5 + (width * height * length)/1000000 * 10 / 100 + estimated_val / 100)

    return math.ceil(cost_package)
