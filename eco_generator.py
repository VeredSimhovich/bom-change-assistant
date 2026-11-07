import os
import sys
import time
from dotenv import load_dotenv
from google import genai
from google.genai import types

from bom_compare import load_bom, compare_boms
from bom_validate import validate_bom

# Reads GEMINI_API_KEY from the .env file (the key never goes into the code)
load_dotenv()

# "gemini-flash-latest" always points to Google's current Flash model (free tier).
# You can override it by adding GEMINI_MODEL=... to the .env file.
MODEL = os.getenv("GEMINI_MODEL", "gemini-3.8-flash")

# If the main model is busy or over quota, these are tried next, in order.
FALLBACK_MODELS = ["gemini-3.5-flash", "gemini-2.5-flash", "gemini-3.5-flash-lite"]

SYSTEM_PROMPT = """You are an experienced product configuration engineer at a hardware company.
You write clear, accurate Engineering Change Order (ECO) drafts based on BOM comparison data.
Rules:
- Use only the data you are given. Never invent part numbers, values or reasons.
- When a reason for a change is not stated in the data, write a likely reason and mark it "(to be confirmed)".
- If a removed part and an added part look like a replacement (same function, similar description), present them as one replacement.
- Treat validation errors as blockers that must be fixed before the ECO can be approved.
- Be precise, never generalize: name the exact parts that changed. For example, if one of two LEDs
  was removed, write "amber LED (LED-8002) removed", never "LEDs removed".
- Use the full parts list of the new revision to understand what remains in the design.
- Never write that something is "verified" or "confirmed" unless the DATA proves it. When the correct
  value is unknown (for example, the true quantity of a duplicated part), say it must be confirmed.
- Before you finish, check every sentence of the Summary against the DATA. Remove or fix any
  statement that is not directly supported by it.
- Write in professional English, concise, using Markdown."""

ECO_TEMPLATE = """Write an ECO draft with exactly these sections:

# ECO Draft: {product} Rev {old_rev} -> Rev {new_rev}

## 1. Summary
2-3 sentences describing the change at a high level.

## 2. Change Details
A Markdown table with columns: Item | Part Number | Change Type (Add / Remove / Replace / Modify) | Old | New | Likely Reason

## 3. Affected Assemblies
Which parent assemblies are affected (use the Parent PN data).

## 4. Validation Issues (Blockers)
A list of every validation error and warning in the new revision, with a recommended fix for each.

## 5. Risk Assessment
Overall risk level (Low / Medium / High) and 2-4 bullet points explaining why.

## 6. Required Actions Before Approval
A numbered checklist.

---
DATA

Added parts:
{added}

Removed parts:
{removed}

Changed fields:
{changed}

Validation issues in the new revision:
{issues}

Full parts list of the new revision (for context only):
{new_parts}
"""


def build_prompt(old_df, new_df):
    """Run the comparison and validation, and turn the results into a prompt."""
    added, removed, changed = compare_boms(old_df, new_df)
    issues = validate_bom(new_df)

    columns = ["Part Number", "Parent PN", "Description", "Qty", "MPN", "Lifecycle Status"]
    top = new_df[new_df["Level"] == 0].iloc[0]
    old_top = old_df[old_df["Level"] == 0].iloc[0]

    return ECO_TEMPLATE.format(
        product=top["Part Number"],
        old_rev=old_top["Rev"],
        new_rev=top["Rev"],
        added=added[columns].to_string(index=False) if not added.empty else "None",
        removed=removed[columns].to_string(index=False) if not removed.empty else "None",
        changed=changed.to_string(index=False) if not changed.empty else "None",
        issues=issues.to_string(index=False) if not issues.empty else "None",
        new_parts=new_df[["Part Number", "Description", "Qty"]].to_string(index=False),
    )


def generate_eco(old_df, new_df):
    """Send the prompt to Gemini and return (ECO draft as Markdown, model used).

    Each model is tried up to 2 times. If it is busy (503) or over the
    free-tier quota (429), the next model in the list is tried.
    """
    client = genai.Client()  # uses GEMINI_API_KEY automatically
    prompt = build_prompt(old_df, new_df)
    models_to_try = [MODEL] + [m for m in FALLBACK_MODELS if m != MODEL]
    last_error = None

    for model in models_to_try:
        for attempt in range(2):
            try:
                response = client.models.generate_content(
                    model=model,
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        system_instruction=SYSTEM_PROMPT,
                        temperature=0.2,  # low = more consistent, factual output
                    ),
                )
                return response.text, model
            except Exception as e:
                last_error = e
                message = str(e)
                if "503" in message or "UNAVAILABLE" in message:
                    print(f"  {model} is busy, retrying...")
                    time.sleep(5)
                elif "429" in message or "RESOURCE_EXHAUSTED" in message or "404" in message:
                    break  # over quota or not available: move to the next model
                else:
                    raise
        print(f"  Switching from {model} to the next model...")

    raise RuntimeError(f"All models failed. Last error: {last_error}")


def list_models():
    """Print the Gemini models available to this API key."""
    client = genai.Client()
    for m in client.models.list():
        print(m.name)


if __name__ == "__main__":
    old_bom = load_bom("BOM_NL-100G-2P_RevA.xlsx")
    new_bom = load_bom("BOM_NL-100G-2P_RevB.xlsx")

    # Run "python eco_generator.py --preview" to see the prompt without calling the API
    if "--preview" in sys.argv:
        print(build_prompt(old_bom, new_bom))
        sys.exit()

    if not os.getenv("GEMINI_API_KEY"):
        print("Missing API key: create a .env file with GEMINI_API_KEY=your-key")
        sys.exit(1)

    # Run "python eco_generator.py --models" to see which models your key can use
    if "--models" in sys.argv:
        list_models()
        sys.exit()

    print(f"Generating ECO draft with {MODEL}...")
    try:
        eco, used_model = generate_eco(old_bom, new_bom)
    except Exception as e:
        print("Error from Gemini:", e)
        print("Tip: run 'python eco_generator.py --models' and put one of the model names")
        print("in your .env file as GEMINI_MODEL=model-name (without the 'models/' prefix).")
        sys.exit(1)

    with open("ECO_draft.md", "w", encoding="utf-8") as f:
        f.write(eco)

    print(eco)
    print(f"\nGenerated with {used_model}. Saved to ECO_draft.md")
