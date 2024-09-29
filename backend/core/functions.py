"""Функции."""


def txt_file(data):
    """Функция переводит из json для получения списка продуктов."""
    result = []
    for item in data:
        name = item['name']
        ingredients = item['ingredients']
        ingredients_list = []
        for ingredient in ingredients:
            amount = ingredient['amount']
            ingredient_select = ingredient['name']
            unit = ingredient['measurement_unit']
            ingredients_list.append(f'{ingredient_select} - {amount} {unit}')
        result.append(f'{name}:{", ".join(ingredients_list)}')
        return result
