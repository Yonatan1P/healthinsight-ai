import pandas as pd
import streamlit as st


def render_visualization(results: pd.DataFrame):
    """
    Render a chart when the result structure is appropriate.

    Returns:
        True if a visualization was rendered, otherwise False.
    """

    if results.empty:
        return False

    # We only automatically visualize simple two-column results.
    if len(results.columns) != 2:
        return False

    x_column = results.columns[0]
    y_column = results.columns[1]

    x = results[x_column]
    y = results[y_column]

    # The chart needs a numeric measure.
    if not pd.api.types.is_numeric_dtype(y):
        return False

    # Avoid charts with too many categories.
    if len(results) > 20:
        return False

    # Detect year-based results.
    is_year = (
        pd.api.types.is_numeric_dtype(x)
        and x.notna().all()
        and x.between(1900, 2100).all()
    )

    if is_year:
        chart_data = results.set_index(x_column)
        st.line_chart(chart_data[y_column])
        return True

    # Categorical comparison.
    if not pd.api.types.is_numeric_dtype(x):
        chart_data = results.set_index(x_column)
        st.bar_chart(chart_data[y_column])
        return True

    return False
