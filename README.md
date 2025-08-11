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
|-- 📂 notebooks/           # Our Jupyter Notebooks with commentary and methodology rationales
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
The raw data for this project was collected via a custom web scraper built with Python and the Selenium library. The scraper was designed to gather job postings from Adzuna and Glassdoor based on a predefined set of keywords. The raw, scraped output from this process is stored in the `/data/raw/ directory`. Note: The scraper script itself is not included in this repository, as the primary focus is on the reproducible analytical pipeline that begins with the raw data files.
---

## The Analytical Pipeline

The analysis is conducted in a series of Jupyter Notebooks, which are designed to be run in numerical order.

**1. `01_data_cleaning_and_filtering.ipynb`**
* **Input:** Raw scraped CSV files from `/data/raw/`.
* **Process:** Merges all raw files, applies a two-layer keyword filter to isolate relevant data science and economics roles, and performs initial cleaning on location and salary data.
* **Output:** `master_focused_job_listings.csv` saved to `/data/processed/`.

**2. `02_feature_engineering_and_pca.ipynb`**
* **Input:** `master_focused_job_listings.csv`.
* **Process:**
    * Performs K-Means clustering on the one-hot encoded skill matrix to identify 7 core job archetypes.
    * Applies Principal Component Analysis (PCA) to the skill matrix to create uncorrelated "Super-Skill" components.
    * Creates and adds the `seniority` control variable.
    * Assembles the final datasets for analysis and modeling.
* **Outputs:**
    * `full_analysis_dataset.csv` (for descriptive analysis and visualisations).
    * `final_regression_dataset.csv` (the lean, numerical dataset for modeling).

**3. `03_regression_and_analysis.ipynb`**
* **Input:** `final_regression_dataset.csv`.
* **Process:**
    * Builds and evaluates the primary OLS regression model to quantify the salary impact of Super-Skills, archetypes, regions, and seniority.
    * Builds and evaluates benchmark models (KNN, Random Forest) for validation.
    * Generates the key charts and tables for the final dissertation.
* **Output:** All final visualisations saved to the `/outputs/figures/` directory.

 
**5. `[pengjin's_archetype analysis.ipynb]`**
* **Input:** `full_analysis_dataset.csv`.
* **Process:**
    * ....
* **Outputs:**
    * `....` (for descriptive analysis and visualizations).

**7. `[skillbuild analysis].ipynb`**
* **Input:** `...`.
* **Process:**
    * ...
* **Output:** All final visualisations saved to the `/outputs/figures/` directory.

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

To reproduce the full analysis, run the Jupyter Notebooks in the `/notebooks/` directory in numerical order. Ensure your raw data files are placed in the `/data/raw/` directory before starting.

---

## Key Libraries Used

* **Data Manipulation:** pandas, numpy
* **Web Scraping:** selenium
* **Machine Learning:** scikit-learn (KMeans, PCA, LinearRegression, RandomForestRegressor, etc.)
* **Statistical Modeling:** statsmodels (for OLS regression summary)
* **NLP:** spaCy
* **Visualisation:** matplotlib, seaborn
