import pandas as pd
import os
import glob
import re

# --- 1. CONFIGURATION ---
# Set your folder paths and keyword lists here.

# The folder where all your individual scraped CSV files are located.
# IMPORTANT: Create a folder (e.g., 'raw_scraped_data') and put all your CSVs inside it.
INPUT_FOLDER_PATH = r'C:\Users\qq18295\OneDrive - University of Bristol\EwDS Dissertation\Data\Web Scraping\raw_job_listings_data' 

# The name for your new, clean, master CSV file.
OUTPUT_MASTER_CSV = r'C:\Users\qq18295\OneDrive - University of Bristol\EwDS Dissertation\Data\Web Scraping\master_cleaned_job_listings.csv'

# Keywords for filtering job titles to keep only relevant roles.
# A job title MUST contain at least one word from this list to be kept.
# Using lemmas/root words makes the filter more effective.
RELEVANT_TITLE_KEYWORDS = ['analyst', 'scientist', 'engineer', 'economic', 'economist', 'econometrics', 'quantitative', 'data', 'machine learning', 
                           'intelligence', 'developer', 'consultant', 'AI', 'analytics']

# Keywords to identify and remove irrelevant roles.
# If a job title contains any of these words, it will be removed.
IRRELEVANT_TITLE_KEYWORDS = ['sales', 'recruiter', 'recruitment', 'development', 'mail']

# List of countries we expect to see
COUNTRIES = ['England', 'Scotland', 'Wales', 'Northern Ireland', 'United Kingdom', 'UK', 'Ireland', 'France', 'Germany', 'USA', 'Canada']  # Add more as needed


# --- 2. DATA CONSOLIDATION FUNCTION ---

def merge_and_tag_csvs(folder_path):
    """
    Finds all CSVs in a folder, merges them, and adds a 'search_keyword' column.
    The keyword is extracted from the CSV filename.
    
    Args:
        folder_path (str): The path to the folder with raw CSV files.

    Returns:
        pandas.DataFrame: A single DataFrame containing all merged data, or None if no files are found.
    """
    print(f"Searching for CSV files in '{folder_path}'...")
    all_files = glob.glob(os.path.join(folder_path, "*.csv"))
    
    if not all_files:
        print("Error: No CSV files found. Please check the INPUT_FOLDER_PATH.")
        return None

    print(f"Found {len(all_files)} files. Merging now...")
    df_list = []
    for filepath in all_files:
        try:
            df = pd.read_csv(filepath)
            
            # Extract the base filename (e.g., 'data_scientist_london.csv')
            filename = os.path.basename(filepath)
            
            # Extract the keyword part (e.g., 'data_scientist')
            # This assumes a format like 'keyword_location.csv' or just 'keyword.csv'
            keyword = filename.split('_')[0]
            df['search_keyword'] = keyword
            
            df_list.append(df)
            print(f"  - Merged '{filename}' (tagged as '{keyword}')")
        except Exception as e:
            print(f"Warning: Could not read or process {filepath}. Error: {e}")
            
    if not df_list:
        print("Error: No dataframes were successfully loaded.")
        return None
        
    master_df = pd.concat(df_list, ignore_index=True)
    print(f"\nMerge complete. Initial total rows: {len(master_df)}")
    return master_df


# --- 3. DATA CLEANING AND FILTERING FUNCTIONS ---

def split_location_with_countries(location):
    if pd.isna(location) or location == '':
        return '', ''
    
    parts = [part.strip() for part in location.split(',')]
    city = parts[0] if parts else ''
    
    # Find the first part that matches a known country
    country = ''
    for part in reversed(parts):  # Start from the end
        if part in COUNTRIES:
            country = part
            break
    
    # If no country found, use the last part
    if not country and len(parts) > 1:
        country = parts[-1]
    
    return city, country



def clean_salary_data(salary_str):
    """
    Clean and standardise salary data from messy formats.
    
    Args:
        salary_str (str): Raw salary string
        
    Returns:
        dict: Dictionary with cleaned salary components
    """
    if pd.isna(salary_str) or salary_str == '':
        return {
            'currency': '',
            'min_salary': None,
            'max_salary': None,
            'pay_period': '',
            'source': '',
            'original': salary_str
        }
    
    # Initialize result dictionary
    result = {
        'currency': '',
        'min_salary': None,
        'max_salary': None,
        'pay_period': 'annual',  # default assumption
        'source': '',
        'original': str(salary_str)
    }
    
    # Clean up the string - remove weird characters and normalize
    cleaned = str(salary_str).replace('Â£', '£').replace('Â ', ' ').strip()
    
    # Extract source (Glassdoor Est., Employer Est., etc.)
    source_match = re.search(r'\((.*?Est\.?.*?)\)', cleaned, re.IGNORECASE)
    if source_match:
        result['source'] = source_match.group(1)
        cleaned = re.sub(r'\(.*?Est\.?.*?\)', '', cleaned, flags=re.IGNORECASE).strip()
    
    # Detect pay period
    if re.search(r'per hour|hourly|/hour|ph\b', cleaned, re.IGNORECASE):
        result['pay_period'] = 'hourly'
    elif re.search(r'per day|daily|/day', cleaned, re.IGNORECASE):
        result['pay_period'] = 'daily'
    elif re.search(r'per month|monthly|/month', cleaned, re.IGNORECASE):
        result['pay_period'] = 'monthly'
    
    # Remove pay period text for cleaner parsing
    cleaned = re.sub(r'per\s*(hour|day|month|year)|hourly|daily|monthly|yearly|/hour|/day|/month|/year', '', cleaned, flags=re.IGNORECASE)
    
    # Extract currency symbols and codes
    currency_patterns = [
        (r'£', 'GBP'),
        (r'\bFCFA\b', 'GBP'),
        (r'\$', 'USD'),
        (r'€', 'EUR'),
        (r'¥', 'JPY'),
        (r'₹', 'INR'),
    ]
    
    for pattern, currency_code in currency_patterns:
        if re.search(pattern, cleaned):
            result['currency'] = currency_code
            break
    
    # Remove currency symbols for number extraction
    cleaned = re.sub(r'[£$€¥₹]|FCFA', '', cleaned)
    
    # Extract numbers (handling K, M suffixes and decimals)
    number_pattern = r'(\d+(?:\.\d+)?)\s*([KMkmBb]?)'
    numbers = re.findall(number_pattern, cleaned)
    
    # Convert numbers with K/M suffixes
    def convert_number(num_str, suffix):
        try:
            num = float(num_str)
            suffix = suffix.upper()
            if suffix == 'K':
                return num * 1000
            elif suffix == 'M':
                return num * 1000000
            elif suffix == 'B':
                return num * 1000000000
            else:
                return num
        except:
            return None
    
    # Process found numbers
    if numbers:
        converted_numbers = []
        for num_str, suffix in numbers:
            converted = convert_number(num_str, suffix)
            if converted is not None:
                converted_numbers.append(converted)
        
        if len(converted_numbers) >= 2:
            # Range format (min - max)
            result['min_salary'] = min(converted_numbers)
            result['max_salary'] = max(converted_numbers)
        elif len(converted_numbers) == 1:
            # Single value
            result['min_salary'] = converted_numbers[0]
            result['max_salary'] = converted_numbers[0]
    
    return result

def process_salary_column(df, salary_column='Salary'):
    """
    Process the entire salary column and create new cleaned columns.
    
    Args:
        df (pandas.DataFrame): DataFrame with salary data
        salary_column (str): Name of the salary column
        
    Returns:
        pandas.DataFrame: DataFrame with new salary columns
    """
    if salary_column not in df.columns:
        print(f"Warning: Column '{salary_column}' not found.")
        return df
    
    print(f"Processing {len(df)} salary entries...")
    
    # Apply cleaning function to each row
    salary_data = df[salary_column].apply(clean_salary_data)
    
    # Extract components into separate columns
    df['salary_currency'] = salary_data.apply(lambda x: x.get('currency', ''))
    df['salary_min'] = salary_data.apply(lambda x: x.get('min_salary'))
    df['salary_max'] = salary_data.apply(lambda x: x.get('max_salary'))
    df['salary_period'] = salary_data.apply(lambda x: x.get('pay_period', ''))
    df['salary_source'] = salary_data.apply(lambda x: x.get('source', ''))
    
    # Create a standardized salary range column
    def format_salary_range(row):
        if pd.isna(row['salary_min']):
            return ''
        elif row['salary_min'] == row['salary_max']:
            return f"{row['salary_currency']} {int(row['salary_min']):,} ({row['salary_period']})"
        else:
            return f"{row['salary_currency']} {int(row['salary_min']):,} - {int(row['salary_max']):,} ({row['salary_period']})"
    
    df['salary_standardized'] = df.apply(format_salary_range, axis=1)
    
    # Print summary statistics
    processed_count = df['salary_min'].notna().sum()
    print(f"Successfully processed {processed_count} salary entries.")
    
    # Show currency distribution
    currency_dist = df['salary_currency'].value_counts()
    print(f"Currency distribution:\n{currency_dist}")
    
    # Show pay period distribution
    period_dist = df['salary_period'].value_counts()
    print(f"Pay period distribution:\n{period_dist}")
    
    return df


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

    # --- Step 3.3: Split Location into City and Country ---
    # Check if location column exists
    if 'Location' in df.columns:
        print("Splitting location data into city and country...")
        df[['City', 'Country']] = df['Location'].apply(lambda x: pd.Series(split_location_with_countries(x)))
        locations_processed = len(df[df['Location'].notna()])
        print(f"Processed {locations_processed} location entries.")
    else:
        print("Warning: 'Location' column not found. Skipping location splitting.")
        df['City'] = ''
        df['Country'] = ''

    # --- Step 3.4: Clean Salary Data ---
    # Check if salary column exists
    if 'Salary' in df.columns:  
        print("Cleaning salary data...")
        df = process_salary_column(df, 'Salary')
    else:
        print("Warning: 'Salary' column not found. Skipping salary cleaning.")

    # --- Step 3.4b: Add Median Annual Salary in GBP ---
    print("Calculating median annual salary in GBP...")
    
    def calculate_annual_median(row):
        if pd.isna(row['salary_min']) or pd.isna(row['salary_max']):
            return None
        median = (row['salary_min'] + row['salary_max']) / 2
        multiplier = 1

        if row['salary_period'] == 'hourly':
            multiplier = 40 * 52  # 40 hours/week, 52 weeks
        elif row['salary_period'] == 'daily':
            multiplier = 5 * 52   # 5 days/week
        elif row['salary_period'] == 'monthly':
            multiplier = 12
        elif row['salary_period'] == 'annual':
            multiplier = 1

        # Only keep if it's GBP
        if row['salary_currency'] == 'GBP':
            return median * multiplier
        else:
            return None

    df['median_annual_salary_gbp'] = df.apply(calculate_annual_median, axis=1)


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
    master_dataframe = merge_and_tag_csvs(INPUT_FOLDER_PATH)
    
    if master_dataframe is not None:
        # Phase 2: Cleaning
        cleaned_dataframe = clean_and_prepare_data(master_dataframe)
        
        # Phase 3: Save the result
        try:
            cleaned_dataframe.to_csv(OUTPUT_MASTER_CSV, index=False)
            print(f"\nSuccessfully saved the cleaned data to '{OUTPUT_MASTER_CSV}'")
        except Exception as e:
            print(f"\nError: Could not save the file. Reason: {e}")