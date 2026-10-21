# PesaPap Capstone Data

## Data Source

This project uses a synthetic PesaPap fintech dataset generated specifically for the PLP Data Analytics capstone using `generate_capstone_data.py`.

No external customer dataset was used.

The generator uses a fixed random seed of `808` to support reproducibility.

## Licence

This dataset is project-generated synthetic educational data. No external dataset licence applies.

## Date Created / Accessed

October 2026

## Analysis Period

July 2025 through June 2026.

## Tables

### users.csv

Grain: one row per synthetic user.

Primary key: `user_id`

### transactions.csv

Grain: one row per transaction.

Primary key: `txn_id`

Foreign key: `user_id` references `users.user_id`.

### campaigns.csv

Grain: one row per monthly synthetic marketing campaign.

Primary key: `campaign_id`

### activity.csv

Grain: one row per user.

Fields:

- `user_id`
- `transaction_count`
- `total_value`
- `active_flag`

## Controlled Data Quality Issues

The raw synthetic transaction table intentionally includes a small number of quality problems so the project can demonstrate a reproducible cleaning process.

These include:

- duplicate transaction IDs
- inconsistent product formatting
- inconsistent channel formatting
- a missing transaction amount
- a non-positive transaction amount
- a transaction occurring before signup

The final cleaned transaction table contains 70,824 unique valid transactions.

## Ethics and Privacy Statement

The dataset is fully synthetic and does not represent real PesaPap customers.

It contains no real names, phone numbers, email addresses, national identification numbers, account numbers or precise locations.

`user_id` is a pseudonymous synthetic identifier.

The public dashboard presents aggregate results and does not expose individual customer records.

## Important Synthetic-Data Limitation

The generator intentionally applies slightly different engagement probabilities by acquisition channel to create a realistic analytical scenario.

Therefore, observed acquisition-channel differences should be interpreted as simulated patterns and not as evidence about a real fintech business.