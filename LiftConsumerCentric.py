import pandas as pd

from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression

# --------------------------------------------------
# STEP 1: LOAD DATA
# --------------------------------------------------

df = pd.read_csv(r"C:\Users\HP\Downloads\lift_synthetic_email_campaign_customers.csv")

print("\nFirst 5 rows:")
print(df.head())

print("\nDataset shape:")
print(df.shape)

# --------------------------------------------------
# STEP 2: SPLIT TREATMENT AND CONTROL GROUPS
# --------------------------------------------------

treated = df[df["email_sent"] == 1]
control = df[df["email_sent"] == 0]

print("\nTreated customers:", len(treated))
print("Control customers:", len(control))

# --------------------------------------------------
# STEP 3: SELECT FEATURES
# --------------------------------------------------

features = [
    "age",
    "purchases_last_year",
    "website_visits_last_month",  # <--- Updated name!
    "loyalty_score"
]

# --------------------------------------------------
# STEP 4: BUILD MODEL FOR TREATED CUSTOMERS
# --------------------------------------------------

X_treated = treated[features]
y_treated = treated["purchased"]

model_treated = LogisticRegression(max_iter=1000)

model_treated.fit(X_treated, y_treated)

# --------------------------------------------------
# STEP 5: BUILD MODEL FOR CONTROL CUSTOMERS
# --------------------------------------------------

X_control = control[features]
y_control = control["purchased"]

model_control = LogisticRegression(max_iter=1000)

model_control.fit(X_control, y_control)

# --------------------------------------------------
# STEP 6: PREDICT FOR ALL CUSTOMERS
# --------------------------------------------------

X_all = df[features]

p_treated = model_treated.predict_proba(X_all)[:, 1]

p_control = model_control.predict_proba(X_all)[:, 1]

# --------------------------------------------------
# STEP 7: CALCULATE UPLIFT
# --------------------------------------------------

df["predicted_if_treated"] = p_treated
df["predicted_if_not_treated"] = p_control

df["uplift"] = (
        df["predicted_if_treated"]
        - df["predicted_if_not_treated"]
)

# --------------------------------------------------
# STEP 8: SORT BY UPLIFT
# --------------------------------------------------

results = df.sort_values(
    by="uplift",
    ascending=False
)

print("\nTop 20 customers by uplift:")
print(
    results[
        [
            "customer_id",
            "predicted_if_treated",
            "predicted_if_not_treated",
            "uplift"
        ]
    ].head(20)
)

# --------------------------------------------------
# STEP 9: SAVE RESULTS
# --------------------------------------------------

results.to_csv(
    "lift_uplift_model_results.csv",
    index=False
)

print("\nResults saved as:")
print("lift_uplift_model_results.csv")