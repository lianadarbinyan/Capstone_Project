from utils.utils import ConfigReader
from db.postgresqldb import PostgreSQLDB
from db.db_tests import test_singleton_connectivity
from utils.queries_generation import QueriesGeneration


def main():
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

        try:
            database.connect()
            print("Successfully connected!")
            
            print(database.list_tables())

            table_name = database.list_tables()[2]
            print(table_name)

            # values_to_insert = [(1, 'value1'), (2, 'value2'), (3, 'value3')]
            # database.insert_values(table_name, values_to_insert)
            # print("Values inserted successfully!")
            
            # update_values = ('updated_value', 'condition_value')
            # database.update_values(table_name, update_values)
            # print("Values updated successfully!")
            
            # condition = "column1 = 'condition_value'"
            # selected_values = database.select_values(table_name, condition)
            # print("Selected values:", selected_values)
            
            # delete_condition = "column1 = 'condition_value'"
            # database.delete_values(table_name, delete_condition)
            # print("Values deleted successfully!")


            queries_generator = QueriesGeneration()            
            queries, query_value_ranges = queries_generator.generate_queries(database.connection, table_name, number_of_queries=50)
            
            print(f"{len(queries)} queries generated!")

            queries_generator.execute_queries(database.connection, queries, '/Users/lianadarbinyan/Desktop/AUA/Capstone/Python_Scripts/quartet.csv')  
            print(f"{len(queries)} queries executed!")
            queries_generator.generate_bounds_and_rows(queries, database.connection, query_value_ranges, '/Users/lianadarbinyan/Desktop/AUA/Capstone/Python_Scripts/labels.csv')
            queries_generator.plot_actual_vs_estimated(queries, database.connection)


        finally:    
            database.close()
            print("Successfully disconnected!")
    
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
    # test_singleton_connectivity()
