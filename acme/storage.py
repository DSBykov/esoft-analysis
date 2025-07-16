import os

# UPLOAD_FOLDER = 'uploads'
# if not os.path.exists(UPLOAD_FOLDER):
#     os.makedirs(UPLOAD_FOLDER)

# app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def save_file(file, config):
    if not os.path.exists(config['UPLOAD_FOLDER']):
        os.makedirs(config['UPLOAD_FOLDER'])
    filepath = os.path.join(config['UPLOAD_FOLDER'], file.filename)
    file.save(filepath)
    print('Файл записан во временное хранилище, папка "uploads" в корне проекта.')
    return filepath