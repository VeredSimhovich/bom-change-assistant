import pandas as pd

# The columns we check for changes between revisions
COMPARE_COLUMNS = ["Description", "Rev", "Qty", "Manufacturer", "MPN", "Lifecycle Status"]


def load_bom(path):
    """Read a BOM Excel file and clean it up."""
    df = pd.read_excel(path)
    df["Part Number"] = df["Part Number"].astype(str).str.strip()
    df = df.fillna("")
    return df


def compare_boms(old_df, new_df):
    """Compare two BOM revisions and return what was added, removed and changed."""
    # Duplicate part numbers are a data-quality issue (handled in step 3),
    # so for comparison we keep only the first appearance of each part.
    old = old_df.drop_duplicates(subset="Part Number").set_index("Part Number")
    new = new_df.drop_duplicates(subset="Part Number").set_index("Part Number")

    added_pns = [pn for pn in new.index if pn not in old.index]
    removed_pns = [pn for pn in old.index if pn not in new.index]
    common_pns = [pn for pn in new.index if pn in old.index]

    added = new.loc[added_pns].reset_index()
    removed = old.loc[removed_pns].reset_index()

    changes = []
    for pn in common_pns:
        for col in COMPARE_COLUMNS:
            old_value = old.at[pn, col]
            new_value = new.at[pn, col]
            if str(old_value) != str(new_value):
                changes.append({
                    "Part Number": pn,
                    "Description": new.at[pn, "Description"],
                    "Field": col,
                    "Old Value": str(old_value),
                    "New Value": str(new_value),
                })
    changed = pd.DataFrame(changes, columns=["Part Number", "Description", "Field", "Old Value", "New Value"])

    return added, removed, changed


if __name__ == "__main__":
    old_bom = load_bom("BOM_NL-100G-2P_RevA.xlsx")
    new_bom = load_bom("BOM_NL-100G-2P_RevB.xlsx")

    added, removed, changed = compare_boms(old_bom, new_bom)

    print("=== ADDED PARTS ===")
    print(added[["Part Number", "Description", "Qty"]].to_string(index=False))
    print()
    print("=== REMOVED PARTS ===")
    print(removed[["Part Number", "Description", "Qty"]].to_string(index=False))
    print()
    print("=== CHANGED PARTS ===")
    print(changed.to_string(index=False))
    print()
    print(f"Summary: {len(added)} added, {len(removed)} removed, {len(changed)} field changes")
