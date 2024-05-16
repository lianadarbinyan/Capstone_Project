import csv
import numpy as np

def calculate_and_write_q_error(labels, quartet, q_error):
    q_error_values = []

    with open(quartet, 'r', newline='') as file:
        reader = csv.DictReader(file)
        estimated_selectivity_values = [float(row['estimated_selectivity_avi']) for row in reader]

    with open(labels, 'r', newline='') as infile:
        reader = csv.DictReader(infile)
        fieldnames = reader.fieldnames + ['q_error']

        with open(q_error, 'w', newline='') as outfile:
            writer = csv.DictWriter(outfile, fieldnames=fieldnames)
            writer.writeheader()

            for row, estimated_selectivity in zip(reader, estimated_selectivity_values):
                actual_selectivity = float(row['Label'])
                
                if actual_selectivity != 0:
                    if estimated_selectivity != 0:
                        q_error = round(max(estimated_selectivity / actual_selectivity, actual_selectivity / estimated_selectivity), 3)
                else:
                    q_error = float('inf')
                
                row['q_error'] = q_error
                writer.writerow(row)


    # The average q-error
    geometric_mean_q_error = np.exp(np.mean(np.log(q_error_values)))
    print(f"Geometric Mean Q-Error: {geometric_mean_q_error}")

# Example usage:
labels = '/Users/lianadarbinyan/Desktop/AUA/Capstone/Python_Scripts/labels.csv'
q_error = '/Users/lianadarbinyan/Desktop/AUA/Capstone/Python_Scripts/q_error.csv'
quartet = '/Users/lianadarbinyan/Desktop/AUA/Capstone/Python_Scripts/quartet.csv'
calculate_and_write_q_error(labels, quartet, q_error)


