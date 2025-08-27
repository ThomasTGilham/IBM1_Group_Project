# --- 1. IMPORT NECESSARY LIBRARIES ---
import pandas as pd
import os
import glob
import re

# --- 2. CONFIGURATION ---
# Set your folder paths and keyword lists here.

# The folder where all your individual scraped CSV files are located.
# IMPORTANT: Create a folder (e.g., 'raw_scraped_data') and put all your CSVs inside it.
INPUT_FILE_PATH = r'/Users/thomastrainor-gilham/Library/CloudStorage/OneDrive-UniversityofBristol/EwDS Dissertation/Data/Web Scraping/Old Datasets & Scripts/pengjin_adzuna_jobs_by_skill_TomEdited.csv' 

# The name for your new, clean, master CSV file.
OUTPUT_MASTER_CSV = r'/Users/thomastrainor-gilham/Library/CloudStorage/OneDrive-UniversityofBristol/EwDS Dissertation/Data/Web Scraping/pengjin_adzuna_cleaned_job_listings.csv'

# Keywords for filtering job titles to keep only relevant roles.
# A job title MUST contain at least one word from this list to be kept.
# Using lemmas/root words makes the filter more effective.
RELEVANT_TITLE_KEYWORDS = ['analyst', 'scientist', 'engineer', 'economic', 'economist', 'econometrics', 'quantitative', 'data', 'machine learning', 
                           'intelligence', 'developer', 'consultant', 'AI', 'analytics']

# Keywords to identify and remove irrelevant roles.
# If a job title contains any of these words, it will be removed.
IRRELEVANT_TITLE_KEYWORDS = ['sales', 'recruiter', 'recruitment', 'development', 'mail']


# --- 3. DATA CLEANING AND FILTERING FUNCTIONS ---
def clean_and_prepare_data(df):
    """
    Runs a full cleaning pipeline on the merged DataFrame.
    
    Args:
        df (pandas.DataFrame): The raw, merged DataFrame.

    Returns:
        pandas.DataFrame: The cleaned and filtered DataFrame.
    """
    # Ensure key columns exist, filling missing with empty strings
    for col in ['Job Title', 'Company Name', 'Job Description']:
        if col not in df.columns:
            print(f"Warning: Column '{col}' not found. Skipping operations on it.")
            df[col] = '' # Create empty column to prevent errors
    
    # --- Step 3.1: Deduplication ---
    # We define a duplicate by the job title, company name, and description.
    initial_rows = len(df)
    df.drop_duplicates(subset=['Job Title', 'Company Name', 'Job Description'], keep='first', inplace=True)
    rows_after_dedup = len(df)
    print(f"Removed {initial_rows - rows_after_dedup} duplicate listings.")

    # --- Step 3.2: Filter Irrelevant Jobs ---
    # Standardize job titles to lower case for consistent matching
    df['title_lower'] = df['Job Title'].str.lower().fillna('')
    
    # Filter based on required and irrelevant keywords
    # 1. Must contain at least one RELEVANT word
    # The regex `r'\b(...)\b'` ensures we match whole words
    relevant_pattern = r'\b(' + '|'.join(RELEVANT_TITLE_KEYWORDS) + r')\b'
    df = df[df['title_lower'].str.contains(relevant_pattern, regex=True)]
    rows_after_relevant_filter = len(df)
    print(f"Filtered to {rows_after_relevant_filter} rows based on relevant keywords.")
    
    # 2. Must NOT contain any IRRELEVANT words
    irrelevant_pattern = r'\b(' + '|'.join(IRRELEVANT_TITLE_KEYWORDS) + r')\b'
    df = df[~df['title_lower'].str.contains(irrelevant_pattern, regex=True)]
    rows_after_irrelevant_filter = len(df)
    print(f"Filtered to {rows_after_irrelevant_filter} rows after removing irrelevant keywords.")

    # --- Step 3.5: Standardise Company Names ---
    # This is a simple example. You can make this much more sophisticated.
    df['Company Name'] = df['Company Name'].str.replace(r' Ltd\.?| plc| Limited| Inc.', '', regex=True).str.strip()
    print("Standardised company names (removed Ltd, plc, etc.).")
    
    # --- Step 3.6: Final Cleanup ---
    df.drop(columns=['title_lower'], inplace=True) # Remove the temporary column
    df.reset_index(drop=True, inplace=True)
    
    print(f"\nCleaning complete. Final total rows: {len(df)}")
    return df


# --- 4. MAIN EXECUTION SCRIPT ---

if __name__ == '__main__':
    # Phase 1: Consolidation
    master_dataframe = pd.read_csv(INPUT_FILE_PATH)
    
    if master_dataframe is not None:
        # Phase 2: Cleaning
        cleaned_dataframe = clean_and_prepare_data(master_dataframe)
        
        # Phase 3: Save the result
        try:
            cleaned_dataframe.to_csv(OUTPUT_MASTER_CSV, index=False)
            print(f"\nSuccessfully saved the cleaned data to '{OUTPUT_MASTER_CSV}'")
        except Exception as e:
            print(f"\nError: Could not save the file. Reason: {e}")