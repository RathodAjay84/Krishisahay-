# crop_model.py
"""Simple crop recommendation using a decision tree classifier.
This module trains on a tiny synthetic dataset and caches the model
as a joblib file. In a real application you would replace the training
code with a proper dataset and persist the trained model externally.
"""

import os

import numpy as np
import pandas as pd
from sklearn.tree import DecisionTreeClassifier
import joblib

# path where the trained model is stored
MODEL_PATH = os.path.join(os.path.dirname(__file__), "crop_model.joblib")


def train_model():
    """Train a toy decision tree on synthetic data and save it."""
    # synthetic training data illustrating a few soil/season/rainfall combinations
    data = pd.DataFrame(
        {
            "soil": ["Black", "Black", "Red", "Sandy", "Red", "Sandy", "Black", "Black", "Red", "Sandy", "Black", "Red", "Sandy"],
            "season": ["Kharif", "Rabi", "Kharif", "Rabi", "Zaid", "Kharif", "Rabi", "Zaid", "Kharif", "Rabi", "Kharif", "Rabi", "Zaid"],
            "rainfall": [800, 200, 600, 300, 100, 900, 150, 250, 700, 400, 750, 350, 200],
            "humidity": [60, 40, 70, 50, 30, 80, 35, 45, 75, 55, 65, 45, 40],
            "temperature": [30, 20, 28, 25, 35, 32, 18, 22, 29, 26, 31, 23, 33],
            "crop": ["Cotton", "Wheat", "Cotton", "Wheat", "Maize", "Rice", "Wheat", "Maize", "Rice", "Maize", "Cotton", "Wheat", "Maize"],
        }
    )

    # one-hot encode categorical variables
    X = pd.get_dummies(data[["soil", "season"]])
    X["rainfall"] = data["rainfall"]
    X["humidity"] = data["humidity"]
    X["temperature"] = data["temperature"]
    y = data["crop"]

    clf = DecisionTreeClassifier(random_state=42)
    clf.fit(X, y)
    joblib.dump(clf, MODEL_PATH)
    return clf


def load_model():
    """Load the trained model from disk, training it if necessary."""
    if os.path.exists(MODEL_PATH):
        try:
            return joblib.load(MODEL_PATH)
        except Exception:
            # corrupted file --> retrain
            return train_model()
    else:
        return train_model()


_model = load_model()


def recommend_crop(soil: str, season: str, rainfall: float, humidity: float, temperature: float) -> str:
    """Return a crop recommendation based on simple rules learned by the tree.

    Args:
        soil: type of soil (e.g. 'Black', 'Red', 'Sandy')
        season: 'Kharif', 'Rabi', or 'Zaid'
        rainfall: anticipated seasonal rainfall in mm
        humidity: average humidity in %
        temperature: average temperature in °C
    """
    try:
        df = pd.get_dummies(pd.DataFrame({"soil": [soil], "season": [season]}))
        # ensure same columns and order as training
        for col in _model.feature_names_in_:
            if col not in df.columns:
                df[col] = 0
        df = df[_model.feature_names_in_]
        df["rainfall"] = rainfall
        df["humidity"] = humidity
        df["temperature"] = temperature
        prediction = _model.predict(df)[0]
        return prediction
    except Exception as e:
        return f"Error generating recommendation: {e}"
