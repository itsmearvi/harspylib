import argparse
import os
import pandas as pd
from amort_allocator import load_cards_from_csv, plan_multi_card_with_max, generate_summary

def main():
    parser = argparse.ArgumentParser(description="Credit Card Amortization CLI")
    parser.add_argument("--cards", required=True, help="Path to cards.csv")
    parser.add_argument("--max", required=True, type=float, help="Max allowed monthly payment")
    parser.add_argument("--outdir", default=".", help="Output directory for CSV/Excel files")
    args = parser.parse_args()

    if not os.path.exists(args.cards):
        print(f"Error: CSV file not found: {args.cards}")
        return

    os.makedirs(args.outdir, exist_ok=True)

    cards = load_cards_from_csv(args.cards)
    if not cards:
        print("No valid cards found in CSV.")
        return

    # Compute schedules
    schedules, monthly_summary = plan_multi_card_with_max(cards, args.max)

    # Save per-card CSVs
    for name, df in schedules.items():
        df.to_csv(os.path.join(args.outdir, f"{name}_schedule.csv"), index=False)

    # Save monthly summary CSV
    monthly_csv_path = os.path.join(args.outdir, "monthly_allocation.csv")
    monthly_summary.to_csv(monthly_csv_path, index=False)

    # Save Excel workbook
    excel_path = os.path.join(args.outdir, "schedules.xlsx")
    with pd.ExcelWriter(excel_path) as writer:
        monthly_summary.to_excel(writer, sheet_name="Summary", index=False)
        for name, df in schedules.items():
            df.to_excel(writer, sheet_name=name, index=False)

    # Generate and save summary
    summary_df = generate_summary(schedules)
    summary_csv_path = os.path.join(args.outdir, "summary.csv")
    summary_df.to_csv(summary_csv_path, index=False)

    # Console outputs
    print("\n✅ Card Summary:")
    print(summary_df.to_string(index=False))
    print(f"\nMonthly allocation CSV: {monthly_csv_path}")
    print(f"Excel workbook: {excel_path}")
    print(f"Per-card CSVs saved in: {args.outdir}")
    print(f"Summary CSV: {summary_csv_path}")

if __name__ == "__main__":
    main()
