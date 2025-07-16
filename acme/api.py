from flask import Flask, flash, redirect
from flask import request

from logic import allowed_file
from storage import save_file
from database import PostgresDB

class ApiException(Exception):
    pass

app = Flask(__name__)

app.config['ALLOWED_EXTENSIONS'] = {'csv', 'xls', 'xlsx'}
app.config['DB_NAME'] = 'esoft_db'
app.config['DB_USER'] = 'postgres'
app.config['DB_PASSWORD'] = 'TheItCrowd_86'
app.config['DB_HOST'] = 'localhost'
app.config['DB_PORT'] = 5432
app.config['DB_ENCODING'] = 'UTF8'
app.config['UPLOAD_FOLDER'] = 'uploads'

dbase = PostgresDB(app.config)

API_ROOT_PATH = '/api/v1/'
API_DATA_PATH = API_ROOT_PATH + 'data/'

# UPLOAD_FOLDER = 'uploads'
# app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# POST /upload для загрузки файла
@app.route(API_ROOT_PATH + 'upload' + '/', methods=['POST'])
def api_upload_file():
    if 'file' not in request.files:
        raise ApiException('No file part')
        # return 'No file part', 500

    file = request.files['file']
    if file.filename == '':
        # return 'No selected file', 501
        raise ApiException('No selected file')
        # return redirect(request.url)

    if file and allowed_file(file.filename, app.config):
        print(f'Загружен файл: "{file.filename}"')
        file_path = save_file(file, app.config)
        dbase.import_csv_to_postgres(csv_file=file_path)
        return f'The file has been saved to {file_path}', 201

# GET /data/stats для получения аналитики по загруженным данным
@app.route(API_DATA_PATH + 'stats' + '/')
def api_status():
    return 'Return status', 201


# GET /data/clean для очистки данных
@app.route(API_DATA_PATH + 'clean' + '/')
def api_clean():
    return 'Clean data', 201

# (Продвинутый уровень) GET /data/plot для получения графика
@app.route(API_DATA_PATH + 'plot' + '/')
def api_plot():
    return 'Plot', 201