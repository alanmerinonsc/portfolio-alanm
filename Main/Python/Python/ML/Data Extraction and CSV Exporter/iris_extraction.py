# This script loads the Iris dataset, converts it to a pandas DataFrame,
# and exports it as a clean CSV file.

from sklearn.datasets import load_iris
import pandas as pd

#load data set
data = load_iris()
print(data)


#covert to dataframe
df = pd.DataFrame(data.data, columns=data.feature_names)
df.dropna() #to handle missing values if any
df['species'] = data.target
df['species_name'] = [data.target_names[i] for i in data.target]

#save
df.to_csv('iris_dataset.csv', index=False)
print("CSV File 'iris_dataset.csv' created successfully.")

print(df.head())