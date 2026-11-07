import pandas as pd
from bom_compare import load_bom

# Fields that every BOM line must have
REQUIRED_FIELDS = ["Part Number", "Description", "Rev", "Qty", "Manufacturer", "MPN"]


def validate_bom(df):
    """Run data-quality checks on a BOM and return a table of issues."""
    issues = []

    def add_issue(severity, pn, check, details):
        issues.append({"Severity": severity, "Part Number": pn, "Check": check, "Details": details})

    # 1. Duplicate part numbers (the same part listed twice)
    duplicates = df[df.duplicated(subset="Part Number", keep=False)]
    for pn in duplicates["Part Number"].unique():
        count = (df["Part Number"] == pn).sum()
        add_issue("Error", pn, "Duplicate part", f"Listed {count} times in the BOM")

    # 2. Missing required fields
    for _, row in df.iterrows():
        for field in REQUIRED_FIELDS:
            if str(row[field]).strip() == "":
                add_issue("Error", row["Part Number"], "Missing field", f"'{field}' is empty")

    # 3. Quantity must be a positive number
    for _, row in df.iterrows():
        try:
            qty = float(row["Qty"])
            if qty <= 0:
                add_issue("Error", row["Part Number"], "Invalid quantity", f"Qty is {row['Qty']}")
        except ValueError:
            add_issue("Error", row["Part Number"], "Invalid quantity", f"Qty '{row['Qty']}' is not a number")

    # 4. Lifecycle status: EOL is an error, NRND is a warning
    for _, row in df.iterrows():
        status = str(row["Lifecycle Status"]).strip().upper()
        if status == "EOL":
            add_issue("Error", row["Part Number"], "End-of-life part",
                      "Part is EOL - find a replacement before release")
        elif status == "NRND":
            add_issue("Warning", row["Part Number"], "NRND part",
                      "Not recommended for new designs - plan a replacement")

    # 5. Every parent must exist in the BOM (no orphan parts)
    all_pns = set(df["Part Number"])
    for _, row in df.iterrows():
        parent = str(row["Parent PN"]).strip()
        if parent != "" and parent not in all_pns:
            add_issue("Error", row["Part Number"], "Missing parent",
                      f"Parent '{parent}' does not exist in the BOM")

    result = pd.DataFrame(issues, columns=["Severity", "Part Number", "Check", "Details"])
    # Show errors before warnings
    result = result.sort_values("Severity").reset_index(drop=True)
    return result


if __name__ == "__main__":
    for path in ["BOM_NL-100G-2P_RevA.xlsx", "BOM_NL-100G-2P_RevB.xlsx"]:
        bom = load_bom(path)
        issues = validate_bom(bom)
        errors = (issues["Severity"] == "Error").sum()
        warnings = (issues["Severity"] == "Warning").sum()
        print(f"=== {path}: {errors} errors, {warnings} warnings ===")
        if issues.empty:
            print("No issues found")
        else:
            print(issues.to_string(index=False))
        print()
