import random
from datetime import date, timedelta

import pandas as pd


random.seed(42)

NUM_ENCOUNTERS = 5000

ENCOUNTER_TYPES = [
    "Emergency",
    "Inpatient",
    "Outpatient",
]


def random_date(start_date: date, end_date: date) -> date:
    """Return a random date between start_date and end_date."""
    days_between = (end_date - start_date).days
    random_days = random.randint(0, days_between)
    return start_date + timedelta(days=random_days)


def generate_encounters(
    num_encounters: int,
    patient_ids: list[int],
) -> pd.DataFrame:
    """Generate synthetic healthcare encounters."""

    encounters = []

    for encounter_id in range(1, num_encounters + 1):
        patient_id = random.choice(patient_ids)
        encounter_type = random.choice(ENCOUNTER_TYPES)

        encounter_date = random_date(
            date(2023, 1, 1),
            date(2025, 12, 31),
        )

        # Most encounters do not require an inpatient admission.
        if encounter_type == "Inpatient":
            admission_date = encounter_date

            length_of_stay = random.randint(1, 14)

            discharge_date = admission_date + timedelta(
                days=length_of_stay
            )

            total_cost = round(
                random.uniform(5000, 50000),
                2,
            )

        elif encounter_type == "Emergency":
            admission_date = None
            discharge_date = None
            length_of_stay = 0

            total_cost = round(
                random.uniform(500, 10000),
                2,
            )

        else:
            admission_date = None
            discharge_date = None
            length_of_stay = 0

            total_cost = round(
                random.uniform(100, 5000),
                2,
            )

        readmitted_30_days = random.random() < 0.12

        encounters.append(
            {
                "encounter_id": encounter_id,
                "patient_id": patient_id,
                "encounter_date": encounter_date,
                "encounter_type": encounter_type,
                "admission_date": admission_date,
                "discharge_date": discharge_date,
                "length_of_stay": length_of_stay,
                "total_cost": total_cost,
                "readmitted_30_days": readmitted_30_days,
            }
        )

    return pd.DataFrame(encounters)


if __name__ == "__main__":
    patients_df = pd.read_csv("data/patients.csv")

    encounters_df = generate_encounters(
        NUM_ENCOUNTERS,
        patients_df["patient_id"].tolist(),
    )

    output_path = "data/encounters.csv"

    encounters_df.to_csv(output_path, index=False)

    print(f"Generated {len(encounters_df)} synthetic encounters.")
    print(f"Saved to: {output_path}")
    print()
    print(encounters_df.head())
