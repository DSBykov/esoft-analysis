import psycopg2
from psycopg2 import sql, OperationalError
import pandas as pd
from sqlalchemy import create_engine

from logic import determining_encoding

from ftfy import fix_text, fix_encoding_and_explain
import urllib.parse


class PostgresDB:
    DEFAULT_NAME_DB = 'default_database_name'
    def __init__(self, config):
        self.config_app = config
        # Подключение к серверу PostgreSQL (не к конкретной БД)
        self.session = psycopg2.connect(
            # Подключаемся к стандартной БД 'postgres'
            dbname = self.config_app['DB_NAME'], # 'postgres',
            user = self.config_app['DB_USER'],
            password = self.config_app['DB_PASSWORD'],
            host = self.config_app['DB_HOST'],
            client_encoding = self.config_app['DB_ENCODING']
        )
        # Для создания БД нужен autocommit
        self.session.autocommit = True

        self.cursor = self.session.cursor()


    def create_db(self):
        print(f'Создание БД "{self.DEFAULT_NAME_DB}"')
        self.cursor.execute(sql.SQL("CREATE DATABASE {}").format(sql.Identifier(self.DEFAULT_NAME_DB)))
        print(f'Пустая БД "{self.DEFAULT_NAME_DB}" создана!')

    def db_is_exists(self):
        try:
            self.cursor.execute('SELECT datname FROM pg_database WHERE datname = %s;',
                                (self.DEFAULT_NAME_DB,))
            exists = self.cursor.fetchone() is not None
        except Exception as e:
            print(f'Ошибка: {e}')
            return False

        if exists:
            print(f'БД "{self.DEFAULT_NAME_DB}" существует!')
            return True
        else:
            print(f'БД "{self.DEFAULT_NAME_DB}" не найдена.')
            return False

    def delete_db(self):
        try:
            if self.db_is_exists():
                self.cursor.execute(f'DROP DATABASE {self.DEFAULT_NAME_DB};')
                print(f'База данных "{self.DEFAULT_NAME_DB}" успешно удалена.')
            else:
                print(f'База данных "{self.DEFAULT_NAME_DB}" не существует.')

        except OperationalError as e:
            print(f'Ошибка при удалении БД: {e}')

    def import_csv_to_postgres(self, csv_file, table_name='default_table'):
        df = pd.read_csv(csv_file)
        print(df)
        # Создание подключения
        engine = create_engine(
            url=f"postgresql+psycopg2://{self.config_app['DB_USER']}:{self.config_app['DB_PASSWORD']}@"\
            f"{self.config_app['DB_HOST']}:{self.config_app['DB_PORT']}/{self.config_app['DB_NAME']}"
            # client_encoding='ascii'
        )
        try:
                # Загрузка данных в PostgreSQL
            df.to_sql(
                name=table_name,
                con=engine,
                if_exists='replace',  # или 'append' для добавления данных
                index=False,
                method='multi'
            )

            print(f'Данные за файла успешно импортированы в таблицу "{table_name}"!')

        except Exception as e:
            print(f"Ошибка при записи в БД: {e}")

    def import_excel_to_postgres(self):
        pass

    def __del__(self):
            try:
                self.cursor.close()
            except AttributeError as e:
                print('Ошибка:', e)

            try:
                self.session.close()
            except AttributeError as e:
                print('Ошибка:', e)