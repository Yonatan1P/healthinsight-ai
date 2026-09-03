import random

import pandas as pd


random.seed(42)

DIAGNOSES = [
    ("I10", "Hypertension"),
    ("E11.9", "Type 2 Diabetes"),
    ("E78.5", "Hyperlipidemia"),
    ("I25.10", "Coronary Artery Disease"),
    ("J18.9", "Pneumonia"),
    ("J44.9", "Chronic Obstructive Pulmonary Disease"),
    ("M54.5", "Low Back Pain"),
    ("M17.9", "Osteoarthritis"),
    ("G43.909", "Migraine"),
    ("K21.9", "Gastroesophageal Reflux Disease"),
    ("N18.3", "Chronic Kidney Disease"),
    ("F32.9", "Depressive Disorder"),
    ("C50.919", "Breast Cancer"),
    ("C61", "Prostate Cancer"),
    ("J45.909", "Asthma"),
]


def generate_diagnoses(encounter_ids: list[int]) -> pd.DataFrame:
    """Generate synthetic diagnoses for healthcare encounters."""

    diagnoses = []

    diagnosis_id = 1

    for encounter_id in encounter_ids:
        # Each encounter receives between 1 and 3 diagnoses.
        num_diagnoses = random.randint(1, 3)

        selected_diagnoses = random.sample(
            DIAGNOSES,
            num_diagnoses,
        )

        for diagnosis_code, diagnosis_name in selected_diagnoses:
            diagnoses.append(
                {
                    "diagnosis_id": diagnosis_id,
                    "encounter_id": encounter_id,
                    "diagnosis_code": diagnosis_code,
                    "diagnosis_name": diagnosis_name,
                }
            )

            diagnosis_id += 1

    return pd.DataFrame(diagnoses)


if __name__ == "__main__":
    encounters_df = pd.read_csv("data/encounters.csv")

    diagnoses_df = generate_diagnoses(
        encounters_df["encounter_id"].tolist()
    )

    output_path = "data/diagnoses.csv"

    diagnoses_df.to_csv(output_path, index=False)

    print(f"Generated {len(diagnoses_df)} synthetic diagnosis records.")
    print(f"Saved to: {output_path}")
    print()
    print(diagnoses_df.head())
