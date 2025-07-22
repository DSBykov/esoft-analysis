from flask import Flask
from flask import request

from logic import allowed_file, save_file_to_database, get_statistics
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



API_ROOT_PATH = '/api/v1/'
API_DATA_PATH = API_ROOT_PATH + 'data/'

# POST /upload для загрузки файла
@app.route(API_ROOT_PATH + 'upload' + '/', methods=['POST'])
def api_upload_file():
    if 'file' not in request.files:
        return 'No file part', 500

    file = request.files['file']
    print('pyte upload file:', type(file))

    if file.filename == '':
        return 'No selected file', 501


    elif not allowed_file(file.filename, app.config):
        return 'Unsupported Media Type', 415

    elif file and allowed_file(file.filename, app.config):
        save_file_to_database(file, app.config)
        return f'The file has been saved to database', 201

# GET /data/stats для получения аналитики по загруженным данным
@app.route(API_DATA_PATH + 'stats' + '/')
def api_status():
    data = get_statistics(app.config)
    print('DATA:', data)
    return data, 201


# GET /data/clean для очистки данных
@app.route(API_DATA_PATH + 'clean' + '/')
def api_clean():
    dbase = PostgresDB(app.config)
    dbase.delete_table()
    return 'Clean data', 201

# (Продвинутый уровень) GET /data/plot для получения графика
@app.route(API_DATA_PATH + 'plot' + '/')
def api_plot():
    return 'Plot', 201