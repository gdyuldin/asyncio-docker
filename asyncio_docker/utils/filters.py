def or_filter(value):
    return value if isinstance(value, (tuple,set,list)) else [value]
