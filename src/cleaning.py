import pandas as pd
import numpy as np


def clean_capstone_data(users, transactions, campaigns, activity):
    """
    Clean the PesaPap capstone datasets.

    Parameters
    ----------
    users : pd.DataFrame
        Raw users table.
    transactions : pd.DataFrame
        Raw transactions table.
    campaigns : pd.DataFrame
        Raw campaigns table.
    activity : pd.DataFrame
        Raw activity table.

    Returns
    -------
    clean_tables : dict
        Dictionary containing cleaned users, transactions,
        campaigns and activity tables.

    cleaning_log : pd.DataFrame
        Table describing each cleaning issue, action taken,
        and number of rows affected.
    """

    users = users.copy()
    transactions = transactions.copy()
    campaigns = campaigns.copy()
    activity = activity.copy()

    log = []

    # =========================================================
    # USERS
    # =========================================================

    duplicate_users = users.duplicated(
        subset=["user_id"]
    ).sum()

    users = users.drop_duplicates(
        subset=["user_id"]
    ).copy()

    log.append({
        "table": "users",
        "issue": "Duplicate user IDs",
        "action": "Removed duplicate user_id rows",
        "rows_affected": int(duplicate_users)
    })

    users["signup_date"] = pd.to_datetime(
        users["signup_date"],
        errors="coerce"
    )

    invalid_signup_dates = users[
        "signup_date"
    ].isna().sum()

    users = users[
        users["signup_date"].notna()
    ].copy()

    log.append({
        "table": "users",
        "issue": "Invalid or missing signup dates",
        "action": "Converted signup_date to datetime and removed invalid rows",
        "rows_affected": int(invalid_signup_dates)
    })

    for column in [
        "county",
        "gender",
        "acquisition_channel"
    ]:
        if column in users.columns:

            before = users[column].copy()

            users[column] = (
                users[column]
                .astype(str)
                .str.strip()
                .str.title()
            )

            changed = (
                before.astype(str)
                != users[column].astype(str)
            ).sum()

            log.append({
                "table": "users",
                "issue": f"Inconsistent {column} text",
                "action": f"Trimmed whitespace and standardised {column} case",
                "rows_affected": int(changed)
            })

    # =========================================================
    # TRANSACTIONS
    # =========================================================

    duplicate_transactions = transactions.duplicated(
        subset=["txn_id"]
    ).sum()

    transactions = transactions.drop_duplicates(
        subset=["txn_id"]
    ).copy()

    log.append({
        "table": "transactions",
        "issue": "Duplicate transaction IDs",
        "action": "Removed duplicate txn_id rows",
        "rows_affected": int(duplicate_transactions)
    })

    before_product = transactions["product"].copy()

    transactions["product"] = (
        transactions["product"]
        .astype(str)
        .str.strip()
        .str.title()
    )

    product_changes = (
        before_product.astype(str)
        != transactions["product"].astype(str)
    ).sum()

    log.append({
        "table": "transactions",
        "issue": "Inconsistent product text",
        "action": "Trimmed whitespace and standardised product case",
        "rows_affected": int(product_changes)
    })

    before_channel = transactions["channel"].copy()

    transactions["channel"] = (
        transactions["channel"]
        .astype(str)
        .str.strip()
        .str.title()
    )

    channel_changes = (
        before_channel.astype(str)
        != transactions["channel"].astype(str)
    ).sum()

    log.append({
        "table": "transactions",
        "issue": "Inconsistent channel text",
        "action": "Trimmed whitespace and standardised channel case",
        "rows_affected": int(channel_changes)
    })

    transactions["amount"] = pd.to_numeric(
        transactions["amount"],
        errors="coerce"
    )

    missing_amounts = transactions[
        "amount"
    ].isna().sum()

    median_amount = transactions.loc[
        transactions["amount"] > 0,
        "amount"
    ].median()

    transactions["amount_imputed"] = (
        transactions["amount"].isna()
    )

    transactions["amount"] = (
        transactions["amount"]
        .fillna(median_amount)
    )

    log.append({
        "table": "transactions",
        "issue": "Missing or invalid transaction amount",
        "action": (
            f"Imputed missing amounts using positive median "
            f"({median_amount:.2f})"
        ),
        "rows_affected": int(missing_amounts)
    })

    non_positive_amounts = (
        transactions["amount"] <= 0
    ).sum()

    transactions = transactions[
        transactions["amount"] > 0
    ].copy()

    log.append({
        "table": "transactions",
        "issue": "Non-positive transaction amount",
        "action": "Removed rows with amount <= 0",
        "rows_affected": int(non_positive_amounts)
    })

    transactions["txn_date"] = pd.to_datetime(
        transactions["txn_date"],
        errors="coerce"
    )

    invalid_transaction_dates = transactions[
        "txn_date"
    ].isna().sum()

    transactions = transactions[
        transactions["txn_date"].notna()
    ].copy()

    log.append({
        "table": "transactions",
        "issue": "Invalid transaction dates",
        "action": "Parsed txn_date and removed unparseable rows",
        "rows_affected": int(invalid_transaction_dates)
    })

    valid_user_ids = set(users["user_id"])

    unknown_users = (
        ~transactions["user_id"].isin(valid_user_ids)
    ).sum()

    transactions = transactions[
        transactions["user_id"].isin(valid_user_ids)
    ].copy()

    log.append({
        "table": "transactions",
        "issue": "Transactions linked to unknown users",
        "action": "Removed transactions without a valid user_id",
        "rows_affected": int(unknown_users)
    })

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

    # =========================================================
    # CAMPAIGNS
    # =========================================================

    if "campaign_id" in campaigns.columns:
        duplicate_campaigns = campaigns.duplicated(
            subset=["campaign_id"]
        ).sum()

        campaigns = campaigns.drop_duplicates(
            subset=["campaign_id"]
        ).copy()

        log.append({
            "table": "campaigns",
            "issue": "Duplicate campaign IDs",
            "action": "Removed duplicate campaign_id rows",
            "rows_affected": int(duplicate_campaigns)
        })

    campaigns["campaign_month"] = pd.to_datetime(
        campaigns["campaign_month"],
        errors="coerce"
    )

    invalid_campaign_dates = campaigns[
        "campaign_month"
    ].isna().sum()

    campaigns = campaigns[
        campaigns["campaign_month"].notna()
    ].copy()

    log.append({
        "table": "campaigns",
        "issue": "Invalid campaign dates",
        "action": "Converted campaign_month to datetime and removed invalid rows",
        "rows_affected": int(invalid_campaign_dates)
    })

    if "campaign_type" in campaigns.columns:

        before_campaign_type = campaigns[
            "campaign_type"
        ].copy()

        campaigns["campaign_type"] = (
            campaigns["campaign_type"]
            .astype(str)
            .str.strip()
            .str.title()
        )

        campaign_type_changes = (
            before_campaign_type.astype(str)
            != campaigns["campaign_type"].astype(str)
        ).sum()

        log.append({
            "table": "campaigns",
            "issue": "Inconsistent campaign type text",
            "action": "Trimmed whitespace and standardised campaign type case",
            "rows_affected": int(campaign_type_changes)
        })

    # =========================================================
    # ACTIVITY
    # =========================================================

    duplicate_activity = activity.duplicated(
        subset=["user_id"]
    ).sum()

    activity = activity.drop_duplicates(
        subset=["user_id"]
    ).copy()

    log.append({
        "table": "activity",
        "issue": "Duplicate activity user IDs",
        "action": "Removed duplicate user_id rows",
        "rows_affected": int(duplicate_activity)
    })

    original_transaction_count = activity[
        "transaction_count"
    ].copy()

    activity["transaction_count"] = pd.to_numeric(
        activity["transaction_count"],
        errors="coerce"
    ).fillna(0).astype(int)

    transaction_count_changes = (
        original_transaction_count.astype(str)
        != activity["transaction_count"].astype(str)
    ).sum()

    original_total_value = activity[
        "total_value"
    ].copy()

    activity["total_value"] = pd.to_numeric(
        activity["total_value"],
        errors="coerce"
    ).fillna(0)

    total_value_changes = (
        original_total_value.astype(str)
        != activity["total_value"].astype(str)
    ).sum()

    activity["active_flag"] = (
        activity["transaction_count"] > 0
    ).astype(int)

    log.append({
        "table": "activity",
        "issue": "Activity field consistency",
        "action": (
            "Standardised transaction_count and total_value "
            "and recalculated active_flag"
        ),
        "rows_affected": int(
            transaction_count_changes
            + total_value_changes
        )
    })

    # =========================================================
    # FINAL OUTPUT
    # =========================================================

    cleaning_log = pd.DataFrame(log)

    clean_tables = {
        "users": users.reset_index(drop=True),
        "transactions": transactions.reset_index(drop=True),
        "campaigns": campaigns.reset_index(drop=True),
        "activity": activity.reset_index(drop=True)
    }

    return clean_tables, cleaning_log
