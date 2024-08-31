import csv
from django.core.management.base import BaseCommand
from .models import Ingredient

class Command(BaseCommand):
    help = 'Import data from a CSV file into the Ingredient model'

    def add_arguments(self, parser):
        # Добавляем аргумент для пути к CSV-файлу
        parser.add_argument(
            'csv_file',  # Имя аргумента
            type=str,    # Тип данных аргумента
            help='Path to the CSV file to import'  # Описание аргумента
        )

    def handle(self, *args, **kwargs):
        # Получаем путь к CSV-файлу из аргументов команды
        file_path = kwargs['csv_file']
        
        # Открываем CSV-файл для чтения
        with open(file_path, 'r', encoding='utf-8') as csv_file:
            # Создаем объект csv_reader для чтения строк из CSV-файла
            csv_reader = csv.reader(csv_file)
            
            # Пропускаем заголовок CSV-файла, если он есть
            next(csv_reader, None)
            
            # Проходим по всем строкам в CSV-файле
            for row in csv_reader:
                # Проверяем, что строка содержит ровно 2 элемента (name и measure)
                if len(row) != 2:
                    # Выводим сообщение в случае ошибки (неправильное количество элементов в строке)
                    self.stdout.write(f"Invalid row: {row}")
                    continue  # Переходим к следующей строке
                
                # Разделяем строку на имя и единицу измерения
                name, measure = row
                
                # Удаляем пробелы вокруг имени и единицы измерения
                name = name.strip()
                measure = measure.strip()
                
                # Создаем новый объект Ingredient, если его нет в базе данных,
                # иначе просто возвращаем существующий
                Ingredient.objects.get_or_create(name=name, measure=measure)
        
        # Выводим сообщение об успешном импорте данных
        self.stdout.write(self.style.SUCCESS('Data imported successfully'))