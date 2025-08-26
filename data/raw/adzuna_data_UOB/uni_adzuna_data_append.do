* --- Configuration ---
* 1. Set the directory where your .dta files are located.

local data_directory "/Users/thomastrainor-gilham/Downloads/adzuna_data/EwDS_extract"

* 2. Set the desired name for the output CSV file.
* The CSV will be saved in the same 'data_directory'.
local output_csv_name "appended_adzuna_data.csv"

* --- Script Start ---

* Set the working directory
cd "`data_directory'"

* Display status
display ""
display "{txt}-------------------------------------------------------"
display "{txt}Starting Stata .dta Append and CSV Export Script"
display "{txt}Data Directory: {res}`data_directory'"
display "{txt}Output CSV Name: {res}`output_csv_name'"
display "{txt}-------------------------------------------------------"
display ""

* Get a list of all .dta files in the directory
fs *.dta

* Initialize a flag to check if it's the first file
local first_file_processed 0

* Loop through each .dta file found
foreach file in `r(files)' {
    * Display which file is being processed
    display "{txt}Processing file: {res}`file'"

    if `first_file_processed' == 0 {
        * This is the first file, so simply load it
        use "`file'", clear
        local first_file_processed 1
        display "{txt}Loaded `file' as initial dataset."
    }
    else {
        * For subsequent files, append them to the master dataset
        append using "`file'"
        display "{txt}Appended `file' to the master dataset."
    }
}

* --- Post-Append Cleaning and Export ---

* Optional: Sort your data if desired
* sort ID_variable

* Optional: Drop duplicate observations if any were introduced
* duplicates drop, force // Use with caution, drops exact duplicate rows

* Optional: Save the appended .dta file (good practice for backup)
* save "appended_data.dta", replace

* Export the appended dataset to a CSV file
* 'replace' overwrites the file if it exists.
* 'nolabel' exports numeric codes instead of value labels for categorical variables.
* Use 'label' instead of 'nolabel' if you want the actual text labels.
export delimited using "`output_csv_name'", replace nolabel

display ""
display "{txt}-------------------------------------------------------"
display "{txt}Script Finished!"
display "{txt}All .dta files appended and exported to: "
display "{res}`data_directory'\\`output_csv_name'"
display "{txt}-------------------------------------------------------"

