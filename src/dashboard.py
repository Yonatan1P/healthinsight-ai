import pandas as pd
import plotly.express as px
import streamlit as st

from src.dashboard_queries import build_provider_year_analysis


def render_kpis(kpis: pd.DataFrame):
    if kpis.empty:
        return

    row = kpis.iloc[0]

    cols = st.columns(5)

    with cols[0]:
        st.metric("Patients", f"{int(row['patient_count']):,}")

    with cols[1]:
        st.metric("Encounters", f"{int(row['encounter_count']):,}")

    with cols[2]:
        st.metric("Readmissions", f"{int(row['readmission_count']):,}")

    with cols[3]:
        st.metric("Readmission Rate", f"{row['readmission_rate']:.2f}%")

    with cols[4]:
        st.metric("Avg. Encounter Cost", f"${row['average_cost']:,.0f}")


def render_filters(datasets: dict[str, pd.DataFrame]):
    st.markdown("### Filters")

    patient_volume = datasets["patient_volume"]
    provider_detail = datasets["provider_detail"]
    encounter_mix = datasets["encounter_mix"]

    years = sorted(
        patient_volume["year"]
        .dropna()
        .astype(int)
        .unique()
        .tolist()
    )

    providers = (
        provider_detail[["provider_id", "provider_name"]]
        .drop_duplicates()
        .sort_values("provider_name")
    )

    specialties = sorted(
        provider_detail["specialty"]
        .dropna()
        .unique()
        .tolist()
    )

    encounter_types = sorted(
        encounter_mix["encounter_type"]
        .dropna()
        .tolist()
    )

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        selected_year = st.selectbox(
            "Year",
            ["All Years"] + years,
        )

    with col2:
        provider_options = (
            ["All Providers"]
            + providers["provider_name"].tolist()
        )

        selected_provider = st.selectbox(
            "Provider",
            provider_options,
        )

    with col3:
        selected_specialty = st.selectbox(
            "Specialty",
            ["All Specialties"] + specialties,
        )

    with col4:
        selected_encounter_type = st.selectbox(
            "Encounter Type",
            ["All Encounter Types"] + encounter_types,
        )

    provider_id = None

    if selected_provider != "All Providers":
        provider_id = int(
            providers.loc[
                providers["provider_name"] == selected_provider,
                "provider_id",
            ].iloc[0]
        )

    return {
        "year": (
            None
            if selected_year == "All Years"
            else int(selected_year)
        ),
        "provider_id": provider_id,
        "specialty": (
            None
            if selected_specialty == "All Specialties"
            else selected_specialty
        ),
        "encounter_type": (
            None
            if selected_encounter_type == "All Encounter Types"
            else selected_encounter_type
        ),
    }

def render_patient_volume(patient_volume: pd.DataFrame):
    if patient_volume.empty:
        st.info("No patient volume data available.")
        return

    data = patient_volume.copy()

    provider_totals = (
        data.groupby("provider_name")["patient_count"]
        .sum()
        .sort_values(ascending=False)
        .head(8)
        .index
    )

    data = data[data["provider_name"].isin(provider_totals)]

    fig = px.line(
        data,
        x="year",
        y="patient_count",
        color="provider_name",
        markers=True,
        labels={
            "year": "Year",
            "patient_count": "Patients",
            "provider_name": "Provider",
        },
    )

    fig.update_layout(
        height=400,
        margin=dict(l=10, r=10, t=20, b=10),
        legend_title_text="Provider",
        hovermode="x unified",
    )

    st.plotly_chart(fig, width="stretch")
    st.caption("Top 8 providers by patient volume.")


def render_readmissions(readmissions: pd.DataFrame):
    if readmissions.empty:
        st.info("No readmission data available.")
        return

    data = readmissions.copy()

    provider_avg = (
        data.groupby("provider_name")["readmission_rate"]
        .mean()
        .sort_values(ascending=False)
        .head(10)
    )

    data = data[data["provider_name"].isin(provider_avg.index)]

    latest_year = data["year"].max()

    latest = (
        data[data["year"] == latest_year]
        .sort_values("readmission_rate", ascending=True)
    )

    fig = px.bar(
        latest,
        x="readmission_rate",
        y="provider_name",
        orientation="h",
        labels={
            "readmission_rate": "Readmission Rate (%)",
            "provider_name": "Provider",
        },
        text="readmission_rate",
    )

    fig.update_traces(
        texttemplate="%{text:.1f}%",
        textposition="outside",
    )

    fig.update_layout(
        height=400,
        margin=dict(l=10, r=40, t=20, b=10),
        showlegend=False,
    )

    st.plotly_chart(fig, width="stretch")
    st.caption(f"Provider readmission rates — {int(latest_year)}.")


def render_encounter_mix(encounter_mix: pd.DataFrame):
    if encounter_mix.empty:
        st.info("No encounter mix data available.")
        return

    fig = px.pie(
        encounter_mix,
        names="encounter_type",
        values="encounter_count",
        hole=0.55,
    )

    fig.update_layout(
        height=400,
        margin=dict(l=10, r=10, t=20, b=10),
        legend_title_text="Encounter Type",
    )

    fig.update_traces(
        textposition="inside",
        textinfo="percent+label",
    )

    st.plotly_chart(fig, width="stretch")


def render_cost_by_provider(provider_detail: pd.DataFrame):
    if provider_detail.empty:
        st.info("No provider cost data available.")
        return

    data = (
        provider_detail
        .sort_values("average_cost", ascending=False)
        .head(10)
        .sort_values("average_cost", ascending=True)
        .copy()
    )

    fig = px.bar(
        data,
        x="average_cost",
        y="provider_name",
        orientation="h",
        labels={
            "average_cost": "Average Cost ($)",
            "provider_name": "Provider",
        },
        text="average_cost",
    )

    fig.update_traces(
        texttemplate="$%{text:,.0f}",
        textposition="outside",
    )

    fig.update_layout(
        height=400,
        margin=dict(l=10, r=60, t=20, b=10),
        showlegend=False,
    )

    st.plotly_chart(fig, width="stretch")
    st.caption("Top 10 providers by average encounter cost.")


def render_provider_table(provider_detail: pd.DataFrame):
    if provider_detail.empty:
        st.info("No provider performance data available.")
        return

    display_data = provider_detail.copy()

    display_data["average_cost"] = display_data["average_cost"].map(
        lambda x: f"${x:,.2f}"
    )

    display_data["total_cost"] = display_data["total_cost"].map(
        lambda x: f"${x:,.2f}"
    )

    display_data["readmission_rate"] = display_data["readmission_rate"].map(
        lambda x: f"{x:.2f}%"
    )

    display_data = display_data.rename(
        columns={
            "provider_name": "Provider",
            "specialty": "Specialty",
            "patient_count": "Patients",
            "encounter_count": "Encounters",
            "readmission_count": "Readmissions",
            "readmission_rate": "Readmission Rate",
            "average_cost": "Avg. Cost",
            "total_cost": "Total Cost",
        }
    )

    columns = [
        "Provider",
        "Specialty",
        "Patients",
        "Encounters",
        "Readmissions",
        "Readmission Rate",
        "Avg. Cost",
        "Total Cost",
    ]

    st.dataframe(
        display_data[columns],
        width="stretch",
        hide_index=True,
    )


def render_provider_dashboard(datasets: dict[str, pd.DataFrame]):
    st.subheader("📊 Provider Performance Dashboard")

    filters = render_filters(datasets)

    # Rebuild the dashboard datasets using the selected filters.
    filtered_datasets = build_provider_year_analysis(filters)

    render_kpis(filtered_datasets["kpis"])

    st.divider()

    left, right = st.columns(2)

    with left:
        st.subheader("Patient Volume Over Time")
        render_patient_volume(filtered_datasets["patient_volume"])

    with right:
        st.subheader("Readmission Rate")
        render_readmissions(filtered_datasets["readmissions"])

    left, right = st.columns(2)

    with left:
        st.subheader("Encounter Mix")
        render_encounter_mix(filtered_datasets["encounter_mix"])

    with right:
        st.subheader("Average Cost by Provider")
        render_cost_by_provider(filtered_datasets["provider_detail"])

    st.divider()

    st.subheader("Provider Performance Details")
    render_provider_table(filtered_datasets["provider_detail"])
