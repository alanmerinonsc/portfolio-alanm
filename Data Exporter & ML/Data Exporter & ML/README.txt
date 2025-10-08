# Iris Data Explorer & Classifier

This project demonstrates a complete machine learning workflow using the Iris dataset. 
It includes **data loading, CSV export, model training, evaluation, prediction, and visualization.

---

## Features

1. Data Loading & CSV Export
   - Loads the Iris dataset from `scikit-learn`.
   - Converts the dataset into a clean CSV file (`iris_dataset.csv`).
   - Handles missing values and adds human-readable species names.

2. Machine Learning Model
   - Trains a **Random Forest Classifier** to predict Iris species.
   - Splits data into **training and test sets**.
   - Displays **accuracy metrics** and a **classification report**.
   - Visualizes **feature importance** to understand which measurements influence predictions most.

3. Predictive Capability
   - Users can input new sepal and petal measurements to predict the Iris species.

---

## Installation

1. Clone or download the project folder.
2. Open the folder in **Visual Studio Code**.
3. Create and activate a virtual environment:
   ```bash
   py -m venv .venv
   .venv\Scripts\activate       # Windows
   # or
   source .venv/bin/activate    # Mac/Linux
4. Install required libraries:
     pip install pandas numpy matplotlib seaborn scikit-learn

