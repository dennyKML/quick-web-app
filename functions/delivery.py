import math

from models.delivery_tariff import DeliveryTariff


def calculate_delivery_cost(from_city_name, to_city_name, weight, width, height, length, estimated_val, tariff_name):
    tariff_cost = DeliveryTariff.get(DeliveryTariff.tariff_name == tariff_name).tariff_min_cost
    if from_city_name == to_city_name:
        cost_package = (float(tariff_cost) + (
                weight / 5 + (width * height * length) * 10 / 100 + estimated_val / 100)) * 0.5
    else:
        cost_package = float(tariff_cost) + (weight / 5 + (width * height * length) * 10 / 100 + estimated_val / 100)

    return math.ceil(cost_package)
