from config import *
import psycopg2
def create_table():
    try:
        conn = psycopg2.connect(DB_URL)
        cursor = conn.cursor()

        create_table_query = '''
        CREATE TABLE IF NOT EXISTS person (
            id SERIAL PRIMARY KEY,
            name TEXT NOT NULL,
            date_birth DATE NOT NULL,
            add_info TEXT,
            user_id VARCHAR(15) NOT NULL CHECK (user_id ~* '^[0-9]+$'),
            UNIQUE(name, date_birth)
        );
        CREATE INDEX index_person ON person (name, date_birth);
        '''
        cursor.execute(create_table_query)
        conn.commit()

        cursor.close()
        conn.close()
        print("Таблица успешно создана.")
    except (Exception, psycopg2.Error) as error:
        print("Ошибка при создании таблицы:", error)
create_table()