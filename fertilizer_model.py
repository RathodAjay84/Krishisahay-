# fertilizer_model.py
"""Simple fertilizer recommendation rules based on soil nutrient levels."""


def recommend_fertilizer(n: float, p: float, k: float) -> str:
    """Return a textual fertilizer suggestion based on NPK values.

    This is just an illustrative rule set. A production system would use a
    model trained on soil test results and crop requirements, possibly
    calling an external agronomic service.
    """
    try:
        if n < 50:
            return "Apply Urea to increase nitrogen content."
        elif p < 30:
            return "Apply Single Super Phosphate (SSP) to increase phosphorus."
        elif k < 40:
            return "Apply Muriate of Potash (MOP) to increase potassium."
        else:
            return "Soil nutrients appear balanced; use a general NPK 10-26-26 mix."
    except Exception as e:
        return f"Error computing recommendation: {e}"
