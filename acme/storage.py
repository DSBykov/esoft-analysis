import os

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
    except Exception as e:
        print(f'Не удалось удалить файл "{file}" из временного хранилища.')