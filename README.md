# IBM 1 Dissertation Project: A Data-Driven Skills Strategy for IBM

##  Project Overview

This repository contains the full codebase and analytical pipeline for the MSc Economics with Data Science dissertation, "Future-Proofing the UK Workforce: A Data-Driven Skills Strategy for IBM". The project analyses over 4,500 UK job postings to identify key job archetypes, quantify the economic value of specific skill sets, and provide strategic recommendations for IBM's SkillsBuild program.

Our core research question is: 
<code style="color: aqua">***How can IBM use its SkillsBuild platform to target future economics & data science skill gaps, focusing on different demographics and regions?***</code>

---

## Folder Structure

The project is organized into a standard data science structure to ensure clarity and reproducibility:

```
/dissertation_project/
|
|-- 📂 data/                # All datasets
|   |-- 📂 raw/             # Original, untouched scraped data
|   |-- 📂 processed/       # Cleaned and engineered datasets
|   |-- 📂 external/        # External data (e.g., ONS population stats)
|
|-- 📂 notebooks/           # Our Notebooks with commentary & methodology rationales
|
|-- 📂 outputs/             # All final outputs from the analysis
|   |-- 📂 figures/         # Final charts and plots (.png)
|   |-- 📂 tables/          # Final summary tables (.csv)
|
|-- readme.md            
|-- requirements.txt     # List of required Python libraries
```

---
## Data Collection 

The raw data for this project was collected via a custom web scraper built with Python 
and the Selenium library. The scraper was designed to gather job postings from Adzuna and Glassdoor based on a predefined set of keywords. The raw, scraped output from this process is stored in the `/data/raw/ directory`. Note: The scraper script itself is not included in this repository, as the primary focus is on the reproducible analytical pipeline that begins with the raw data files.

---

## The Analytical Pipeline

The analysis is conducted in a series of Jupyter Notebooks, which are designed to be run in numerical order.

### **1. `01_data_cleaning_and_filtering.ipynb`**
* **Input:** Raw scraped CSV files from `/data/raw/`.
* **Process:** Merges all raw files, performs a multi-tiered imputation for missing salary and date data, and applies a two-layer keyword filter to isolate relevant data science and economics roles.
* **Output:** `master_cleaned_job_listings_final_v2.csv` saved to `/data/processed/joblisting_processed_data`.

### **2. `02_feature_engineering_and_pca.ipynb`**
* **Input:** `master_cleaned_job_listings_final_v2.csv`.
* **Process:**
    * Performs K-Means clustering on the one-hot encoded skill matrix to identify 7 core job archetypes.
    * Applies Principal Component Analysis (PCA) to the skill matrix to create uncorrelated "Super-Skill" components.
    * Creates and adds the `seniority` control variable.
    * Assembles the final datasets for analysis and modeling.
* **Outputs:**
    * `master_enriched_job_listings_dataset.csv` (for descriptive analysis and visualisations).
    * `final_modelling_dataset_WITH_NOISE.csv` and `final_modelling_dataset_NO_NOISE.csv`(the numerical datasets for regression).

### **3. `03_regression_and_analysis.ipynb`**
* **Input:** `final_modelling_dataset.csv`.
* **Process:**
    * Systematically runs and compares four different OLS regression models to ensure robustness:
       * Model A: With "Noise" cluster, full data.
       * Model B: With "Noise" cluster, sensitivity analysis (non-imputed salary).
       * Model C: No "Noise" cluster, full data (the final, preferred model).
       * Model D: No "Noise" cluster, sensitivity analysis.
    * Builds and evaluates the primary semi-log OLS model (Model C) to quantify the salary impact of Super-Skills, archetypes, regions, and seniority.
    * Builds and evaluates benchmark models (KNN, Random Forest) for validation.
    * Generates the key charts and tables for the final dissertation.
* **Output:** All final visualisations saved to the `/outputs/figures/` directory.

### **4. `04_archetype_analysis.ipynb`**
* **Input:** `master_enriched_job_listings_dataset.csv`.
* **Process:** Conducts a deep-dive descriptive analysis into the seven core job archetypes. This includes profiling their top technical skills, soft skills, "Super-Skill" compositions (via heatmaps and radar charts), and salary distributions (via violin plots)
* **Outputs:** All archetype profile visualisations saved to /outputs/figures/.

### **5. `05_regional_analysis.ipynb` & `05.1_region_interactive_maps.ipynb`**
* **Input:** `master_enriched_job_listings_dataset.csv` and external ONS population data
* **Process:** Performs the geographic analysis of the UK job market. This includes creating the per-capita job archetype maps and the regional salary heatmaps to identify local skill hotspots and economic disparities.
* **Output:** All regional charts and maps saved to /outputs/figures/

### **6. `06_IBM_skills_gap_analysis.ipynb`**
* **Input:** `skillsbuild_courses_cleaned.csv` from /data/raw/ and `master_enriched_job_listings_dataset.csv` from /data/processed/
* **Process:**
   * Ingests and cleans the raw IBM SkillsBuild course data.
   * Tags each course with the same granular skill lexicon and "Super-Skill" components used in the job market analysis.
   * Merges the "supply" data (IBM courses) with the "demand" data (job market) to calculate the skills gap.

* **Output:** The final Skills Gap Matrix and strategic bubble charts saved to /outputs/figures/
---

## How to Run This Project

### Prerequisites

* Python 3.9+
* Conda or another virtual environment manager (recommended)

### Installation

1.  **Clone the repository:**
    ```bash
    git clone [your-repo-url]
    cd dissertation_project
    ```

2.  **Create and activate a virtual environment:**
    ```bash
    conda create --name ibm-dissertation python=3.9
    conda activate ibm-dissertation
    ```

3.  **Install the required packages:**
    ```bash
    pip install -r requirements.txt
    ```

### Execution

To reproduce the full analysis, run the Jupyter Notebooks in the `/notebooks/` directory in numerical order. Ensure raw data files are placed in the `/data/raw/` directory before starting.

---

## Key Libraries Used

* **Data Manipulation:** pandas, numpy
* **Web Scraping:** selenium
* **Machine Learning:** scikit-learn (KMeans, PCA, LinearRegression, RandomForestRegressor, etc.)
* **Statistical Modeling:** statsmodels (for OLS regression summary)
* **NLP:** spaCy
* **Visualisation:** matplotlib, seaborn, folium (for interactive maps)
* **Table Generation:** stargazer (for final regression tables), dataframe_image
