import gradio as gr
import pandas as pd
import tempfile, os
import plotly.express as px
from amort_allocator import load_cards_from_csv, plan_multi_card_with_max, generate_summary
from typing import Any

# --- Cache previous inputs/outputs ---
if "prev_inputs" not in globals():
    prev_inputs: dict[str, Any] = {
        "file_path": None,
        "max_allowed": None,
        "schedules": None,
        "monthly": None,
        "monthly_csv": None,
        "excel_path": None,
        "summary_df": None,
        "summary_csv": None,
        "fig": None
    }

def compute_from_csv(file_path, max_allowed):
    global prev_inputs

    if file_path is None:
        return "Upload CSV", None, None, None, None, None, None

    # Recompute only if file or max_allowed changed
    recompute = (prev_inputs["file_path"] != file_path) or (prev_inputs["max_allowed"] != max_allowed)

    if not recompute and prev_inputs["schedules"] is not None:
        return ("Schedules already computed!",
                prev_inputs["monthly"],
                prev_inputs["monthly_csv"],
                prev_inputs["excel_path"],
                prev_inputs["fig"],
                prev_inputs["summary_df"],
                prev_inputs["summary_csv"])

    # Load cards
    cards = load_cards_from_csv(file_path)
    if not cards:
        return "No valid cards found", None, None, None, None, None, None

    # Compute schedules
    schedules, monthly = plan_multi_card_with_max(cards, float(max_allowed))

    # Temporary directory for outputs
    tmpdir = tempfile.mkdtemp()
    monthly_csv = os.path.join(tmpdir, "monthly_allocation.csv")
    excel_path = os.path.join(tmpdir, "schedules.xlsx")
    monthly.to_csv(monthly_csv, index=False)

    # Excel workbook with per-card sheets
    with pd.ExcelWriter(excel_path) as writer:
        monthly.to_excel(writer, sheet_name="Summary", index=False)
        for name, df in schedules.items():
            df.to_excel(writer, sheet_name=name, index=False)

    # Generate summary
    summary_df = generate_summary(schedules)
    summary_csv = os.path.join(tmpdir, "summary.csv")
    summary_df.to_csv(summary_csv, index=False)

    # Interactive balance chart using Plotly
    valid_schedules = {name: df for name, df in schedules.items() if "New_Bal" in df.columns}
    all_months = sorted({month for df in valid_schedules.values() for month in df["Month"]})
    aligned_balances = {name: df.set_index("Month").reindex(all_months)["New_Bal"].fillna(0)
                        for name, df in valid_schedules.items()}
    balances_df = pd.DataFrame(aligned_balances)
    balances_df.index.name = "Month"
    balances_df_reset = balances_df.reset_index().melt(id_vars="Month", var_name="Card", value_name="Balance")
    fig = px.line(balances_df_reset, x="Month", y="Balance", color="Card", markers=True,
                  title="Remaining Balances Over Time")

    # Cache results
    prev_inputs.update({
        "file_path": file_path,
        "max_allowed": max_allowed,
        "schedules": schedules,
        "monthly": monthly,
        "monthly_csv": monthly_csv,
        "excel_path": excel_path,
        "summary_df": summary_df,
        "summary_csv": summary_csv,
        "fig": fig
    })

    return "Schedules computed!", monthly, monthly_csv, excel_path, fig, summary_df, summary_csv

# --- Gradio Interface ---
with gr.Blocks() as demo:
    gr.Markdown("## 💳 Credit Card Amortization Tool (Interactive)")

    file_in = gr.File(label="Upload cards.csv", type="filepath")
    max_allowed = gr.Number(label="Max Allowed Monthly Payment", value=500)
    compute_btn = gr.Button("Compute")

    # Outputs
    status = gr.Textbox(label="Status")
    monthly_table = gr.Dataframe(label="Monthly Allocation")
    monthly_csv_file = gr.File(label="Download Monthly CSV", type="filepath")
    excel_file = gr.File(label="Download Excel Workbook", type="filepath")
    balance_chart = gr.Plot(label="Remaining Balances")
    summary_table = gr.Dataframe(label="Card Summary")
    summary_csv_file = gr.File(label="Download Summary CSV", type="filepath")

    # Compute schedules only on button click
    compute_btn.click(
        fn=compute_from_csv,
        inputs=[file_in, max_allowed],
        outputs=[status, monthly_table, monthly_csv_file, excel_file, balance_chart, summary_table, summary_csv_file]
    )

if __name__ == "__main__":
    demo.launch()
