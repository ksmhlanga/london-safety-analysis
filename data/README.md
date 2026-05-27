\# Data Directory



This directory contains all datasets used in the London Safety Analysis project.



\## Folder Structure



\### `/raw/`

Original, unmodified data from external sources.

\- \*\*Never edit files in this folder\*\*

\- Preserves data integrity and reproducibility



\### `/processed/`

Cleaned, transformed, and analysis-ready datasets.

\- All transformations documented in notebooks

\- Generated from `/raw/` data through reproducible scripts



\### `/external/`

Reference and supplementary data:

\- London borough boundary files (GeoJSON)

\- Postcode lookups

\- Population statistics

\- Other supporting datasets



---



\## Data Dictionary



\### Crime Data (`crime\_data\_2023\_2025.csv`)

\*Status: To be collected\*



| Column | Type | Description |

|--------|------|-------------|

| borough | string | London borough name |

| crime\_type | string | Type of crime (violence, burglary, etc.) |

| date | datetime | Month and year of incident |

| latitude | float | Location latitude |

| longitude | float | Location longitude |



\### School Ratings (`school\_ratings\_2024.csv`)

\*Status: To be collected\*



| Column | Type | Description |

|--------|------|-------------|

| school\_name | string | Official school name |

| borough | string | London borough |

| ofsted\_rating | string | Overall effectiveness rating |

| rating\_date | datetime | Date of inspection |



\### Healthcare Facilities (`nhs\_facilities\_2024.csv`)

\*Status: To be collected\*



\### Demographics (`ons\_demographics\_2021.csv`)

\*Status: To be collected\*



\### Property Prices (`land\_registry\_prices\_2023\_2025.csv`)

\*Status: To be collected\*



---



\*\*Last Updated:\*\* February 2026

