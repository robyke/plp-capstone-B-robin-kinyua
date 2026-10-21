# PesaPap Customer Growth, Retention and Value Analytics

## End-to-End Data Analytics Capstone

**Track:** B - Fintech / Mobile Money  
**Author:** Robin Kinyua  
**Programme:** PLP Data Analytics  
**Date:** October 2026

## Project Overview

PesaPap is a simulated fintech and mobile money platform. This capstone analyses customer growth, transaction value, acquisition performance, customer segmentation and retention to support decisions by the Head of Growth.

The project demonstrates an end-to-end analytics workflow covering data generation, data quality auditing, reusable cleaning, exploratory data analysis, SQL, statistical testing, cohort analysis, dashboarding and stakeholder reporting.

## Business Problem

PesaPap has acquired thousands of customers, but the growth team needs to understand which acquisition channels generate the strongest customers, which products and counties contribute the most value, how customer activity changes after signup, and which customer groups should receive retention or reactivation attention.

**Main decision:** Where should PesaPap focus acquisition, retention and customer engagement efforts to improve customer value and long-term activity?

## Key Findings

- Total customers: **8,000**
- Customers with at least one valid transaction: **7,522**
- Ever-active rate: **94.02%**
- Total transactions: **70,824**
- Total transaction value: **KES 111,178,105**
- Average transaction value: **KES 1,569.78**
- Average customer value: **KES 13,897.26**
- Referral generated approximately **KES 29.03 million**
- Send Money generated approximately **KES 32.98 million**
- High Value customers contributed approximately **68.95%** of transaction value
- **478 customers** were inactive

## Statistical Evidence

A Mann-Whitney U test comparing Referral and Social customer value produced:

- U statistic: **1,945,284**
- p-value: **6.24 × 10^-8**

The null hypothesis is rejected at the 0.05 significance level.

Because the dataset is synthetic and the generator intentionally uses slightly different engagement probabilities by acquisition channel, this result demonstrates the analytical method rather than proving a real-world causal relationship.

## Recommendations

1. Prioritise Referral acquisition while measuring acquisition cost and scalability.
2. Protect and reward High Value customers.
3. Target Low Activity customers with engagement campaigns.
4. Develop reactivation campaigns for inactive users.
5. Promote Send Money and test cross-sell opportunities.
6. Explore high-value counties such as Nyeri, Nakuru and Machakos.
7. Introduce lifecycle retention campaigns several months after signup.

## Dashboard

Live Looker Studio dashboard:

https://datastudio.google.com/reporting/88c76eb4-bf90-4299-aa75-db02ccf89b44

Static dashboard image:

`reports/dashboard.png`

## Tools Used

Python, pandas, NumPy, Matplotlib, SciPy, SQLite, SQL, openpyxl, Google Colab, Looker Studio, Excel, Git and GitHub.

## Project Structure

```text
plp-capstone-B-robin-kinyua/
├── README.md
├── requirements.txt
├── .gitignore
├── data/
│   ├── README.md
│   ├── generate_capstone_data.py
│   ├── users.csv
│   ├── transactions.csv
│   ├── campaigns.csv
│   ├── activity.csv
│   └── processed/
│       ├── users_clean.csv
│       ├── transactions_clean.csv
│       ├── campaigns_clean.csv
│       ├── activity_clean.csv
│       └── cleaning_log.csv
├── src/
│   └── cleaning.py
├── notebooks/
│   ├── 01_cleaning.ipynb
│   ├── 02_eda.ipynb
│   └── 03_analysis.ipynb
├── sql/
│   └── queries.sql
└── reports/
    ├── executive_summary.md
    ├── stakeholder_summary.xlsx
    ├── dashboard.png
    ├── dashboard_data.csv
    └── slides.pdf
```

## How to Run

```bash
git clone https://github.com/robyke/plp-capstone-B-robin-kinyua.git
cd plp-capstone-B-robin-kinyua
pip install -r requirements.txt
```

Run the notebooks in this order:

1. `notebooks/01_cleaning.ipynb`
2. `notebooks/02_eda.ipynb`
3. `notebooks/03_analysis.ipynb`

## Reproducibility

The synthetic generator uses random seed `808`.

Verified results:

- Raw transactions: **70,828**
- Clean transactions: **70,824**
- Unique clean transaction IDs: **70,824**
- Total cleaned transaction value: **KES 111,178,105**
- Average transaction value: **KES 1,569.78**

All three notebooks were executed successfully in sequence before submission.

## Ethics and Privacy

The dataset is fully synthetic and contains no real names, phone numbers, email addresses, national identification numbers, account numbers or precise locations.

`user_id` is a pseudonymous synthetic identifier. Individual customer records are not displayed on the published dashboard.

## Limitations

The project uses synthetic data, so findings demonstrate analytical methods rather than actual PesaPap business performance.

The generator intentionally applies different engagement probabilities across acquisition channels, so some channel differences are built into the simulated data.

The project does not include real acquisition costs, profitability, competitor activity or external economic conditions.

The 94.02% active rate represents customers who transacted at least once during the full observation period, not current-month active users.

## Author

**Robin Kinyua**

GitHub: `robyke`