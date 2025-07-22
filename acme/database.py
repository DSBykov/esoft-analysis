import psycopg2
from psycopg2 import sql
import pandas as pd
from sqlalchemy import create_engine


def handle_missing_values(df, strategy='auto'):
    """
    Заполняет пропущенные значения

    Параметры:
        strategy: 'auto', 'mean', 'median', 'mode', 'drop', или конкретное значение
    """
    df_filled = df.copy()
    print('df.columns', df.columns)
    for col in df.columns:
        print('col', col)
        # Пропускаем столбцы без пропусков
        if not df[col].isna().any():
            print(f'Столбец "{col}" НЕ содержит пустые значения')
            continue

        # Автоматический выбор стратегии
        if strategy == 'auto':
            if pd.api.types.is_numeric_dtype(df[col]):
                fill_value = df[col].median()
            else:
                fill_value = df[col].mode()[0]
        elif strategy == 'mean' and pd.api.types.is_numeric_dtype(df[col]):
            print('Выбрана стратегия mean')
            fill_value = df[col].mean()
        elif strategy == 'median' and pd.api.types.is_numeric_dtype(df[col]):
            print('Выбрана стратегия median')
            fill_value = df[col].median()
        elif strategy == 'mode':
            print('Выбрана стратегия mode')
            fill_value = df[col].mode()[0]
        elif strategy == 'drop':
            print('Выбрана стратегия drop')
            print('Rows after:', len(df_filled))
            df_filled = df.dropna(subset=[col])
            print('Rows before:', len(df_filled))
            print(f"Удалены строки с пропусками в столбце {col}")
            continue
        else:
            print('Выбрана стратегия ХЗ')
            fill_value = strategy  # пользовательское значение

        # Заполняем пропуски
        df_filled[col] = df[col].fillna(fill_value)
        print(f"Заполнено {df[col].isnull().sum()} пропусков в {col} значением {fill_value}")

    return df_filled


class PostgresDB:
    DEFAULT_NAME_DB = 'esoft_db'
    DEFAULT_NAME_TABLE = 'default_table'
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

    def delete_table(self):
        try:
            self.cursor.execute(f"DROP TABLE IF EXISTS {self.DEFAULT_NAME_TABLE}")
            self.session.commit()
            print(f'Выполнена очистка данных.')

        except Exception as e:
            print(f'Ошибка при очистке данных: {e}')

    def import_file_to_postgres(self, file, file_type):
        df = None
        if file_type == 'csv':
            df = pd.read_csv(file)
        elif file_type in ['excel', 'xls', 'xlsx']:
            df = pd.read_excel(file)
        print(df)

        # Создание подключения для SQLAlchemy
        engine = create_engine(
            url=f"postgresql+psycopg2://{self.config_app['DB_USER']}:{self.config_app['DB_PASSWORD']}@"\
            f"{self.config_app['DB_HOST']}:{self.config_app['DB_PORT']}/{self.config_app['DB_NAME']}"
        )
        try:
            # Загрузка данных в PostgreSQL
            df.to_sql(
                name=self.DEFAULT_NAME_TABLE,
                con=engine,
                if_exists='replace',  # или 'append' для добавления данных
                index=False,
                method='multi'
            )

            print(f'Данные за файла успешно импортированы в таблицу "{self.DEFAULT_NAME_TABLE}"!')

        except Exception as e:
            print(f"Ошибка при записи в БД: {e}")

    def get_data(self):
        engine = create_engine(f"postgresql://{self.config_app['DB_USER']}:{self.config_app['DB_PASSWORD']}@"
                               f"{self.config_app['DB_HOST']}:{self.config_app['DB_PORT']}/{self.config_app['DB_NAME']}")
        try:
            query = f'SELECT * FROM {self.DEFAULT_NAME_TABLE}'
            df = pd.read_sql(query, engine)
            return df
        except Exception as e:
            print(f"Ошибка при получении данных из базы: {e}")
            return None



    def __del__(self):
        try:
            self.cursor.close()
        except AttributeError as e:
            print('Ошибка:', e)

        try:
            self.session.close()
        except AttributeError as e:
            print('Ошибка:', e)
        print('Подключение к базе данных закрыто!')