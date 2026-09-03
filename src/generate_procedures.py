import random

import pandas as pd


random.seed(42)

PROCEDURES = [
    ("99213", "Established Patient Office Visit"),
    ("99214", "Established Patient Office Visit - Moderate"),
    ("99223", "Initial Hospital Care"),
    ("99233", "Subsequent Hospital Care"),
    ("93000", "Electrocardiogram"),
    ("71046", "Chest X-Ray"),
    ("80053", "Comprehensive Metabolic Panel"),
    ("85025", "Complete Blood Count"),
    ("36415", "Blood Collection"),
    ("93306", "Echocardiogram"),
    ("74177", "CT Abdomen and Pelvis"),
    ("70450", "CT Head"),
    ("73721", "MRI Joint"),
    ("45378", "Diagnostic Colonoscopy"),
    ("29881", "Knee Arthroscopy"),
]


def generate_procedures(encounter_ids: list[int]) -> pd.DataFrame:
    """Generate synthetic procedures for healthcare encounters."""

    procedures = []

    procedure_id = 1

    for encounter_id in encounter_ids:
        # Each encounter receives between 0 and 3 procedures.
        num_procedures = random.randint(0, 3)

        if num_procedures == 0:
            continue

        selected_procedures = random.sample(
            PROCEDURES,
            num_procedures,
        )

        for procedure_code, procedure_name in selected_procedures:
            procedures.append(
                {
                    "procedure_id": procedure_id,
                    "encounter_id": encounter_id,
                    "procedure_code": procedure_code,
                    "procedure_name": procedure_name,
                }
            )

            procedure_id += 1

    return pd.DataFrame(procedures)


if __name__ == "__main__":
    encounters_df = pd.read_csv("data/encounters.csv")

    procedures_df = generate_procedures(
        encounters_df["encounter_id"].tolist()
    )

    output_path = "data/procedures.csv"

    procedures_df.to_csv(output_path, index=False)

    print(f"Generated {len(procedures_df)} synthetic procedure records.")
    print(f"Saved to: {output_path}")
    print()
    print(procedures_df.head())
