# El Salvador 2024 Census Analytics & K-Means++ Segmentation (`el-salvador-census-2024-segmentation`)

> **Strategic Repository Name:** `el-salvador-census-2024-segmentation`
> **GitHub Description:** `End-to-end demographic analytics & unsupervised K-Means++ segmentation of El Salvador's 2024 Census (10.51M records, 262 districts) with Star Schema SQL, 2D PCA & AG Grid.`
> **Topics:** `el-salvador` · `census-2024` · `kmeans-clustering` · `pca` · `python` · `star-schema` · `ag-grid` · `data-science-portfolio`

> **End-to-End Demographic & Econometric Data Science Analysis:** Direct ZIP-streamed aggregation across all **5 official El Salvador 2024 Census (`CPV2024SV`) microdata tables** (**6,029,976 individuals**, **1,920,668 households**, **2,270,026 dwellings**, **226,808 international emigrants**, and **63,267 recent mortality records** = **10,510,745 total census records**), benchmarked against **UN Population Division (1950–2100)** trajectories and analyzed across all **262 Districts** and **44 Restructured Municipalities** via **K-Means++**, **2D SVD PCA**, **Multivariate OLS (1,000 Bootstrap CIs)**, and **Labor Mobility / Vulnerability Scoring**.

![Demographic & Analytical Overview](images/dashboard_overview_preview.png)

- **Interactive AG Grid HTML5 Workbench:** [`index.html`](index.html)
- **Official Data Source:** [Banco Central de Reserva (BCR) / ONEC — VII Censo de Población y VI de Vivienda 2024 (Bases de Datos y Tabulados)](https://poblacion.bcr.gob.sv/pages/teg-base-de-datos-y-tabulados)
- **Reproducible Streaming, ML & Econometric Pipeline:** [`src/census_analysis.py`](src/census_analysis.py)
- **Aggregated District, Municipality & Statistical JSON:** [`data/census_summary.json`](data/census_summary.json)

---

## Table of Contents
1. [Analytical Scope & Research Questions](#1-analytical-scope--research-questions)
2. [Complete English Schema Across All 5 CPV 2024 Datasets](#2-complete-english-schema-across-all-5-cpv-2024-datasets)
3. [Methodological Architecture & External Demographic Benchmarks](#3-methodological-architecture--external-demographic-benchmarks)
4. [Exploratory Demographic, Infrastructure & Migration Findings](#4-exploratory-demographic-infrastructure--migration-findings)
5. [Unsupervised Machine Learning, OLS Regression & Vulnerability Analysis](#5-unsupervised-machine-learning-ols-regression--vulnerability-analysis)
6. [Key Analytical Takeaways & Methodological Caveats](#6-key-analytical-takeaways--methodological-caveats)
7. [Repository Structure & Reproducible Verification](#7-repository-structure--reproducible-verification)

---

## 1. Analytical Scope & Research Questions

In 2024, El Salvador completed its first national Population and Housing Census in 17 years (**CPV 2024**, following the 2007 census), coinciding with the country's territorial reorganization from **262 historical districts (*distritos*)** into **44 restructured municipalities** across **14 departments** (*Ley Especial para la Reestructuración Municipal*).

This empirical study investigates six core statistical and structural questions across all `10.51M` census records:
1. **Population Reconciliation & Demographic Transition:** How does El Salvador's enumerated 2024 population (**6,029,976**) reconcile between residential districts and institutional collective dwellings, and how does its age-sex structure compare to **UN Population Division (1950–2100)** medium-fertility and zero-migration trajectories?
2. **Household Asset Accumulation & Broadband Stratification:** Across **1,920,668 households** and **15 tracked assets**, which durables exhibit saturation versus sharp spatial divergence?
3. **Transnational Migration & the Remittance Mechanism:** How did the **2014–2024 emigration cohort (`226,808` individuals)** alter demographic aging and household capital formation across rural eastern and northern districts?
4. **Unsupervised K-Means++ District Typology:** Can 8 standardized continuous indicators across **262 districts** recover distinct structural regimes along human capital (`PC1`) and remittance/aging (`PC2`) axes?
5. **Econometric Validation (OLS + Bootstrap CIs):** Controlling for schooling, urbanization, and indoor piped water, what is the isolated partial effect of remittance incidence on household wealth and broadband adoption?
6. **Labor Commuting & Infrastructure Vulnerability:** How do inter-municipal worker commuting outflows (`31.38%` nationally) and formal salaried employment (`57.99%`) covary with composite infrastructure deprivation?

---

## 2. Complete English Schema Across All 5 CPV 2024 Datasets

Because `Bases-Finales-CPV2024SV-CSV.zip` is **171.8 MB compressed (2.17 GB uncompressed)**, [`src/census_analysis.py`](src/census_analysis.py) streams all 5 CSV files directly from the ZIP archive in 500k–750k row chunks without extracting 2.17 GB onto disk.

| # | CSV Table in Archive | English Entity | Records | Columns | Primary Key | Foreign Join Key |
| :- | :--- | :--- | ---: | ---: | :--- | :--- |
| **1** | `Base de Datos de Viviendas - CPV 2024 SV.csv` | **Dwellings** | 2,270,026 | 35 | `COD_VIV` (14-char) | `DISTODESC` (6-char) |
| **2** | `Base de Datos de Hogares - CPV 2024 SV.csv` | **Households** | 1,920,668 | 36 | `COD_HOG` (16-char) | `COD_VIV` (14-char) |
| **3** | `Base de Datos de Población - CPV 2024 SV.csv` | **Population** | 6,029,976 | 90 | `COD_PER` (21-char) | `COD_HOG` (16-char) |
| **4** | `Base de Datos de Mortalidad - CPV 2024 SV.csv` | **Mortality (12m)** | 63,267 | 17 | `COD_MORT` (18-char) | `COD_HOG` (16-char) |
| **5** | `Base de Datos de Emigración Internacional - CPV 2024 SV.csv` | **Emigration (2014–24)** | 226,808 | 18 | `COD_EMIG` (18-char) | `COD_HOG` (16-char) |

### Key Data Engineering Reconciliation (`5,922,921 + 107,055 = 6,029,976`)
Auditing `DEPTODESC` and `DISTODESC` across `Viviendas` and `Población` surfaces an essential structural detail in the BCR microdata:
- **`5,922,921` residents** live across the **262 geographic districts** in Departments `01` through `14`.
- **`107,055` individuals** are recorded in **14 collective penitentiary records** (`V01_VIV = 2 [Collective]`, `V01_2_VIV_COLECTIVA = 3 [Penitentiary / Detention Center]`) assigned to special non-geographic code **`DEPTODESC = 15` (`DISTODESC = 150101`)** so institutional prison populations do not distort local municipal per-capita rates.
- Excluding `150101` prior to Z-score standardization prevents a 107,055-person zero-household outlier from distorting K-Means++ centroids.

---

## 3. Methodological Architecture & External Demographic Benchmarks

1. **[`datasets/population-growth-estimates-and-projections`](https://github.com/datasets/population-growth-estimates-and-projections) (UN Population Division, 1950–2100):**
   - Provides longitudinal country-level estimates and projection variants (*Medium Fertility*, *Zero Migration*, *Constant Fertility*).
   - Plotting CPV 2024's actual count (**6.03M**) against the UN's *Zero-Migration Counterfactual* (**~6.51M in 2024**) visually demonstrates how international out-migration and declining fertility (`0–4` cohort = `373,233` vs. `25–29` cohort = `540,516`) have flattened El Salvador's total population curve ahead of schedule.
2. **Sentinel-Cleaned Continuous Feature Engineering (`K-Means++`, `2D PCA` & `OLS Bootstrap`):**
   - Raw CPV 2024 binary and categorical fields encode `1 = Yes`, `2 = No`, and `9` or `99 = Unknown`. Running Euclidean clustering on raw integer codes would cluster districts on missing-value sentinels (`99`). Instead, [`src/census_analysis.py`](src/census_analysis.py) computes clean continuous district rates (`0–100%` and valid means) over non-missing denominators prior to Z-score standardization, K-Means++ (`k = 2..8`, 50 restarts), SVD PCA, and 1,000-resample OLS bootstrap regression.
3. **Top-5 vs. Bottom-5 Territorial Extremes & Relational Star Schema (`cpv2024_analytics`):**
   - Pairs an interactive **Overview & Regression Workbench** with a dynamic **Top 5 Leaders vs. Bottom 5 High-Vulnerability Extremes Matrix** across 4 census dimensions (*Adult Schooling Years*, *Household Durable Asset Index*, *Residential Broadband %*, and *International Remittance %*).
   - Normalizes the 5 raw CPV 2024 CSV database exports into a formal relational Star Schema ([`sql/cpv2024_star_schema.sql`](sql/cpv2024_star_schema.sql)) with 3 Dimension tables (`dim_geography`, `dim_dwellings`, `dim_households`), 3 Fact tables (`fact_population`, `fact_international_emigration`, `fact_mortality`), analytical SQL views (`vw_district_kmeans_features`, `vw_remittance_asset_paradox`), runtime `DistrictSchemaContract` checks, and deterministic **Spanish-to-English survey mappings** (`SPANISH_TO_ENGLISH_SENTENCES`).

---

## 4. Exploratory Demographic, Infrastructure & Migration Findings

### 4.1 Age-Sex Pyramid & UN Projection Comparison
![Demographic Pyramid and UN Projections](images/demographic_pyramid_and_un_projections.png)

- **Rapid Base Contraction:** The `0–4` age cohort (**373,233**, `6.19%` of population) is **31.0% smaller** than the peak `25–29` cohort (**540,516**, `8.96%`), confirming a sharp drop in total fertility toward replacement level.
- **Gender Asymmetry:** El Salvador's population is **52.55% female** (`3,168,895` females vs. `2,861,081` males), with the female share rising steadily past age 20 due to male-skewed international emigration and higher male external mortality.

### 4.2 Department Urbanization & Remittance Dependency
![Department Population and Remittances](images/department_population_and_remittances.png)

- **Metropolitan Concentration:** **San Salvador** (**1,563,371** residents across 19 districts, `96.2%` urban) and **La Libertad** (**765,879** residents across 22 districts, `81.8%` urban) together house **39.3% of El Salvador's residential population**.
- **Eastern & Northern Remittance Belt:** While **26.33%** of households receive international remittances nationally, household remittance penetration reaches **47.5% in La Unión**, **42.8% in Morazán**, **42.3% in Cabañas**, **40.3% in Chalatenango**, and **39.4% in San Miguel**.

### 4.3 Household Asset Penetration & The Digital Divide (`1,920,668` Households)
![Household Assets and Digital Divide](images/household_assets_digital_divide.png)

| Asset Tier | Census Indicator (`Hogares`) | Households Owning | National Penetration (%) |
| :--- | :--- | ---: | ---: |
| **Tier 1: Near-Universal Staples (>75%)** | Mobile Phone (`H02_7_HOG_CEL`) | 1,766,105 | **93.74%** |
| | Refrigerator (`H02_1_HOG_REFRI`) | 1,554,937 | **82.53%** |
| | Television (`H02_6_HOG_TV`) | 1,506,107 | **79.94%** |
| **Tier 2: Middle-Class & Digital Divide (25%–45%)** | Cable / Satellite TV (`H02_10_HOG_CABLETV`) | 786,567 | **41.75%** |
| | Residential Internet (`H02_11_HOG_INTERNET`) | 786,216 | **41.73%** |
| | Desktop / Laptop Computer (`H02_8_HOG_COMPU`) | 745,398 | **39.56%** |
| | Washing Machine (`H02_2_HOG_LAVADORA`) | 608,630 | **32.30%** |
| | Automobile / Pickup (`H02_13_HOG_AUTO`) | 530,147 | **28.14%** |
| | Tablet (`H02_9_HOG_TABLET`) | 500,457 | **26.56%** |
| **Tier 3: Discretionary & Transport (<25%)** | Microwave Oven (`H02_3_HOG_MICRO`) | 432,127 | **22.94%** |
| | Motorcycle (`H02_15_HOG_MOTOCICLETA`) | 330,929 | **17.56%** |
| | Bicycle for Transport (`H02_14_HOG_BICICLETA`) | 267,610 | **14.20%** |
| | Streaming Subscription (`H02_12_HOG_PLATAFORMAS`) | 243,076 | **12.90%** |
| | Electric Stove (`H02_4_HOG_COCINA`) | 147,952 | **7.85%** |
| | Air Conditioning (`H02_5_HOG_AC`) | 141,124 | **7.49%** |

### 4.4 International Emigration Trajectory (`2014–2024`, `N = 226,808`)
![International Emigration Trends](images/international_emigration_trends.png)

- **Destination Concentration:** **85.91% (`194,849`)** of emigrants relocated to the **United States**, followed by **Spain (`9,142`, 4.03%)**, **Italy (`4,468`, 1.97%)**, **Mexico (`3,997`, 1.76%)**, and **Canada (`2,543`, 1.12%)**.
- **Primary Drivers:** **Job Search / Employment (`129,172`, 56.95%)** dominates, followed by **Family Reunification (`33,731`, 14.87%)** and **Insecurity or Violence (`32,647`, 14.39%)**. Annual departures peaked in **2022 (`34,284`)** and **2023 (`34,168`)**.

---

## 5. Unsupervised Machine Learning, OLS Regression & Vulnerability Analysis

### 5.1 Selecting Optimal $k$ (WCSS Elbow & Silhouette Evaluation)
![Elbow and Silhouette Evaluation](images/elbow_silhouette_evaluation.png)

We standardized 8 continuous district-level indicators (`mean_schooling_yrs`, `literacy_rate_pct`, `mean_hh_assets`, `internet_hh_pct`, `piped_water_pct`, `firewood_cooking_pct`, `remittance_hh_pct`, `mean_age`) across all **262 districts** and evaluated K-Means++ across $k \in \{2, \dots, 8\}$ (50 random restarts per $k$):
- **$k = 2$** (`WCSS = 1,445.4`, `Silhouette = 0.2724`) provides a binary urban-versus-rural split.
- **$k = 4$** (`WCSS = 911.1`, `Silhouette = 0.2598`) captures the primary WCSS elbow before the Silhouette drop at $k = 5$ (`0.2249`), cleanly separating **transnational remittance towns (Cluster 3)** from **semi-urban commuter belts (Cluster 2)** and **high-vulnerability rural agricultural districts (Cluster 4)**.

### 5.2 Cluster Profiles & 2D SVD Principal Component Analysis
![District K-Means Clusters and PCA](images/district_kmeans_clusters_pca.png)

The first two principal components explain **77.91% of total variance across all 262 districts**:
- **`PC1` (53.70% variance):** Urban Human Capital, Broadband & Infrastructure Development (`+Schooling`, `+Assets`, `+Internet`, `-Firewood`).
- **`PC2` (24.21% variance):** Transnational Emigration, Remittances & Demographic Aging (`+Remittance %`, `+Mean Age`, `+Emigration Rate`).

| Cluster Persona | Districts ($n$) | Population | Households | Adult Schooling | Literacy % | Mean Assets (0–15) | Internet % | Piped Water % | Firewood % | Remittance % | Emigrants / 1k |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| **Cluster 1: Metropolitan Tech & High-Capital Hubs** | 32 | 2,475,756 (41.8%) | 814,848 | **9.69 yrs** | **94.31%** | **6.09** | **54.74%** | **70.40%** | **3.55%** | 24.22% | 34.76 |
| **Cluster 2: Semi-Urban Commuter & Industrial Corridors** | 84 | 1,779,703 (30.0%) | 567,967 | **7.57 yrs** | **90.00%** | **4.50** | **23.94%** | **38.48%** | **13.13%** | 20.63% | 33.92 |
| **Cluster 3: Remittance-Driven & Aging Transnational Towns** | 88 | 1,059,669 (17.9%) | 349,341 | **6.38 yrs** | **83.83%** | **5.03** | **31.09%** | **46.28%** | **15.65%** | **45.15%** | **68.90** |
| **Cluster 4: High-Vulnerability Rural Agricultural Districts** | 58 | 607,793 (10.3%) | 188,512 | **5.81 yrs** | **81.23%** | **3.96** | **14.89%** | **31.75%** | **32.68%** | 32.87% | 58.76 |

### Key Unsupervised ML Insight: The "Remittance Paradox" Between Cluster 2 and Cluster 3
Compare **Cluster 2 (Semi-Urban Commuter Corridors)** and **Cluster 3 (Remittance-Driven Transnational Towns)**:
- Cluster 3 is overwhelmingly rural (**20.84% urban** vs. **59.95% urban** in Cluster 2) and has lower formal schooling (**6.38 yrs** vs. **7.57 yrs**) and literacy (**83.83%** vs. **90.00%**).
- **Yet Cluster 3 owns MORE household appliances/assets (`5.03` vs. `4.50`), has +7.15 percentage points higher residential internet penetration (`31.09%` vs. `23.94%`), and +7.80 pp higher indoor piped water (`46.28%` vs. `38.48%`)!**
- **Why?** Because **45.15% of Cluster 3 households receive foreign remittances** (reaching `65%–72%` in landmark districts like *Intipucá*, *Concepción de Oriente*, and *Yayantique*), funding private household durable goods, home internet, and water upgrades despite low local formal schooling and an aging population (**35.04 yrs** mean age).

---

### 5.3 Econometric Validation: Multivariate OLS & 1,000-Resample Bootstrap CIs
![OLS Regression and Standardized Bootstrap Betas](images/regression_paradox_and_loadings.png)

To formally test the "Remittance Paradox" beyond unsupervised clustering, we fit multivariate OLS models across all **262 districts** with **1,000 non-parametric bootstrap resamples** (95% confidence intervals) predicting both **Household Assets (`0–15`)** and **Residential Broadband Penetration (%)**:

| Outcome Model | $R^2$ | Adj. $R^2$ | RMSE | Adult Schooling Std $\beta$ [95% CI] | Remittance HH % Std $\beta$ [95% CI] | Urbanization Std $\beta$ [95% CI] | Piped Water Std $\beta$ [95% CI] |
| :--- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| **Household Assets (`0–15`)** | **0.7908** | 0.7875 | 0.3601 | **`0.7092`** `[0.5987, 0.8171]` | **`0.7088`** `[0.6302, 0.7851]` | `0.2467` `[0.1483, 0.3310]` | `0.2461` `[0.1798, 0.3079]` |
| **Residential Broadband (%)** | **0.6313** | 0.6255 | 9.1588 | **`0.6913`** `[0.5677, 0.8094]` | **`0.5872`** `[0.4844, 0.6991]` | `0.2929` `[0.1906, 0.3940]` | `0.1012` `[0.0114, 0.1941]` |

- **Empirical Takeaway:** After controlling for urbanization, adult schooling, and piped water, **remittance incidence (`std β = 0.7088`) matches formal schooling (`std β = 0.7092`) as an equally powerful standardized predictor of private household asset accumulation**, and explains a substantial share of rural broadband adoption (`std β = 0.5872`).
- **Regression Residual Outliers (`Observed - OLS Predicted Assets`):**
  - *Top Positive Overperformers:* **Antiguo Cuscatlán (`+1.07`)**, **Anamorós (`+0.96`, 52.4% remittances)**, **El Sauce (`+0.83`, 56.9% remittances)**, **San Lorenzo (`+0.82`)**, and **Pasaquina (`+0.76`, 50.7% remittances)**.
  - *Top Negative Underperformers:* **San Ramón (`-0.84`)**, **San Juan Tepezontes (`-0.80`)**, **Verapaz (`-0.80`)**, **San Ildefonso (`-0.74`)**, and **Joateca (`-0.68`)**.

### 5.4 Infrastructure Deprivation, Labor Commuting & 10×10 Correlation Matrix
![Infrastructure Vulnerability, Labor Commuting and 10x10 Correlation Matrix](images/vulnerability_and_commuting_analysis.png)

Incorporating four previously untapped `Población` labor-mobility and migration fields (`P05_RESI_LUGAR`, `P19_ACTIV_CAT_OCUP`, `P21_ACTIV_HORAS_TRAB`, `P22_ACTIV_UBI_NEGOCIO`) alongside a composite **Infrastructure Vulnerability Index (`0–100`)** reveals four structural dynamics:
- **National Labor Mobility (`6.03M` Población microdata):** **31.38%** of employed workers commute outside their residential municipality, **57.99%** hold formal salaried jobs, mean workweek is **43.12 hrs**, and **6.21%** of residents lived in another municipality/country 5 years ago.
- **Bedroom Commuter Corridors vs. Remittance Autarky:** *Cuscatancingo* and *Soyapango* exhibit >49% outbound commuting alongside ~6–8% infrastructure vulnerability, whereas *Concepción de Oriente* shows near-minimal municipal commuting with heavy remittance reliance.
- **2D PCA Factor Loadings (`8` standardized inputs):** `PC1` weights heavily on literacy/schooling/assets/internet vs. firewood cooking; `PC2` is anchored by `remittance_hh_pct` (`+0.6640`) and `mean_age` (`+0.4154`), isolating transnational aging towns orthogonal to urban industrialization.

---

## 6. Key Analytical Takeaways & Methodological Caveats

1. **Two Distinct Orthogonal Axes of Territorial Inequality (`77.91%` PCA Variance):**
   - `PC1` (`53.70%`) captures classic human-capital and municipal service access (schooling, literacy, durable assets, broadband vs. firewood reliance), while `PC2` (`24.21%`) captures transnational remittance incidence (`+0.6640`) and demographic aging (`+0.4154`). One-dimensional urban–rural splits collapse Clusters 3 and 4 together despite their **12.28 pp remittance gap** (`45.15%` vs. `32.87%`) and **1.07-asset gap** (`5.03` vs. `3.96`).
2. **Remittances Act as a Private Substitute for Local Human Capital in Asset & Broadband Models:**
   - OLS bootstrap estimation confirms that district remittance incidence (`std β = 0.7088`) carries virtually identical standardized explanatory weight to formal adult schooling (`std β = 0.7092`) for household durables (`R² = 0.7908`), though infrastructure residuals highlight large local heterogeneity (`Antiguo Cuscatlán` at `+1.07` vs. `San Ramón` at `-0.84`).
3. **Labor Commuting Separates Urban Dormitory Belts from Core Hubs and Remittance Towns:**
   - Nationally, `31.38%` of employed individuals work outside their residential municipality, led by suburban metropolitan districts (`Cuscatancingo`, `Soyapango` at >49% outflow) with low infrastructure vulnerability (~6–8%), whereas rural eastern remittance hubs show high household assets alongside low inter-municipal labor commuting.
4. **Methodological Limitations & Explicit Analytical Tradeoffs:**
   - **Ecological Inference:** District-level OLS regressions (`N = 262`) measure cross-district macro covariation rather than individual household causal returns; micro-level household regressions on `1.92M` `Hogares` rows remain a natural follow-up.
   - **Equal-Weight District Estimation:** Both K-Means++ (`262` centroids) and OLS treat every district equally so populous metropolitan areas do not drown out peripheral districts, whereas headline KPI cards in [`index.html`](index.html) compute population/household-weighted totals.
   - **Cross-Sectional Censoring:** Emigration (`226,808` since 2014) reflects surviving household reports recorded in 2024 and excludes entire-household departures.

---

## 7. Repository Structure & Reproducible Verification

```text
el-salvador-census-2024-segmentation/
├── images/
│   ├── dashboard_overview_preview.png            # 4-panel demographic & cluster overview banner
│   ├── demographic_pyramid_and_un_projections.png # 2024 Age-Sex Pyramid + UN 1950-2100 curves
│   ├── department_population_and_remittances.png  # 14 Departments Urban/Rural & Remittance %
│   ├── household_assets_digital_divide.png        # 15 Household Asset penetration rates (1.92M HHs)
│   ├── international_emigration_trends.png        # 2014-2024 Emigration wave & primary causes
│   ├── elbow_silhouette_evaluation.png            # K-Means++ WCSS Elbow & Silhouette curve (k=2..8)
│   ├── district_kmeans_clusters_pca.png           # 262 Districts K-Means++ scatter & 2D SVD PCA
│   ├── regression_paradox_and_loadings.png        # OLS Model Fit & Standardized Bootstrap Betas
│   └── vulnerability_and_commuting_analysis.png   # Vulnerability vs Commuting & 10x10 Correlation Matrix
├── data/
│   └── census_summary.json                        # Aggregated metrics across 262 districts & 44 munis
├── sql/
│   └── cpv2024_star_schema.sql                    # Relational Star Schema DDL & analytical views
├── src/
│   └── census_analysis.py                         # Zero-extraction ZIP streaming, validation & ML/OLS
├── index.html                                     # Self-contained AG Grid Community HTML5 Workbench
├── verify.mjs                                     # Automated data reconciliation & HTML5 verification suite
├── PRODUCT.md                                     # Product context & surface mode specification
├── DESIGN.md                                      # Operate-mode design tokens & typography contract
├── .gitignore                                     # Excludes 171.8 MB raw CPV 2024 ZIP archive
└── README.md                                      # English Analytical Documentation & Schema Reference
```

### Run the Analysis, Verification & Publish to GitHub

```powershell
# 1. Stream all 5 CSVs from Bases-Finales-CPV2024SV-CSV.zip & regenerate all charts (~125-145s)
uv run --with pandas --with numpy --with matplotlib python src/census_analysis.py

# 2. Run the automated verification check (validates 6,029,976 population reconciliation, clusters, charts & HTML)
node verify.mjs

# 3. Publish as a standalone GitHub repository (excludes the 171.8 MB ZIP via .gitignore)
winget install --id Git.Git -e; winget install --id GitHub.cli -e
git init
git add .
git commit -m "Add El Salvador 2024 Census (10.51M records) K-Means++ segmentation, Star Schema SQL, and AG Grid dashboard"
gh auth login
gh repo create el-salvador-census-2024-segmentation --public --description "End-to-end demographic analytics & unsupervised K-Means++ segmentation of El Salvador's 2024 Census (10.51M records, 262 districts) with Star Schema SQL, 2D PCA & AG Grid." --source=. --remote=origin --push
```
