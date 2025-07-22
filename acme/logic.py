import json

import chardet
from storage import save_file, remove_tmp_file
from database import PostgresDB, handle_missing_values
import pandas as pd



class LogicException(Exception):
    pass

def allowed_file(filename, config):
    if '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in config['ALLOWED_EXTENSIONS']:
        return True
    else:
        raise LogicException(f'File "{filename}" extensions is not allowed.')

def get_format_file(filename):
    print('get_format_file', filename)
    if '.' in filename:
        print('расширение файла:', filename.rsplit('.', 1)[1].lower())
        return filename.rsplit('.', 1)[1].lower()

def save_file_to_database(file, config):
    print(f'Загружен файл: "{file.filename}"')
    file_path = save_file(file, config)
    print('Файл записан во временное хранилище:', file_path)
    file_type = get_format_file(file.filename)
    dbase = PostgresDB(config)
    dbase.import_file_to_postgres(file_path, file_type)
    # Удаляем файл из временного хранилища после импорта в БД
    remove_tmp_file(file_path)
    print(f'Файл {file.filename} удален из временного хранилища')

def determining_encoding(file_path):
    with open(file_path, 'rb') as f:
        result = chardet.detect(f.read(10000))
    print(f"Кодировка файла: {result['encoding']} (уверенность: {result['confidence']:.2%})")
    return result



def get_statistics(config):
    dbase = PostgresDB(config)
    df = dbase.get_data()

    # Нормализация данных выполняется перед их анализом,
    # т.к. данные в базе могут быть перезаписаны
    normalize_data = handle_missing_values(df)

    median_values = normalize_data.median(numeric_only=True)
    print("Медианные значения:\n", median_values)

    mean_values = normalize_data.mean(numeric_only=True)
    print("Средние значения:\n", mean_values)

    correlation_matrix = normalize_data.corr(numeric_only=True)
    print("Матрица корреляций:\n", correlation_matrix)

    data_median = json.loads(median_values.to_json())
    data_mean = json.loads(mean_values.to_json())
    data_correlation = json.loads(correlation_matrix.to_json())

    result_json = {
        'median_values': data_median,
        'mean_values': data_mean,
        'correlation_matrix': data_correlation
    }
    return json.dumps(result_json)

