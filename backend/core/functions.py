"""Функции."""


def txt_file(data):
    """Функция переводит из json для получения списка продуктов."""
    result = []
    for item in data:
        name = item['name']
        ingredients = item['ingredients']
        ingredients_list = []
        for ing in ingredients:
            a = ing['amount']
            i = ing['name']
            ml = ing['measurement_unit']
            ingredients_list.append(f'{i} - {a} {ml}')
        result.append(f'{name}:{", ".join(ingredients_list)}')
        return result
