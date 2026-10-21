
import numpy as np
import pandas as pd

rng = np.random.default_rng(808)

# =========================================================
# USERS TABLE
# =========================================================

n_users = 8000

analysis_start = pd.Timestamp("2025-07-01")
analysis_end = pd.Timestamp("2026-06-30")

users = pd.DataFrame({
    "user_id": range(1, n_users + 1),
    "signup_date": (
        analysis_start
        + pd.to_timedelta(
            rng.integers(0, 365, n_users),
            unit="D"
        )
    ),
    "county": rng.choice(
        [
            "Nairobi",
            "Mombasa",
            "Kisumu",
            "Nakuru",
            "Eldoret",
            "Machakos",
            "Nyeri"
        ],
        n_users,
        p=[0.30, 0.15, 0.12, 0.12, 0.10, 0.11, 0.10]
    ),
    "acquisition_channel": rng.choice(
        [
            "Referral",
            "Social",
            "Agent",
            "Search",
            "Partnership"
        ],
        n_users,
        p=[0.24, 0.23, 0.20, 0.18, 0.15]
    ),
    "age_band": rng.choice(
        [
            "18-24",
            "25-34",
            "35-44",
            "45-54",
            "55+"
        ],
        n_users,
        p=[0.22, 0.36, 0.22, 0.13, 0.07]
    )
})

# =========================================================
# TRANSACTIONS TABLE
# =========================================================

# Reset the RNG before transaction generation so the
# transaction dataset exactly reproduces the capstone analysis.
rng = np.random.default_rng(808)

channel_multiplier = {
    "Referral": 1.08,
    "Search": 1.04,
    "Agent": 1.00,
    "Partnership": 0.97,
    "Social": 0.93
}

records = []
txn_id = 1

for row in users.itertuples(index=False):

    signup_date = row.signup_date
    signup_month = signup_date.to_period("M")
    final_month = analysis_end.to_period("M")

    months = pd.period_range(
        signup_month,
        final_month,
        freq="M"
    )

    multiplier = channel_multiplier.get(
        row.acquisition_channel,
        1.0
    )

    for month_number, month in enumerate(months):

        base_active_probability = max(
            0.28,
            0.62 * (0.94 ** month_number)
        )

        active_probability = min(
            base_active_probability * multiplier,
            0.90
        )

        if rng.random() > active_probability:
            continue

        number_of_transactions = rng.poisson(1.7) + 1

        month_start = month.start_time
        month_end = month.end_time.normalize()

        valid_start = max(
            signup_date,
            month_start
        )

        valid_end = min(
            analysis_end,
            month_end
        )

        available_days = (
            valid_end - valid_start
        ).days

        if available_days < 0:
            continue

        for _ in range(number_of_transactions):

            random_day = rng.integers(
                0,
                available_days + 1
            )

            txn_date = (
                valid_start
                + pd.Timedelta(
                    days=int(random_day)
                )
            )

            records.append({
                "txn_id": txn_id,
                "user_id": row.user_id,
                "txn_date": txn_date,
                "product": rng.choice(
                    [
                        "Airtime",
                        "Bill Pay",
                        "Send Money",
                        "Merchant Pay",
                        "Savings"
                    ],
                    p=[0.24, 0.18, 0.30, 0.18, 0.10]
                ),
                "amount": round(
                    rng.lognormal(
                        mean=6.9,
                        sigma=0.95
                    ),
                    0
                ),
                "channel": rng.choice(
                    ["App", "USSD", "Agent"],
                    p=[0.58, 0.27, 0.15]
                )
            })

            txn_id += 1

transactions = pd.DataFrame(records)

# =========================================================
# CAMPAIGNS TABLE
# =========================================================

campaigns = pd.DataFrame({
    "campaign_id": range(1, 13),
    "campaign_month": pd.date_range(
        "2025-07-01",
        periods=12,
        freq="MS"
    ),
    "campaign_type": [
        "Referral Bonus",
        "Cashback",
        "Bill Pay Promo",
        "Merchant Discount",
        "Referral Bonus",
        "Savings Push",
        "Cashback",
        "Agent Activation",
        "Merchant Discount",
        "Savings Push",
        "Bill Pay Promo",
        "Referral Bonus"
    ],
    "marketing_spend": rng.integers(
        250000,
        900000,
        12
    ),
    "new_users_acquired": rng.integers(
        300,
        1200,
        12
    )
})

# =========================================================
# ACTIVITY TABLE
# =========================================================

activity = (
    transactions
    .groupby("user_id")
    .agg(
        transaction_count=("txn_id", "count"),
        total_value=("amount", "sum")
    )
    .reset_index()
)

activity = users[["user_id"]].merge(
    activity,
    on="user_id",
    how="left"
)

activity["transaction_count"] = (
    activity["transaction_count"]
    .fillna(0)
    .astype(int)
)

activity["total_value"] = (
    activity["total_value"]
    .fillna(0)
)

activity["active_flag"] = (
    activity["transaction_count"] > 0
).astype(int)

# =========================================================
# CONTROLLED DATA QUALITY ISSUES
# =========================================================

transactions.loc[15, "amount"] = np.nan
transactions.loc[85, "amount"] = -500
transactions.loc[120, "product"] = " send money "
transactions.loc[220, "channel"] = "app"

bad_user = transactions.loc[350, "user_id"]

bad_signup = users.loc[
    users["user_id"] == bad_user,
    "signup_date"
].iloc[0]

transactions.loc[
    350,
    "txn_date"
] = bad_signup - pd.Timedelta(days=30)

duplicate_rows = transactions.iloc[
    [50, 100]
].copy()

transactions = pd.concat(
    [transactions, duplicate_rows],
    ignore_index=True
)

# =========================================================
# FORMAT DATES
# =========================================================

users["signup_date"] = (
    users["signup_date"]
    .dt.strftime("%Y-%m-%d")
)

transactions["txn_date"] = (
    pd.to_datetime(
        transactions["txn_date"]
    )
    .dt.strftime("%Y-%m-%d")
)

campaigns["campaign_month"] = (
    campaigns["campaign_month"]
    .dt.strftime("%Y-%m-%d")
)

# =========================================================
# SAVE FILES
# =========================================================

users.to_csv("data/users.csv", index=False)
transactions.to_csv("data/transactions.csv", index=False)
campaigns.to_csv("data/campaigns.csv", index=False)
activity.to_csv("data/activity.csv", index=False)

print("Generated datasets:")
print("users.csv:", users.shape)
print("transactions.csv:", transactions.shape)
print("campaigns.csv:", campaigns.shape)
print("activity.csv:", activity.shape)
