from utils.utils import ConfigReader
from db.postgresqldb import PostgreSQLDB


def test_singleton_connectivity():
    try:
        config_path = r"/Users/lianadarbinyan/Desktop/AUA/Capstone/Python_Scripts/resources/default.init"
        config_reader = ConfigReader(config_path)
        
        database = PostgreSQLDB(
            host=config_reader.get_property("host"),
            port=int(config_reader.get_property("port")),
            dbname=config_reader.get_property("dbname"),
            user=config_reader.get_property("user"),
            password=config_reader.get_property("password"),
            sslmode=config_reader.get_property("sslmode"),
            connectTimeout=int(config_reader.get_property("connect_timeout"))
        )
        
        database.connect()
        print("Successfully connected!")
        
        another_database_reference = PostgreSQLDB(
            host=config_reader.get_property("host"),
            port=int(config_reader.get_property("port")),
            dbname=config_reader.get_property("dbname"),
            user=config_reader.get_property("user"),
            password=config_reader.get_property("password"),
            sslmode=config_reader.get_property("sslmode"),
            connectTimeout=int(config_reader.get_property("connect_timeout"))
        )
        
        print(database == another_database_reference)
        
        database.close()
        print("Successfully disconnected!")

    except Exception as e:
        print(f"An error occurred: {e}")
