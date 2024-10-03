"""Функции."""


def txt_file(data):
    """Функция переводит из json для получения списка продуктов."""
    result = []
    for item in data:
        name = item['name']
        ingredients_data = item['ingredients']
        ingredients = []
        for ingredient in ingredients_data:
            amount = ingredient['amount']
            ingredient_select = ingredient['name']
            unit = ingredient['measurement_unit']
            ingredients.append(f'{ingredient_select} - {amount} {unit}')
        result.append(f'{name}:{", ".join(ingredients)}')
        return result
