import random

import pandas as pd


random.seed(42)

NUM_PROVIDERS = 100

SPECIALTIES = [
    "Primary Care",
    "Cardiology",
    "Orthopedics",
    "Emergency Medicine",
    "Oncology",
    "Neurology",
    "Pediatrics",
    "General Surgery",
    "Dermatology",
    "Gastroenterology",
]


def generate_providers(num_providers: int) -> pd.DataFrame:
    """Generate synthetic healthcare providers."""

    providers = []

    for provider_id in range(1, num_providers + 1):
        providers.append(
            {
                "provider_id": provider_id,
                "provider_name": f"Provider {provider_id:03d}",
                "specialty": random.choice(SPECIALTIES),
            }
        )

    return pd.DataFrame(providers)


if __name__ == "__main__":
    providers_df = generate_providers(NUM_PROVIDERS)

    output_path = "data/providers.csv"

    providers_df.to_csv(output_path, index=False)

    print(f"Generated {len(providers_df)} synthetic providers.")
    print(f"Saved to: {output_path}")
    print()
    print(providers_df.head())
