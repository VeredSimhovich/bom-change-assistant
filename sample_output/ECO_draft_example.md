# ECO Draft: NL-100G-2P Rev A -> Rev B

## 1. Summary
This Engineering Change Order advances the NovaLink 100G Dual-Port Ethernet Adapter top assembly (NL-100G-2P), main board (PCA-1001), and bare PCB (PCB-2001) from Rev A to Rev B. Key hardware changes include replacing the 0.9V 20A voltage regulator (IC-3003) with a 25A version (IC-3007), adding an ASIC thermal pad (MECH-1105), removing the amber LEDs (LED-8002), adjusting passive component quantities, and updating firmware (FW-0001) to Rev 1.6. Four validation errors are flagged on the new revision and must be resolved as blockers before final approval.

## 2. Change Details

| Item | Part Number | Change Type (Add / Remove / Replace / Modify) | Old | New | Likely Reason |
| :--- | :--- | :--- | :--- | :--- | :--- |
| NovaLink 100G Dual-Port Ethernet Adapter (Top Assembly) | NL-100G-2P | Modify | Rev A | Rev B | Major revision update for top assembly (to be confirmed) |
| Printed Circuit Assembly, Main Board | PCA-1001 | Modify | Rev A | Rev B | Major revision update for main board assembly (to be confirmed) |
| Bare PCB, 12-layer, FR-4 | PCB-2001 | Modify | Rev A | Rev B | PCB layout revision update (to be confirmed) |
| Voltage Regulator, 0.9V | IC-3003 -> IC-3007 | Replace | IC-3003 (0.9V, 20A, Qty 2) | IC-3007 (0.9V, 25A, Qty 2) | Replace NRND component with higher current capacity regulator (to be confirmed) |
| Thermal Pad, 1.5mm, ASIC | MECH-1105 | Add | - | Qty 1 (MPN: CF-TP-15) | Improve thermal dissipation for ASIC (to be confirmed) |
| LED, Amber, 0603 | LED-8002 | Remove | Qty 2 (MPN: BB-LED-A) | - | Deprecate amber LED status indicator (to be confirmed) |
| Capacitor, Ceramic, 0.1uF, 16V, 0402 | CAP-5001 | Modify | Qty 120 | Qty 132 | Additional high-frequency decoupling (to be confirmed) |
| Capacitor, Polymer, 330uF, 2.5V | CAP-5003 | Modify | Qty 8 | Qty 10 | Additional bulk capacitance (to be confirmed) |
| Inductor, Power, 0.22uH, 30A | IND-7001 | Modify | Manufacturer: MagFlow | Manufacturer: [Empty] | Vendor entry error or source change (to be confirmed) |
| Firmware Image, Adapter | FW-0001 | Modify | Rev 1.4 (MPN: FW-NL100-1.4) | Rev 1.6 (MPN: FW-NL100-1.6) | Firmware update for hardware compatibility/features (to be confirmed) |
| Label, Serial Number | LBL-1201 | Modify | Qty 1 | Qty 0 | Label BOM entry error or process change (to be confirmed) |
| Oscillator, 156.25MHz | OSC-4001 | Modify | Lifecycle Status: Active | Lifecycle Status: EOL | Part status changed to End-of-Life (to be confirmed) |

## 3. Affected Assemblies
- **NL-100G-2P** (NovaLink 100G Dual-Port Ethernet Adapter - Top Assembly)
- **PCA-1001** (Printed Circuit Assembly, Main Board)

## 4. Validation Issues (Blockers)
1. **RES-6001 (Duplicate part):** Listed 2 times in the BOM.
   - *Recommended Fix:* Remove the duplicate line item in the BOM to ensure RES-6001 is listed once with the single correct total quantity.
2. **IND-7001 (Missing field):** Manufacturer field is empty.
   - *Recommended Fix:* Populate the missing 'Manufacturer' field with the designated approved manufacturer name.
3. **LBL-1201 (Invalid quantity):** Quantity is set to 0.
   - *Recommended Fix:* Correct the quantity to 1 if the serial number label is required, or fully remove the part line item if obsolete.
4. **OSC-4001 (End-of-life part):** Component lifecycle status is EOL.
   - *Recommended Fix:* Identify, qualify, and update the BOM with an active pin-compatible replacement for oscillator OSC-4001 prior to release.

## 5. Risk Assessment
Overall Risk Level: **High**

- **Validation Blockers Present:** Four unresolved BOM errors (duplicate entry, missing manufacturer data, zero part quantity, and an EOL part) currently block release.
- **Obsolescence / Supply Chain Risk:** Oscillator OSC-4001 has reached EOL status; failure to substitute an active component will disrupt manufacturing.
- **Power and Thermal Design Changes:** Replacing 0.9V 20A voltage regulators (IC-3003) with 25A regulators (IC-3007), increasing decoupling/bulk capacitance (CAP-5001, CAP-5003), adding thermal pad MECH-1105, and updating PCB-2001 to Rev B alter power distribution and thermal profiles.
- **Firmware Integration:** Updating adapter firmware FW-0001 from Rev 1.4 to Rev 1.6 requires full functional verification on Rev B hardware.

## 6. Required Actions Before Approval
1. [ ] Fix duplicate BOM entry for Resistor `RES-6001`.
2. [ ] Enter valid Manufacturer information for Power Inductor `IND-7001`.
3. [ ] Resolve invalid quantity (Qty 0) for Serial Number Label `LBL-1201` by updating quantity or removing the item.
4. [ ] Select and qualify an active replacement for EOL Oscillator `OSC-4001` and update the BOM.
5. [ ] Verify power delivery stability with 0.9V 25A Voltage Regulator `IC-3007` and updated decoupling capacitors (`CAP-5001`, `CAP-5003`).
6. [ ] Confirm thermal design with added ASIC Thermal Pad `MECH-1105`.
7. [ ] Validate Adapter Firmware `FW-0001` Rev 1.6 compatibility with `PCA-1001` Rev B board revision.