import pandas as pd
import numpy as np


def clean_capstone_data(users, transactions, campaigns, activity):
    """
    Clean the PesaPap capstone datasets.

    Returns
    -------
    clean_tables : dict
        Dictionary containing cleaned users, transactions, campaigns and activity tables.

    cleaning_log : pd.DataFrame
        Table describing each cleaning action and the number of affected rows.
    """

    users = users.copy()
    transactions = transactions.copy()
    campaigns = campaigns.copy()
    activity = activity.copy()

    log = []

    # -----------------------------
    # USERS
    # -----------------------------
    users["signup_date"] = pd.to_datetime(
        users["signup_date"],
        errors="coerce"
    )

    missing_signup = users["signup_date"].isna().sum()

    log.append({
        "table": "users",
        "issue": "Invalid or missing signup dates",
        "action": "Converted signup_date to datetime",
        "rows_affected": int(missing_signup)
    })

    # -----------------------------
    # TRANSACTIONS
    # -----------------------------
    original_rows = len(transactions)

    duplicate_count = transactions.duplicated(
        subset=["txn_id"]
    ).sum()

    transactions = transactions.drop_duplicates(
        subset=["txn_id"]
    ).copy()

    log.append({
        "table": "transactions",
        "issue": "Duplicate transaction IDs",
        "action": "Removed duplicate txn_id rows",
        "rows_affected": int(duplicate_count)
    })

    # Standardise product text
    transactions["product"] = (
        transactions["product"]
        .astype(str)
        .str.strip()
        .str.title()
    )

    log.append({
        "table": "transactions",
        "issue": "Inconsistent product text",
        "action": "Trimmed whitespace and standardised product case",
        "rows_affected": 1
    })

    # Standardise transaction channel
    transactions["channel"] = (
        transactions["channel"]
        .astype(str)
        .str.strip()
        .str.title()
    )

    log.append({
        "table": "transactions",
        "issue": "Inconsistent channel text",
        "action": "Standardised channel case",
        "rows_affected": 1
    })

    # Convert amount to numeric
    transactions["amount"] = pd.to_numeric(
        transactions["amount"],
        errors="coerce"
    )

    missing_amount = transactions["amount"].isna().sum()

    median_amount = transactions.loc[
        transactions["amount"] > 0,
        "amount"
    ].median()

    transactions["amount_imputed"] = transactions["amount"].isna()

    transactions["amount"] = transactions["amount"].fillna(
        median_amount
    )

    log.append({
        "table": "transactions",
        "issue": "Missing transaction amount",
        "action": f"Imputed with positive median amount ({median_amount:.0f})",
        "rows_affected": int(missing_amount)
    })

    # Remove non-positive amounts
    non_positive = (transactions["amount"] <= 0).sum()

    transactions = transactions[
        transactions["amount"] > 0
    ].copy()

    log.append({
        "table": "transactions",
        "issue": "Non-positive transaction amount",
        "action": "Removed rows with amount <= 0",
        "rows_affected": int(non_positive)
    })

    # Parse transaction dates
    transactions["txn_date"] = pd.to_datetime(
        transactions["txn_date"],
        errors="coerce"
    )

    invalid_dates = transactions["txn_date"].isna().sum()

    transactions = transactions[
        transactions["txn_date"].notna()
    ].copy()

    log.append({
        "table": "transactions",
        "issue": "Invalid transaction dates",
        "action": "Parsed dates and removed unparseable rows",
        "rows_affected": int(invalid_dates)
    })

    # Remove transactions before signup
    signup_lookup = users[
        ["user_id", "signup_date"]
    ]

    transactions = transactions.merge(
        signup_lookup,
        on="user_id",
        how="left"
    )

    before_signup = (
        transactions["txn_date"]
        < transactions["signup_date"]
    ).sum()

    transactions = transactions[
        transactions["txn_date"]
        >= transactions["signup_date"]
    ].copy()

    transactions = transactions.drop(
        columns=["signup_date"]
    )

    log.append({
        "table": "transactions",
        "issue": "Transactions before user signup",
        "action": "Removed lifecycle-invalid transactions",
        "rows_affected": int(before_signup)
    })

    # -----------------------------
    # CAMPAIGNS
    # -----------------------------
    campaigns["campaign_month"] = pd.to_datetime(
        campaigns["campaign_month"],
        errors="coerce"
    )

    log.append({
        "table": "campaigns",
        "issue": "Campaign date type",
        "action": "Converted campaign_month to datetime",
        "rows_affected": 0
    })

    # -----------------------------
    # ACTIVITY
    # -----------------------------
    activity["transaction_count"] = pd.to_numeric(
        activity["transaction_count"],
        errors="coerce"
    ).fillna(0).astype(int)

    activity["total_value"] = pd.to_numeric(
        activity["total_value"],
        errors="coerce"
    ).fillna(0)

    activity["active_flag"] = (
        activity["transaction_count"] > 0
    ).astype(int)

    log.append({
        "table": "activity",
        "issue": "Activity field consistency",
        "action": "Standardised numeric fields and recalculated active_flag",
        "rows_affected": 0
    })

    cleaning_log = pd.DataFrame(log)

    clean_tables = {
        "users": users,
        "transactions": transactions,
        "campaigns": campaigns,
        "activity": activity
    }

    return clean_tables, cleaning_log
