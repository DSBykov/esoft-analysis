import os
import sys


def save_file(file, config):
    if not os.path.exists(config['UPLOAD_FOLDER']):
        os.makedirs(config['UPLOAD_FOLDER'])
    filepath = os.path.join(config['UPLOAD_FOLDER'], file.filename)
    file.save(filepath)
    print('Файл записан во временное хранилище, папка "uploads" в корне проекта.')
    return filepath

def remove_tmp_file(file):
    try:
        os.remove(file)
        print(f'Файл "{file}" удален из временного хранилища')
        return True

    except FileNotFoundError:
        print(f'Файл "{file}" не найден, удаление не требуется', file=sys.stderr)
        return True  # Файла нет - считаем операцию успешной

    except Exception as e:
        print(f'Неожиданная ошибка при удалении файла "{file}": {str(e)}', file=sys.stderr)
        return False