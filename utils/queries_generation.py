import random
import csv
import sys
sys.path.append('/Users/lianadarbinyan/Desktop/AUA/Capstone/Python_Scripts/')
from db.postgresqldb import PostgreSQLDB
import matplotlib.pyplot as plt
import itertools
from sklearn.neighbors import KernelDensity
from sklearn.model_selection import GridSearchCV
import numpy as np


class QueriesGeneration:

    def __init__(self):
        self.histograms = {}

    def generate_queries(self, db_connection, table_name, number_of_queries):
        signs = [">", "<", "=", ">=", "<=", "!="]
        queries = []
        postgres_db = PostgreSQLDB(db_connection)

        columns = postgres_db.get_attrs(table_name)
        domain_value_ranges = self.get_column_value_ranges(db_connection, table_name)
        query_value_ranges = {column: domain_value_ranges[column] for column in columns}

        print(f"when the values are domain values {query_value_ranges}")

        # Generate queries with more than one column
        for r in range(2, len(columns) + 1):
            for combination in itertools.combinations(columns, r):
                for _ in range(number_of_queries):
                    random_values = [round(random.uniform(float(query_value_ranges[column][0]), float(query_value_ranges[column][1])), 3) for column in combination]
                    signs_combination = [random.choice(signs) for _ in combination]
                    predicates = [f"{column} {sign} {value}" for column, sign, value in zip(combination, signs_combination, random_values)]
                    sql_string = f"SELECT * FROM {table_name} WHERE {' AND '.join(predicates)}"
                    try:
                        with db_connection.cursor() as cursor:
                            cursor.execute(sql_string)
                            if cursor.rowcount > 0:
                                selectivity_avi = self.calculate_selectivity_avi(predicates, domain_value_ranges)
                                selectivity_stholes = self.calculate_selectivity_stholes(predicates, domain_value_ranges)
                                queries.append({"query": sql_string, "estimated_selectivity_avi": selectivity_avi, "estimated_selectivity_stholes": selectivity_stholes})
                    except Exception as e:
                        print(f"Error executing query: {e}")

        print(query_value_ranges)
        return queries, query_value_ranges


        #   AVI ASSUMPTION
    def calculate_selectivity_avi(self, used_predicates, domain_value_ranges):
        for predicate in used_predicates:
            column, sign, value = predicate.split()
            domain_min_value, domain_max_value = domain_value_ranges[column]
            domain_min_value, domain_max_value = float(domain_min_value), float(domain_max_value)

            predicate_value = float(value)

            if sign == "=":
                predicate_range_width = 1 if predicate_value >= domain_min_value and predicate_value <= domain_max_value else 0
            elif sign == ">":
                predicate_range_width = max(0, min(predicate_value, domain_max_value) - domain_min_value)
            elif sign == ">=":
                predicate_range_width = max(0, min(predicate_value, domain_max_value) - domain_min_value) + 1
            elif sign == "<":
                predicate_range_width = max(0, domain_max_value - max(predicate_value, domain_min_value))
            elif sign == "<=":
                predicate_range_width = max(0, domain_max_value - max(predicate_value, domain_min_value)) + 1
            else:  # "!="
                predicate_range_width = max(0, domain_max_value - domain_min_value + 1) - (1 if predicate_value == domain_min_value else 0)

            domain_range_width = domain_max_value - domain_min_value + 1
            selectivity_fraction = predicate_range_width / domain_range_width

            return round(selectivity_fraction, 3)


    def calculate_selectivity_stholes(self, predicates, domain_value_ranges):
        total_selectivity = 1.0
        
        for predicate in predicates:
            column, sign, value = predicate.split()
            value = float(value)
            domain_min_val, domain_max_val = domain_value_ranges[column]
            domain_min_val = float(domain_min_val)
            domain_max_val = float(domain_max_val)
            
            if sign == '=':
                subrange_selectivity = self.calculate_equal_subrange_selectivity(value, domain_min_val, domain_max_val)
            elif sign == '>':
                subrange_selectivity = self.calculate_greater_subrange_selectivity(value, domain_min_val, domain_max_val)
            elif sign == '<':
                subrange_selectivity = self.calculate_less_subrange_selectivity(value, domain_min_val, domain_max_val)
            else:
                subrange_selectivity = 1.0
            
            total_selectivity *= subrange_selectivity
        
        return round(total_selectivity, 3)

    def calculate_equal_subrange_selectivity(self, value, domain_min_val, domain_max_val):
        subrange_width = (domain_max_val - domain_min_val) / 10
        subrange_index = int((value - domain_min_val) / subrange_width)
        return 1 / 10  # Assuming equal selectivity within each subrange
    
    def calculate_greater_subrange_selectivity(self, value, domain_min_val, domain_max_val):
        subrange_width = (domain_max_val - domain_min_val) / 10
        subrange_index = int((value - domain_min_val) / subrange_width)
        return (10 - subrange_index) / 10

    def calculate_less_subrange_selectivity(self, value, domain_min_val, domain_max_val):
        subrange_width = (domain_max_val - domain_min_val) / 10
        subrange_index = int((value - domain_min_val) / subrange_width)
        return (subrange_index + 1) / 10


# KDE

    # def calculate_selectivity_kde(self, db_connection, table_name, columns, values):
    #     kde = self.fit_kde(db_connection, table_name, columns)
    #     log_density = kde.score_samples([values])[0]
    #     return np.exp(log_density)
    

    # def fit_kde(self, db_connection, table_name, columns):
    #     data = self.fetch_data(db_connection, table_name, columns)
    #     kde = KernelDensity(kernel='gaussian', bandwidth=0.1).fit(data)
    #     return kde
    
    # def optimal_bandwidth(self, data):
    #     params = {'bandwidth': np.logspace(-1, 1, 20)}
    #     grid = GridSearchCV(KernelDensity(), params, cv=5)
    #     grid.fit(data)
    #     return grid.best_estimator_.bandwidth
    

    # def fetch_data(self, db_connection, table_name, columns):
    #     column_names = ', '.join(columns)
    #     query = f"SELECT {column_names} FROM {table_name}"
    #     with db_connection.cursor() as cursor:
    #         cursor.execute(query)
    #         data = cursor.fetchall()
    #     return data


    def get_column_value_ranges(self, db_connection, table_name):
        postgres_db = PostgreSQLDB(db_connection)
        columns = postgres_db.get_attrs(table_name)
        value_ranges = {}
        
        cursor = db_connection.cursor()
        try:
            for column in columns:
                cursor.execute(f"SELECT MIN({column}), MAX({column}) FROM {table_name}")
                min_val, max_val = cursor.fetchone()
                value_ranges[column] = (min_val, max_val)
        except Exception as e:
            print(f"Error fetching value range for column '{column}': {e}")
        finally:
            cursor.close()
        
        return value_ranges


    def execute_queries(self, db_connection, queries, csv_filename):

        try:
            with db_connection.cursor() as cursor, open(csv_filename, 'w', newline='') as csvfile:
                fieldnames = ['query', 'planning_time_ms', 'execution_time_ms', 'estimated_selectivity_avi', 'estimated_selectivity_stholes']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()

                for query in queries:
                    try:
                        explain_query = f"EXPLAIN (ANALYZE, FORMAT JSON) {query['query']}"
                        cursor.execute(explain_query)
                        explain_result = cursor.fetchall()

                        for row in explain_result:
                            explain_json = row[0][0]
                            planning_time_ms = explain_json.get('Planning Time', 0.0)
                            execution_time_ms = explain_json.get('Execution Time', 0.0)

                    except Exception as e:
                        print(f"Error executing query: {e}")

                    writer.writerow({
                                'query': query['query'],
                                'planning_time_ms': planning_time_ms,
                                'execution_time_ms': execution_time_ms,
                                'estimated_selectivity_avi': query['estimated_selectivity_avi'],
                                'estimated_selectivity_stholes': query['estimated_selectivity_stholes']
                                # 'estimated_selectivity_kde': query['estimated_selectivity_kde']                            
                            })
                    
            print(f"All queries executed and results saved to {csv_filename}.")

        except Exception as e:
            print(f"An error occurred: {e}")


    def generate_bounds_and_rows(self, queries, db_connection, query_value_ranges, csv_filename):
        attribute_bounds = {column: list(domain_range) for column, domain_range in query_value_ranges.items()}
        query_results = {}

        with open(csv_filename, 'w', newline='') as csvfile:
            fieldnames = ['Query number', 'Query', 'Lower bound, Upper bound', 'Label']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()

            for index, query in enumerate(queries):
                predicates = query['query'].split("WHERE")[1].split("AND")
                query_attribute_bounds = {column: list(domain_range) for column, domain_range in query_value_ranges.items()}
                involved_columns = []
                for predicate in predicates:
                    column, sign, value = predicate.split()
                    involved_columns.append(column)
                    value = float(value)
                    if sign == '>=':
                        query_attribute_bounds[column][0] = max(query_attribute_bounds[column][0], value)
                    elif sign == '<=':
                        query_attribute_bounds[column][1] = min(query_attribute_bounds[column][1], value)
                
                lower_upper_bounds = []

                for column in involved_columns:
                    lower_bound = float(query_attribute_bounds[column][0])
                    upper_bound = float(query_attribute_bounds[column][1])
                    lower_upper_bounds.extend([lower_bound, upper_bound])

                try:
                    with db_connection.cursor() as cursor:
                        cursor.execute(query['query'])
                        num_rows = cursor.rowcount
                except Exception as e:
                    print(f"Error executing query: {e}")
                    num_rows = 0

                writer.writerow({
                    'Query number': index + 1,
                    'Query': query['query'],
                    'Lower bound, Upper bound': lower_upper_bounds,
                    'Label': num_rows
                })

                query_results[index + 1] = num_rows

        print(f"Bounds and rows saved to {csv_filename}")

        return query_results


    def plot_actual_vs_estimated(self, queries, db_connection):
        import matplotlib.pyplot as plt
        import numpy as np

        queries_two_columns = [query for query in queries if len(query['query'].split('WHERE')[1].split('AND')) == 2]
        queries_four_columns = [query for query in queries if len(query['query'].split('WHERE')[1].split('AND')) == 4]

        actual_values_two = []
        estimated_values_avi_two = []
        estimated_values_stholes_two = []

        for query in queries_two_columns:
            try:
                with db_connection.cursor() as cursor:
                    cursor.execute(query['query'])
                    rows = cursor.fetchall()
                    total_rows = float(len(rows))
                    actual_rows = cursor.rowcount
                    actual_values_two.append(actual_rows)
                    estimated_values_avi_two.append(query['estimated_selectivity_avi'] * total_rows) 
                    estimated_values_stholes_two.append(query['estimated_selectivity_stholes'] * total_rows) 

            except Exception as e:
                print(f"Error executing query: {e}")

        actual_values_two = np.array(actual_values_two)
        estimated_values_avi_two = np.array(estimated_values_avi_two)
        estimated_values_stholes_two = np.array(estimated_values_stholes_two)
        errors_avi_two = np.maximum(estimated_values_avi_two / actual_values_two, actual_values_two / estimated_values_avi_two)
        errors_stholes_two = np.maximum(estimated_values_stholes_two / actual_values_two, actual_values_two / estimated_values_stholes_two)
        max_error = 2
        upper_bound_avi_two = actual_values_two * max_error
        lower_bound_avi_two = actual_values_two / max_error
        upper_bound_stholes_two = actual_values_two * max_error
        lower_bound_stholes_two = actual_values_two / max_error

        # Calculate the percentage of small errors for two columns
        percentage_small_errors_avi_two = (np.mean(errors_avi_two < 2)) * 100
        percentage_small_errors_stholes_two = (np.mean(errors_stholes_two < 2)) * 100

        fig, axes = plt.subplots(1, 2, figsize=(14, 6))

        ax1 = axes[0]
        ax2 = axes[1]

        ax1.plot(actual_values_two, upper_bound_avi_two, color='grey', linestyle='-')
        ax1.plot(actual_values_two, lower_bound_avi_two, color='grey', linestyle='-')
        ax2.plot(actual_values_two, upper_bound_stholes_two, color='grey', linestyle='-')
        ax2.plot(actual_values_two, lower_bound_stholes_two, color='grey', linestyle='-')

        ax1.scatter(actual_values_two, estimated_values_avi_two, color='black')
        ax1.set_xscale('log')
        ax1.set_yscale('log')
        ax1.set_xlabel('Actual Number of Rows (AVI)')
        ax1.set_ylabel('Estimated Number of Rows (AVI)')
        ax1.set_title(f'AVI ({percentage_small_errors_avi_two:.2f}%) - 2D')

        ax2.scatter(actual_values_two, estimated_values_stholes_two, color='black')
        ax2.set_xscale('log')
        ax2.set_yscale('log')
        ax2.set_xlabel('Actual Number of Rows (STHoles)')
        ax2.set_ylabel('Estimated Number of Rows (STHoles)')
        ax2.set_title(f'STHoles ({percentage_small_errors_stholes_two:.2f}%) - 2D')

        plt.tight_layout()
        plt.savefig("/Users/lianadarbinyan/Desktop/AUA/Capstone/Python_Scripts/plot_2D.png")
        plt.show()

        actual_values_four = []
        estimated_values_avi_four = []
        estimated_values_stholes_four = []

        for query in queries_four_columns:
            try:
                with db_connection.cursor() as cursor:
                    cursor.execute(query['query'])
                    rows = cursor.fetchall()
                    total_rows = float(len(rows))
                    actual_rows = cursor.rowcount
                    actual_values_four.append(actual_rows)
                    estimated_values_avi_four.append(query['estimated_selectivity_avi'] * total_rows) 
                    estimated_values_stholes_four.append(query['estimated_selectivity_stholes'] * total_rows) 

            except Exception as e:
                print(f"Error executing query: {e}")

        actual_values_four = np.array(actual_values_four)
        estimated_values_avi_four = np.array(estimated_values_avi_four)
        estimated_values_stholes_four = np.array(estimated_values_stholes_four)
        errors_avi_four = np.maximum(estimated_values_avi_four / actual_values_four, actual_values_four / estimated_values_avi_four)
        errors_stholes_four = np.maximum(estimated_values_stholes_four / actual_values_four, actual_values_four / estimated_values_stholes_four)
        max_error = 2
        upper_bound_avi_four = actual_values_four * max_error
        lower_bound_avi_four = actual_values_four / max_error
        upper_bound_stholes_four = actual_values_four * max_error
        lower_bound_stholes_four = actual_values_four / max_error

        # Calculate the percentage of small errors for four columns
        percentage_small_errors_avi_four = (np.mean(errors_avi_four < 2)) * 100
        percentage_small_errors_stholes_four = (np.mean(errors_stholes_four < 2)) * 100

        fig, axes = plt.subplots(1, 2, figsize=(14, 6))

        ax1 = axes[0]
        ax2 = axes[1]

        ax1.plot(actual_values_four, upper_bound_avi_four, color='grey', linestyle='-')
        ax1.plot(actual_values_four, lower_bound_avi_four, color='grey', linestyle='-')
        ax2.plot(actual_values_four, upper_bound_stholes_four, color='grey', linestyle='-')
        ax2.plot(actual_values_four, lower_bound_stholes_four, color='grey', linestyle='-')

        ax1.scatter(actual_values_four, estimated_values_avi_four, color='black')
        ax1.set_xscale('log')
        ax1.set_yscale('log')
        ax1.set_xlabel('Actual Number of Rows (AVI)')
        ax1.set_ylabel('Estimated Number of Rows (AVI)')
        ax1.set_title(f'AVI ({percentage_small_errors_avi_four:.2f}%) - 4D')

        ax2.scatter(actual_values_four, estimated_values_stholes_four, color='black')
        ax2.set_xscale('log')
        ax2.set_yscale('log')
        ax2.set_xlabel('Actual Number of Rows (STHoles)')
        ax2.set_ylabel('Estimated Number of Rows (STHoles)')
        ax2.set_title(f'STHole ({percentage_small_errors_stholes_four:.2f}%) - 4D')

        plt.tight_layout()
        plt.savefig("/Users/lianadarbinyan/Desktop/AUA/Capstone/Python_Scripts/plot_4D.png")
        plt.show()
