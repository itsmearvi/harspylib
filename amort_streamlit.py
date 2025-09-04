import streamlit as st
import pandas as pd
import tempfile, os
from amort_allocator import load_cards_from_csv, plan_multi_card_with_max, generate_summary

# --- Initialize session state ---
for key in ["cards_file", "max_allowed", "schedules", "monthly_summary", "summary_df", "compute_done"]:
    if key not in st.session_state:
        st.session_state[key] = None

st.title("💳 Credit Card Amortization Tool")

uploaded_file = st.file_uploader("Upload cards.csv", type="csv")
max_allowed = st.number_input("Max Allowed Monthly Payment", min_value=50.0, value=1000.0, step=50.0)

# Determine whether recomputation is needed
recompute = False
if uploaded_file is not None:
    if (st.session_state.cards_file != uploaded_file) or (st.session_state.max_allowed != max_allowed):
        st.session_state.cards_file = uploaded_file
        st.session_state.max_allowed = max_allowed
        st.session_state.compute_done = False  # reset compute flag
        recompute = True

compute_clicked = st.button("Compute Schedules")

# --- Compute schedules ---
if compute_clicked or (recompute and not st.session_state.compute_done):
    if uploaded_file is None:
        st.error("Please upload a cards.csv file.")
    else:
        tmp_path = os.path.join(tempfile.mkdtemp(), "cards.csv")
        with open(tmp_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

        cards = load_cards_from_csv(tmp_path)
        st.session_state.schedules, st.session_state.monthly_summary = plan_multi_card_with_max(
            cards, float(max_allowed)
        )
        st.session_state.summary_df = generate_summary(st.session_state.schedules)
        st.session_state.compute_done = True

# --- Display results ---
if st.session_state.schedules is not None:
    st.subheader("📊 Monthly Allocation")
    st.dataframe(st.session_state.monthly_summary)

    st.subheader("📋 Card Summary")
    st.dataframe(st.session_state.summary_df)

    # --- Interactive balance chart ---
    def plot_balances(schedules):
        valid_schedules = {name: df for name, df in schedules.items() if "New_Bal" in df.columns}
        if not valid_schedules:
            return
        all_months = sorted({month for df in valid_schedules.values() for month in df["Month"]})
        aligned_balances = {name: df.set_index("Month").reindex(all_months)["New_Bal"].fillna(0)
                            for name, df in valid_schedules.items()}
        balances_df = pd.DataFrame(aligned_balances)
        balances_df.index.name = "Month"
        st.line_chart(balances_df)

    plot_balances(st.session_state.schedules)

    # --- Downloads ---
    tmpdir = tempfile.mkdtemp()

    # Excel workbook
    
    excel_prefix = st.session_state.cards_file.name.split(".csv")[0]
    excel_path = os.path.join(tmpdir, excel_prefix + "-schedules.xlsx")
    with pd.ExcelWriter(excel_path) as writer:
        st.session_state.monthly_summary.to_excel(writer, sheet_name="Summary", index=False)
        for name, df in st.session_state.schedules.items():
            df.to_excel(writer, sheet_name=name, index=False)
    with open(excel_path, "rb") as f:
        st.download_button("⬇ Download Excel Workbook", f, file_name=excel_prefix + "-schedules.xlsx")

    # Monthly CSV
    monthly_csv = os.path.join(tmpdir, "monthly_allocation.csv")
    st.session_state.monthly_summary.to_csv(monthly_csv, index=False)
    with open(monthly_csv, "rb") as f:
        st.download_button("⬇ Download Monthly CSV", f, file_name="monthly_allocation.csv")

    # Per-card CSVs
    st.subheader("Per-Card CSVs")
    for name, df in st.session_state.schedules.items():
        card_csv = os.path.join(tmpdir, f"{name}_schedule.csv")
        df.to_csv(card_csv, index=False)
        with open(card_csv, "rb") as f:
            st.download_button(f"Download {name} CSV", f, file_name=f"{name}_schedule.csv")

    # Summary CSV
    summary_csv = os.path.join(tmpdir, "summary.csv")
    st.session_state.summary_df.to_csv(summary_csv, index=False)
    with open(summary_csv, "rb") as f:
        st.download_button("⬇ Download Summary CSV", f, file_name="summary.csv")
