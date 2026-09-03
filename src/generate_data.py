import random
from datetime import date, timedelta

import pandas as pd


# Make our synthetic data reproducible.
random.seed(42)

NUM_PATIENTS = 1000

GENDERS = ["Male", "Female", "Other"]

INSURANCE_TYPES = [
    "Medicare",
    "Medicaid",
    "Commercial",
    "Self-Pay",
]

ZIP_CODES = [
    "98004",
    "98005",
    "98006",
    "98007",
    "98008",
    "98052",
    "98053",
    "98074",
    "98075",
]


def random_date(start_date: date, end_date: date) -> date:
    """Return a random date between start_date and end_date."""
    days_between = (end_date - start_date).days
    random_days = random.randint(0, days_between)
    return start_date + timedelta(days=random_days)


def generate_patients(num_patients: int) -> pd.DataFrame:
    """Generate a synthetic patient dataset."""

    patients = []

    for patient_id in range(1, num_patients + 1):
        patients.append(
            {
                "patient_id": patient_id,
                "date_of_birth": random_date(
                    date(1930, 1, 1),
                    date(2010, 12, 31),
                ),
                "gender": random.choice(GENDERS),
                "insurance_type": random.choice(INSURANCE_TYPES),
                "zip_code": random.choice(ZIP_CODES),
            }
        )

    return pd.DataFrame(patients)


if __name__ == "__main__":
    patients_df = generate_patients(NUM_PATIENTS)

    output_path = "data/patients.csv"

    patients_df.to_csv(output_path, index=False)

    print(f"Generated {len(patients_df)} synthetic patients.")
    print(f"Saved to: {output_path}")
    print()
    print(patients_df.head())
