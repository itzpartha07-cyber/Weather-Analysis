# NISER Automatic Weather Station — Data Analysis

**Course:** EPS101 &nbsp;|&nbsp; **Instructor:** Jayesh Mahendra Goyal &nbsp;|&nbsp; **Project:** #26

---

## Overview

This project analyses atmospheric measurements from the NISER Jatni Automatic Weather Station (AWS)
for the period **March–October 2025**, covering pre-monsoon, monsoon, and post-monsoon phases over
Bhubaneswar, Odisha.

Variables recorded at 15-minute intervals: temperature, relative humidity, atmospheric pressure,
wind speed, wind direction, solar radiation, and rainfall.

---

## Setup

```bash
pip install pandas matplotlib numpy
```

Place both CSV files in the same directory as `analysis.py`, then run:

```bash
python analysis.py
```

---

## What the script does

| Question | What it computes |
|----------|-----------------|
| Q1 | Daily means of all variables; daily total rainfall; time-series plots |
| Q2 | Global max and min values with timestamps for each variable |
| Q3 | Monthly max/min plots for all variables |
| Q4 | Month with highest total rainfall |
| Q5 | Specific humidity from RH; comparison of rainy vs winter months |
| Q6 | Diurnal (hourly mean) variation for the rainiest month |
| Q7 | Pressure drop detection — cyclone signature check |
| Q8 | Pressure at 10 km altitude via barometric formula; 24-hr plot |

---

## Key findings

- Peak temperature: **41.1 °C** on 28 March 2025 at 13:45
- Maximum rainfall month: **August 2025**
- No cyclone signature detected — only typical monsoon low-pressure systems
- Clear semi-diurnal pressure oscillation (~2 mbar amplitude) visible in August diurnal plot
- Specific humidity in August (~0.022–0.0245 kg/kg) vs October (~0.018–0.0225 kg/kg)

---

## Data format

CSV files exported from a Campbell Scientific datalogger. The header spans 4 rows —
the script skips to row index 2 automatically. `NAN` entries in wind direction are
handled via `pd.to_numeric(..., errors="coerce")` during load.

### Variables and units

| Column | Variable | Unit |
|--------|----------|------|
| `WS_ms_Avg` | Wind speed (avg) | m/s |
| `WindDir` | Wind direction | degrees |
| `AirTemp_C_Avg` | Air temperature (avg) | °C |
| `RH_Avg` | Relative humidity (avg) | % |
| `Rain_mm_Tot` | Rainfall (total per interval) | mm |
| `SlrW_Avg` | Solar radiation (avg) | W/m² |
| `BP_mbar_Avg` | Barometric pressure (avg) | mbar |

---

## Formulae used

### Specific humidity (Q5)

Using the Tetens approximation for saturation vapour pressure:

```
es = 6.112 * exp(17.67 * T / (T + 243.5))   # saturation vapour pressure (hPa)
e  = (RH / 100) * es                          # actual vapour pressure
q  = 0.622 * e / (P - 0.378 * e)             # specific humidity (kg/kg)
```

### Pressure at altitude (Q8)

```
P(z) = P0 * exp(-z / H)    # H = 8400 m (scale height used)
```

---
