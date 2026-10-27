def clamp(min_value, max_value, value):
    if value < min_value:
        value = min_value

    if value > max_value:
        value = max_value

    return value