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
            min_override = float(row["Min_Override"]) if "Min_Override" in row and not pd.isna(row["Min_Override"]) else 0.0
            min_pct = float(row["Min_Pct"])/100 if "Min_Pct" in row and not pd.isna(row["Min_Pct"]) else None
            cards.append(SimpleCard(
                name=str(row["Card"]),
                balance=float(row["Balance"]),
                apr_percent=float(row["APR"]),
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

    # CODE FIX TWO BELOW
    """
    Allocate payments across cards each month:
      - Compute per-card base payment:
          * if min_override > 0  -> base = max(25, min_override)  (NO + interest)
          * else                 -> base = max(25, min_pct*balance or 2%*balance) + interest
        (each base is capped at balance + interest)
      - baseline = sum(base for all cards)
      - budget = max(user max_allowed, baseline)
      - Distribute extra = budget - baseline to cards in APR-desc order (avalanche),
        capping each at (balance + interest).
    """
    eps = 0.01
    schedules = {}
    month_num = 1
    monthly_records = []
    # Work on a live list of cards
    remaining_cards = [c for c in cards if c.balance > eps]

    while remaining_cards:
        # Sort by APR (desc) for avalanche
        cards_sorted = sorted(remaining_cards, key=lambda c: c.apr_percent, reverse=True)
        highest_apr_card = cards_sorted[0].name if cards_sorted else None

        # ---- Per-card month calcs (interest, min_due, base, cap) ----
        calc = []
        for c in cards_sorted:
            interest = compute_monthly_interest(c.balance, c.apr_percent)
            min_due = compute_min_due(c)  # returns override or pct/2% floor (>=25)

            # Base payment rule:
            if c.min_override and c.min_override > 0:
                # Fixed minimum; do NOT add interest on top
                base = min_due
            else:
                # Percentage-based min; pay min + interest
                base = min_due + interest

            cap = max(0.0, c.balance + interest)  # can't pay more than balance+interest
            base = min(base, cap)                 # cap the base at payoff

            calc.append({
                "card": c,
                "interest": interest,
                "min_due": min_due,
                "base": base,
                "cap": cap,
                "payment": base  # start at base; may add extra below
            })

        # ---- Budget & extra ----
        baseline = sum(item["base"] for item in calc)
        budget = max(float(max_allowed), baseline)  # raise to at least meet all minima
        extra = budget - baseline                   # only this extra is spread to highest APR first

        # ---- Distribute extra in APR order (avalanche), honoring each cap ----
        for item in calc:
            if extra <= 1e-9:
                break
            room = item["cap"] - item["payment"]
            if room <= 0:
                continue
            add = min(extra, room)
            item["payment"] += add
            extra -= add

        # ---- Post payments: compute new balances & record month ----
        month_data = {}
        for item in calc:
            c = item["card"]
            pay = item["payment"]
            interest = item["interest"]
            new_bal = c.balance + interest - pay

            month_data[c.name] = {
                "Month": month_num,
                "Card": c.name,
                "Curr_Bal": round(c.balance, 2),
                "Interest": round(interest, 2),
                "Min_Due": round(item["min_due"], 2),
                "Actual_Payment": round(pay, 2),
                "New_Bal": round(max(new_bal, 0.0), 2),
                "Highest_APR": (c.name == highest_apr_card),
            }
            c.balance = new_bal

        monthly_records.append(month_data)
        month_num += 1
        remaining_cards = [c for c in cards_sorted if c.balance > eps]

    # ---- Build per-card schedules ----
    card_names = [c.name for c in cards]
    for name in card_names:
        rows = [m[name] for m in monthly_records if name in m]
        schedules[name] = pd.DataFrame(rows)

    # ---- Build monthly allocation summary (same columns every month) ----
    summary_rows = []
    for i, month in enumerate(monthly_records, start=1):
        row = {"Month": i}
        for name in card_names:
            row[name] = month.get(name, {}).get("Actual_Payment", 0.0)
        summary_rows.append(row)
    monthly_summary = pd.DataFrame(summary_rows)

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
