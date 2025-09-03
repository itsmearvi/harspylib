import pandas as pd
from dataclasses import dataclass
from typing import Optional

@dataclass
class SimpleCard:
    name: str
    balance: float
    apr_percent: float
    min_override: Optional[float] = 0.0  # fixed minimum payment
    min_pct: Optional[float] = None       # percentage of balance, e.g., 2% as 0.02

def load_cards_from_csv(path: str):
    df = pd.read_csv(path)
    cards = []
    for _, row in df.iterrows():
        try:
            min_override = float(row["min_override"]) if "min_override" in row and not pd.isna(row["min_override"]) else 0.0
            min_pct = float(row["min_pct"])/100 if "min_pct" in row and not pd.isna(row["min_pct"]) else None
            cards.append(SimpleCard(
                name=str(row["name"]),
                balance=float(row["balance"]),
                apr_percent=float(row["apr_percent"]),
                min_override=min_override,
                min_pct=min_pct
            ))
        except Exception as e:
            print(f"Skipping row due to error: {e}")
    return cards

def compute_monthly_interest(balance, apr_percent):
    return balance * (apr_percent / 100 / 12)

def compute_min_due(c: SimpleCard):
    """Compute min due for a card: min_override > min_pct*balance > 2% fallback, always >=25"""
    if c.min_override and c.min_override > 0:
        return max(25, c.min_override)
    if c.min_pct and c.min_pct > 0:
        return max(25, c.balance * c.min_pct)
    return max(25, c.balance * 0.02)

def plan_multi_card_with_max(cards, max_allowed):
    eps = 0.01
    remaining_cards = [c for c in cards if c.balance > eps]
    schedules = {}
    month_num = 1
    monthly_records = []

    while remaining_cards:
        remaining_cards.sort(key=lambda x: x.apr_percent, reverse=True)
        month_data = {}
        highest_apr_card = remaining_cards[0].name if remaining_cards else None

        # Compute interest and min due
        allocations = {}
        total_non_priority_payment = 0.0
        for i, c in enumerate(remaining_cards):
            interest = compute_monthly_interest(c.balance, c.apr_percent)
            min_due = compute_min_due(c)
            allocations[c.name] = {"interest": interest, "min_due": min_due, "payment": 0.0}

        # Non-priority cards: pay min_due + interest
        for c in remaining_cards[1:]:
            payment = min(allocations[c.name]["min_due"] + allocations[c.name]["interest"], c.balance + allocations[c.name]["interest"])
            allocations[c.name]["payment"] = payment
            total_non_priority_payment += payment

        # Priority card: highest APR gets remaining
        priority_card = remaining_cards[0]
        remaining_budget = max_allowed - total_non_priority_payment
        payment_priority = min(priority_card.balance + allocations[priority_card.name]["interest"], max(remaining_budget, 0.0))
        allocations[priority_card.name]["payment"] = payment_priority

        # Apply payments and update balances
        for c in remaining_cards:
            interest = allocations[c.name]["interest"]
            payment = allocations[c.name]["payment"]
            min_due = allocations[c.name]["min_due"]
            new_bal = c.balance + interest - payment
            month_data[c.name] = {
                "Month": month_num,
                "Card": c.name,
                "Curr_Bal": round(c.balance,2),
                "Interest": round(interest,2),
                "Min_Due": round(min_due,2),
                "Actual_Payment": round(payment,2),
                "New_Bal": round(max(new_bal,0),2),
                "Highest_APR": c.name == highest_apr_card
            }
            c.balance = new_bal

        monthly_records.append({k:v for k,v in month_data.items()})
        month_num += 1
        remaining_cards = [c for c in remaining_cards if c.balance > eps]

    # Build per-card schedules
    card_names = [c.name for c in cards]
    for name in card_names:
        rows = [m[name] for m in monthly_records if name in m]
        schedules[name] = pd.DataFrame(rows)

    # Monthly allocation summary
    monthly_summary = pd.DataFrame([
        {"Month": m, **{k: v["Actual_Payment"] for k,v in month.items()}}
        for m, month in enumerate(monthly_records, start=1)
    ]).fillna(0)

    return schedules, monthly_summary

def generate_summary(schedules, start_date=None):
    summary = []
    for name, df in schedules.items():
        if df.empty:
            continue
        opening_balance = df["Curr_Bal"].iloc[0]
        total_interest = df["Interest"].sum()
        total_tenure = df["Month"].max()
        if start_date is not None:
            start_payment = pd.to_datetime(start_date) + pd.DateOffset(months=int(df["Month"].iloc[0]-1))
            end_payment = pd.to_datetime(start_date) + pd.DateOffset(months=int(df["Month"].iloc[-1]-1))
        else:
            start_payment = f"Month {df['Month'].iloc[0]}"
            end_payment = f"Month {df['Month'].iloc[-1]}"
        summary.append({
            "Card": name,
            "Opening_Balance": round(opening_balance,2),
            "Total_Interest": round(total_interest,2),
            "Total_Tenure_Months": total_tenure,
            "Start_Payment": start_payment,
            "End_Payment": end_payment
        })
    return pd.DataFrame(summary)
