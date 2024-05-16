import psycopg2
import psycopg2.extras
from db.db_service import IDatabase, SingletonMeta
from typing import List


class PostgreSQLDB(IDatabase, metaclass=SingletonMeta):
    def __init__(self, host, port, dbname, user, password, sslmode, connectTimeout):
        self.url = f"\
                    dbname='{dbname}' \
                    user='{user}' \
                    password='{password}' \
                    host='{host}' \
                    port='{port}' \
                    sslmode='{sslmode}' \
                    connect_timeout='{connectTimeout}'"
                     
        self.connection = None

    def connect(self):
        try:
            self.connection = psycopg2.connect(self.url)
            return self.connection
        except Exception as e:
            print(f"An error occurred: {e}")

    def close(self):
        try:
            if self.connection is not None:
                self.connection.close()
        except Exception as e:
            print(f"An error occurred: {e}")

    def list_tables(self) -> List[str]:
        tables = []
        try:
            with self.connection.cursor() as cursor:
                cursor.execute("""SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'""")
                for table in cursor.fetchall():
                    tables.append(table[0])
        except Exception as e:
            print(f"An error occurred: {e}")
        return tables
    
    def get_attrs(self, table_name):
        attributes = []
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(f"SELECT column_name FROM information_schema.columns WHERE table_name='{table_name}'")
                attributes = [attr[0] for attr in cursor.fetchall()]
        except Exception as e:
            print(f"Error fetching attributes: {e}")
        finally:
            cursor.close()
        return attributes

    def get_attrs_and_dtypes(self, table_name):
        attrs_and_dtypes = {}
        try:
            with self.connection.cursor() as cursor:
                cursor.execute(f"SELECT column_name, data_type FROM information_schema.columns WHERE table_name='{table_name}'")
                attrs_and_dtypes = {row[0]: row[1] for row in cursor.fetchall()}
        except Exception as e:
            print(f"Error fetching attributes and data types: {e}")
        finally:
            cursor.close()
        return attrs_and_dtypes

    def insert_values(self, table_name, values):
        try:
            with self.connection.cursor() as cursor:
                query = f"INSERT INTO {table_name} VALUES %s"
                psycopg2.extras.execute_values(cursor, query, values)
                self.connection.commit()
                print("Values inserted successfully.")
        except Exception as e:
            print(f"An error occurred during insertion: {e}")

    def update_values(self, table_name, values):
        try:
            with self.connection.cursor() as cursor:
                query = f"UPDATE {table_name} SET column1 = %s, column2 = %s WHERE condition = %s"
                cursor.execute(query, values)
                self.connection.commit()
                print("Values updated successfully.")
        except Exception as e:
            print(f"An error occurred during update: {e}")

    def select_values(self, table_name, condition):
        try:
            with self.connection.cursor() as cursor:
                query = f"SELECT * FROM {table_name} WHERE {condition}"
                cursor.execute(query)
                return cursor.fetchall()
        except Exception as e:
            print(f"An error occurred during selection: {e}")

    def delete_values(self, table_name, condition):
        try:
            with self.connection.cursor() as cursor:
                query = f"DELETE FROM {table_name} WHERE {condition}"
                cursor.execute(query)
                self.connection.commit()
                print("Values deleted successfully.")
        except Exception as e:
            print(f"An error occurred during deletion: {e}")

