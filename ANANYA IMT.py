import pandas as pd
import statsmodels.formula.api as smf

file = r"C:\Users\HP\Downloads\01_01_06_Consumer_Behaviour_tiktok_marketing_synthetic_data.xlsx"
df = pd.read_excel(file)

# H1: Funny content captures user attention
h1 = smf.ols("attention ~ funny_content", data=df).fit()
print("\nH1: Funny content captures attention")
print(h1.summary())

# H3a: Funny content captures more attention among new consumers
h3a = smf.ols("attention ~ funny_content * new_consumer", data=df).fit()
print("\nH3a: Funny content effect is stronger for new consumers")
print(h3a.summary())

# H2 + H3b:
# Attention increases outcomes; effects are stronger for new consumers
for outcome in ["likes", "shares", "purchase_intention"]:
    model = smf.ols(
        f"{outcome} ~ attention * new_consumer + funny_content",
        data=df
    ).fit()

    print(f"\nOutcome model: {outcome}")
    print(model.summary())