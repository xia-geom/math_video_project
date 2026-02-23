import pandas as pd
import numpy as np

# ==========================================
# CONFIGURATION
# ==========================================
FILE_PATH = 'data/raw/drew00h_20260112_032345.xls'
SHEET_NAME = 'Drew00h_20260112 03_23_45'       # Check your Excel tab name
PASSING_GRADE = 50.0        # The standard UQAM cutoff (change to 50.0 if propédeutique)
# ==========================================

def clean_and_load(file_path):
    # Load data, skipping rows if necessary.
    # We assume the headers are on row 1 (index 0).
    df = pd.read_excel(file_path, sheet_name=0, engine='xlrd')    
    # Fill NaN numerical values with 0 for calculation purposes
    cols_to_fix = ['Examen Intra(47,5)', 'Examen Final(47,5)', 'Presence(5)']
    for col in cols_to_fix:
        if col in df.columns:
            df[col] = df[col].fillna(0)
    return df

def run_audit():
    print(f"--- STARTING AUDIT ON {FILE_PATH} ---\n")
    df = clean_and_load(FILE_PATH)
    
    errors_found = 0
    warnings_found = 0

    for index, row in df.iterrows():
        # Skip empty rows or header artifacts
        if pd.isna(row['Nom']):
            continue

        student = row['Nom']
        row_num = index + 2  # Excel row number (1-based + header)
        
        # 1. STATUS CHECK (Skip DX/XX students)
        status = row['Statut d\'inscription']
        if pd.notna(status) and status in ['DX', 'XX']:
            continue

        # 2. MATH RE-VERIFICATION
        # Recalculate the weighted sum independently
        calc_total = (
            float(row.get('Examen Intra(47,5)', 0)) +
            float(row.get('Examen Final(47,5)', 0)) +
            float(row.get('Presence(5)', 0))
        )
        excel_total = float(row.get('Total(100)', 0))
        
        # Check if they match within 0.01 precision
        if not np.isclose(calc_total, excel_total, atol=0.01):
            print(f"🔴 MATH ERROR (Row {row_num}): {student}")
            print(f"   - Excel says: {excel_total}")
            print(f"   - Python calc: {calc_total:.2f}")
            errors_found += 1

        # 3. COMPLETENESS CHECK (The "Lajoie-Asselin" Trap)
        letter_grade = row.get('Note')
        if pd.isna(letter_grade):
            print(f"🔴 MISSING GRADE (Row {row_num}): {student}")
            print(f"   - Total is {excel_total}, but 'Note' column is EMPTY.")
            errors_found += 1
            
        # 4. THRESHOLD LOGIC CHECK
        # Only check if we actually have a grade
        elif pd.notna(letter_grade):
            # Check for False Positives (Passed but score is too low)
            if letter_grade == 'S' and excel_total < PASSING_GRADE:
                print(f"⚠️ THRESHOLD WARNING (Row {row_num}): {student}")
                print(f"   - Marked 'S' but score is {excel_total} (Cutoff: {PASSING_GRADE})")
                print(f"   - Is this an exception? Verify manual override.")
                warnings_found += 1
            
            # Check for False Negatives (Failed but score is high enough)
            elif letter_grade == 'E' and excel_total >= PASSING_GRADE:
                print(f"⚠️ THRESHOLD WARNING (Row {row_num}): {student}")
                print(f"   - Marked 'E' but score is {excel_total} (Cutoff: {PASSING_GRADE})")
                warnings_found += 1

    print("\n--- AUDIT COMPLETE ---")
    print(f"Errors: {errors_found}")
    print(f"Warnings: {warnings_found}")
    
    if errors_found == 0 and warnings_found == 0:
        print("✅ CLEAN. You are safe to enter these grades.")
    else:
        print("❌ FIX REQUIRED. Do not upload until resolved.")

if __name__ == "__main__":
    run_audit()