# 🌸 Iris Species Classification with Random Forest

This project demonstrates a simple machine learning pipeline using the classic Iris dataset. It includes data loading, preprocessing, model training with a Random Forest classifier, evaluation, prediction, and feature importance visualization.

## 📦 Dependencies
- pandas  
- numpy  
- matplotlib  
- seaborn  
- scikit-learn  

Install them via pip:
```bash
pip install pandas numpy matplotlib seaborn scikit-learn
```

## 📁 Dataset
The dataset used is `iris_dataset.csv`, which should contain the following columns:
- `sepal length (cm)`
- `sepal width (cm)`
- `petal length (cm)`
- `petal width (cm)`
- `species`
- `species_name` *(used for final prediction label)*

## 🚀 Workflow Overview
1. **Load Data**: Read the CSV and preview the first few rows.
2. **Feature Selection**: Extract numeric features (`x`) and target labels (`y`).
3. **Split Data**: Use `train_test_split` to divide data into training and testing sets.
4. **Train Model**: Fit a `RandomForestClassifier` with 100 trees.
5. **Evaluate**: Print accuracy and classification report.
6. **Predict Sample**: Classify a sample flower with known measurements.
7. **Visualize Importance**: Plot feature importances using Seaborn.

## 🧪 Sample Prediction
```python
sample = np.array([[5.1, 3.5, 1.4, 0.2]])
predicted_class = df['species_name'].unique()[model.predict(sample)[0]]
print("Predicted species:", predicted_class)
```

## 📊 Feature Importance
The script visualizes which features contributed most to the model’s decisions using a barplot.

```python
importance = model.feature_importances_
features = x.columns

sns.barplot(x=importance, y=features, palette='viridis')
plt.title('Feature Importance')
plt.show()
```

## 📝 Notes
- Ensure the dataset includes the `species_name` column for correct sample prediction.
- Avoid renaming or relocating the dataset without updating the path in `pd.read_csv()`.

## 📌 Author
Alan M.