"""Функции."""
from rest_framework import serializers


def txt_file(data):
    """Функция переводит из json для получения списка продуктов."""
    result = []
    for item in data:
        name = item['name']
        ingredients = item['ingredients']
        ingst = []
        for ing in ingredients:
            a = ing['amount']
            i = ing['name']
            ml = ing['measurement_unit']
            ingst.append(f'{i} - {a} {ml}')
        result.append(f'{name}:{", ".join(ingst)}')
        return result
