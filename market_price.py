# market_price.py
"""Market price lookup and simple trend prediction.

Real implementations would pull live data from commodity exchanges and use
a trained time-series model.  Here we stub out the functionality with
fixed prices and a toy linear regression fitted on synthetic data.
"""

import numpy as np
from sklearn.linear_model import LinearRegression
import plotly.graph_objects as go

# static price list for illustration
BASE_PRICES = {
    "Wheat": 2200,
    "Rice": 2400,
    "Cotton": 5600,
    "Maize": 1800,
}

# synthetic historical data for the last 12 months
HISTORICAL_DATA = {
    "Wheat": [2100, 2150, 2200, 2250, 2300, 2350, 2400, 2350, 2300, 2250, 2200, 2150],
    "Rice": [2300, 2350, 2400, 2450, 2500, 2550, 2600, 2550, 2500, 2450, 2400, 2350],
    "Cotton": [5500, 5550, 5600, 5650, 5700, 5750, 5800, 5750, 5700, 5650, 5600, 5550],
    "Maize": [1700, 1750, 1800, 1850, 1900, 1950, 2000, 1950, 1900, 1850, 1800, 1750],
}

def available_crops():
    """Return the list of crops for which we have price data."""
    return list(BASE_PRICES.keys())

_model = None


def predict_price_trend(crop: str) -> float:
    """Return a very simple "prediction" of next month's price.

    Currently the model is a linear regressor trained on nonsense data; it
    simply returns the base price plus a small random change.
    """
    global _model
    if crop not in BASE_PRICES:
        return 0.0
    base = BASE_PRICES[crop]
    # for demonstration just return base +/- 5%
    return base * (1 + np.random.uniform(-0.05, 0.05))


def get_current_price(crop: str) -> float:
    """Look up the current market price from the static dictionary."""
    return BASE_PRICES.get(crop, 0.0)

def get_price_chart(crop: str):
    """Return a Plotly figure showing price trends for the crop."""
    if crop not in HISTORICAL_DATA:
        return None
    months = [f"Month {i+1}" for i in range(12)]
    prices = HISTORICAL_DATA[crop]
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=months, y=prices, mode='lines+markers', name=crop))
    fig.update_layout(title=f"{crop} Price Trend (Last 12 Months)", xaxis_title="Month", yaxis_title="Price (₹/qtl)")
    return fig
