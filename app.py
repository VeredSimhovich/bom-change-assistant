import os
import pandas as pd
import streamlit as st

from bom_compare import compare_boms
from bom_validate import validate_bom
from eco_generator import generate_eco

SAMPLE_OLD = "BOM_NL-100G-2P_RevA.xlsx"
SAMPLE_NEW = "BOM_NL-100G-2P_RevB.xlsx"

st.set_page_config(page_title="BOM Change Assistant", page_icon="🔧", layout="wide")


def read_bom(source):
    """Read a BOM from an uploaded file or a file path, and clean it up."""
    df = pd.read_excel(source)
    df["Part Number"] = df["Part Number"].astype(str).str.strip()
    return df.fillna("")


# ---------- Header ----------
st.title("🔧 BOM Change Assistant")
st.caption("Compare two BOM revisions, catch data-quality issues, and draft an ECO with AI. "
           "Sample data is fictional.")

# ---------- Inputs ----------
with st.sidebar:
    st.header("BOM files")
    use_sample = st.toggle("Use sample BOMs (NovaLink adapter)", value=True)
    if use_sample:
        old_source, new_source = SAMPLE_OLD, SAMPLE_NEW
        st.info("Using fictional sample files: Rev A vs Rev B")
    else:
        old_source = st.file_uploader("Old revision (.xlsx)", type="xlsx")
        new_source = st.file_uploader("New revision (.xlsx)", type="xlsx")

if not old_source or not new_source:
    st.warning("Upload both BOM files in the sidebar to start.")
    st.stop()

old_df = read_bom(old_source)
new_df = read_bom(new_source)

added, removed, changed = compare_boms(old_df, new_df)
issues = validate_bom(new_df)
errors = int((issues["Severity"] == "Error").sum())
warnings = int((issues["Severity"] == "Warning").sum())

# ---------- Dashboard ----------
c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("Parts in new BOM", len(new_df))
c2.metric("Added", len(added))
c3.metric("Removed", len(removed))
c4.metric("Field changes", len(changed))
c5.metric("Validation errors", errors)
c5.caption(f"{warnings} warning(s)")

if errors > 0:
    st.error(f"⛔ {errors} blocking issue(s) in the new revision - fix before ECO approval.")
else:
    st.success("✅ No blocking issues in the new revision.")

# ---------- Details ----------
tab_changes, tab_issues, tab_eco = st.tabs(["📋 Changes", "⚠️ Validation", "🤖 ECO Draft (AI)"])

with tab_changes:
    left, right = st.columns(2)
    with left:
        st.subheader("Added parts")
        st.dataframe(added[["Part Number", "Description", "Qty"]], hide_index=True, width="stretch")
    with right:
        st.subheader("Removed parts")
        st.dataframe(removed[["Part Number", "Description", "Qty"]], hide_index=True, width="stretch")
    st.subheader("Changed fields")
    st.dataframe(changed, hide_index=True, width="stretch")
    if not changed.empty:
        st.subheader("Changes by field")
        st.bar_chart(changed["Field"].value_counts())

with tab_issues:
    if issues.empty:
        st.success("No issues found.")
    else:
        st.dataframe(issues, hide_index=True, width="stretch")

with tab_eco:
    st.write("The comparison and validation above are calculated by code. "
             "The AI only writes the ECO document from those results - review it before use.")
    if not os.getenv("GEMINI_API_KEY"):
        st.warning("No GEMINI_API_KEY found in the .env file.")
    elif st.button("Generate ECO draft", type="primary"):
        with st.spinner("Drafting ECO..."):
            try:
                eco, used_model = generate_eco(old_df, new_df)
                st.session_state["eco"] = eco
                st.session_state["eco_model"] = used_model
            except Exception as e:
                st.error(f"AI request failed: {e}")

    if "eco" in st.session_state:
        st.caption(f"Generated with {st.session_state['eco_model']}")
        st.markdown(st.session_state["eco"])
        st.download_button("Download ECO (.md)", st.session_state["eco"],
                           file_name="ECO_draft.md", mime="text/markdown")
