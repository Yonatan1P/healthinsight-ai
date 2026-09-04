import pandas as pd
import streamlit as st

from src.agent import ask
from src.dashboard import render_provider_dashboard
from src.visualizer import render_visualization


st.set_page_config(
    page_title="HealthInsight AI",
    page_icon="🏥",
    layout="wide",
)


if "analysis_result" not in st.session_state:
    st.session_state.analysis_result = None


st.title("🏥 HealthInsight AI")

st.markdown(
    """
    **Natural-language healthcare analytics powered by AI**

    Ask questions about the synthetic healthcare dataset and
    HealthInsight AI will generate SQL, analyze the data, and
    explain the results in plain English.
    """
)

st.divider()

st.subheader("Ask a question")

question = st.text_input(
    "Healthcare analytics question",
    placeholder="Example: Analyze how different providers have performed over different years.",
)

if st.button("🔍 Analyze", type="primary"):

    if not question.strip():
        st.warning("Please enter a question.")

    else:
        try:
            with st.spinner("Analyzing your question..."):
                st.session_state.analysis_result = ask(question)

        except Exception as e:
            st.session_state.analysis_result = None

            st.error(
                "Something went wrong while analyzing your question."
            )

            st.exception(e)


result = st.session_state.analysis_result

if result is not None:

    if result["analysis_type"] == "dashboard":

        st.info(
            "HealthInsight AI identified this as a multi-dimensional "
            "analysis and generated a dashboard."
        )

        render_provider_dashboard(
            result["datasets"]
        )

        with st.expander("View analysis plan"):
            st.json(result["plan"])

    else:

        st.subheader("💡 Analysis")
        st.info(result["explanation"])

        st.subheader("📊 Results")

        results = result["results"]

        if results.shape == (1, 1):

            value = results.iloc[0, 0]

            if pd.isna(value):
                st.metric(
                    label=results.columns[0].replace("_", " ").title(),
                    value="No data",
                )

            elif isinstance(value, (int, float)):
                st.metric(
                    label=results.columns[0].replace("_", " ").title(),
                    value=f"{value:,.2f}".rstrip("0").rstrip("."),
                )

            else:
                st.metric(
                    label=results.columns[0].replace("_", " ").title(),
                    value=str(value),
                )

        else:

            rendered_chart = render_visualization(results)

            if rendered_chart:
                st.caption("Visualization")

            st.dataframe(
                results,
                width="stretch",
                hide_index=True,
            )

        with st.expander("View generated SQL"):
            st.code(
                result["sql"],
                language="sql",
            )
