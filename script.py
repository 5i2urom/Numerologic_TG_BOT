from config import DB_URL
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
            user_id BIGINT NOT NULL,
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

def insert_execute(name, date, add, user_id):
    try:
        conn = psycopg2.connect(DB_URL)
        cursor = conn.cursor()
        select_query = f"""SELECT * FROM person
                    WHERE user_id = {user_id} AND
                    name = '{name}' AND date_birth = '{date}' """
        cursor.execute(select_query)
        if cursor.rowcount == 0:
            insert_query = f"""INSERT INTO person (name, date_birth, add_info, user_id)
                               VALUES (%s, %s, %s, %s);"""
            record_to_insert = (name, date, add, user_id)
            cursor.execute(insert_query, record_to_insert) 
        conn.commit()

        cursor.close()
        conn.close()
        print("Успешно")
    except (Exception, psycopg2.Error) as error:
        print("Ошибка", error)   
#create_table()