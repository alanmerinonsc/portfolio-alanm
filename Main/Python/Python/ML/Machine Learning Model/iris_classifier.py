import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns


df = pd.read_csv('iris_dataset.csv')
print(df.head())

#numeric colums
x = df[['sepal length (cm)', 'sepal width (cm)', 'petal length (cm)', 'petal width (cm)']]

#species label
y = df['species']

from sklearn.model_selection import train_test_split
x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.2, random_state=42)

from sklearn.ensemble import RandomForestClassifier
model = RandomForestClassifier(n_estimators=100)
model.fit(x_train, y_train)

from sklearn.metrics import accuracy_score, classification_report
y_pred = model.predict(x_test)
print("Accuracy:", accuracy_score(y_test, y_pred))
print(classification_report(y_test, y_pred))

sample = np.array([[5.1, 3.5, 1.4, 0.2]]) #example sample
predicted_class = df['species_name'].unique()[model.predict(sample)[0]]
print("Predicted species:", predicted_class)

#visualization
importance = model.feature_importances_
features = x.columns

sns.barplot(x=importance, y=features, palette='viridis')
plt.title('Feature Importance')
plt.show()