def is_valid_number(value, key=None):
    obj = {
        'weight': (0, 30),
        'width': (0, 5000),
        'height': (0, 2000),
        'length': (0, 3000),
        'estimated_val': (0, 100000)
    }

    try:
        number = float(value)
        if number <= 0:
            return False

        if key and key in obj:
            min_val, max_val = obj[key]
            if not (min_val < number <= max_val):
                return False

        return True
    except ValueError:
        return False
