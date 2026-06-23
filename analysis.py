import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# ── config ─────────────────────────────────────────────
DATA_FILE  = "NISER_Jatni_2025_Min_15.csv"
START_DATE = "2025-03-01"
END_DATE   = "2025-10-31"


# ── load and clean ──────────────────────────────────────
def load_data(path):
    df = pd.read_csv(path, header=2)
    df = df.dropna(subset=["TS"]).copy()

    df.columns = [
        "timestamp", "record",
        "windspeed", "winddir",
        "temp", "humidity",
        "rain", "solar", "pressure"
    ]

    df["timestamp"] = pd.to_datetime(
        df["timestamp"], format="%d/%m/%y %H:%M"
    )

    num_cols = ["windspeed", "winddir", "temp",
                "humidity", "rain", "solar", "pressure"]
    for col in num_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df["date"] = df["timestamp"].dt.date
    return df


def filter_period(df, start, end):
    s = pd.to_datetime(start)
    e = pd.to_datetime(end)
    return df[(df["timestamp"] >= s) & (df["timestamp"] <= e)].copy()


# ── daily aggregates ────────────────────────────────────
def daily_stats(df):
    cols = ["temp", "humidity", "pressure", "windspeed", "winddir", "solar"]
    daily_mean = df.groupby("date")[cols].mean()
    daily_rain = df.groupby("date")["rain"].sum()
    return daily_mean, daily_rain


# ── Q1: time-series plots ───────────────────────────────
def plot_timeseries(daily_mean, daily_rain):
    xd = pd.to_datetime(daily_mean.index)
    xr = pd.to_datetime(daily_rain.index)

    labels = {
        "temp":      "Temperature (°C)",
        "humidity":  "Humidity (%)",
        "pressure":  "Pressure (mbar)",
        "windspeed": "Wind speed (m/s)",
        "winddir":   "Wind direction (°)",
        "solar":     "Solar radiation (W/m²)"
    }

    for col, ylabel in labels.items():
        fig, ax = plt.subplots(figsize=(11, 4))
        ax.plot(xd, daily_mean[col], lw=0.9, color="#2563eb")
        ax.set(title=f"Daily mean {ylabel} — Mar–Oct 2025",
               xlabel="Date", ylabel=ylabel)
        ax.tick_params(axis="x", rotation=45)
        ax.grid(True, alpha=0.3)
        fig.tight_layout()
        plt.show(block=False)

    # rainfall as bar chart
    fig, ax = plt.subplots(figsize=(11, 4))
    ax.bar(xr, daily_rain.values, color="#0ea5e9", width=0.8)
    ax.set(title="Daily total rainfall (mm) — Mar–Oct 2025",
           xlabel="Date", ylabel="Rainfall (mm)")
    ax.tick_params(axis="x", rotation=45)
    ax.grid(True, alpha=0.3, axis="y")
    fig.tight_layout()
    plt.show(block=False)

    # solar vs rainfall on twin axes
    fig, ax1 = plt.subplots(figsize=(11, 4))
    ax1.plot(xd, daily_mean["solar"], color="#f59e0b",
             lw=0.9, label="Solar (W/m²)")
    ax1.set_ylabel("Solar radiation (W/m²)", color="#f59e0b")
    ax2 = ax1.twinx()
    ax2.bar(xr, daily_rain.values, color="#0ea5e9",
            alpha=0.35, width=0.8, label="Rainfall (mm)")
    ax2.set_ylabel("Rainfall (mm)", color="#0ea5e9")
    ax1.set_title("Solar radiation vs daily rainfall — Mar–Oct 2025")
    ax1.tick_params(axis="x", rotation=45)
    fig.tight_layout()
    plt.show(block=False)


# ── Q2: global extremes ─────────────────────────────────
def global_extremes(df):
    variables = ["temp", "humidity", "pressure",
                 "windspeed", "winddir", "solar", "rain"]
    print("\n=== Q2  Global max / min ===\n")
    for var in variables:
        hi = df.loc[df[var].idxmax()]
        lo = df.loc[df[var].idxmin()]
        print(f"{var.upper()}")
        print(f"  max = {hi[var]:.3f}  at  {hi['timestamp']}")
        print(f"  min = {lo[var]:.3f}  at  {lo['timestamp']}")
        print()


# ── Q3: monthly max / min ───────────────────────────────
def plot_monthly_extremes(df):
    df = df.copy()
    df["month"] = df["timestamp"].dt.to_period("M")
    variables = ["temp", "humidity", "pressure",
                 "windspeed", "solar", "rain"]

    for var in variables:
        mo_max = df.groupby("month")[var].max()
        mo_min = df.groupby("month")[var].min()
        x = mo_max.index.to_timestamp()

        fig, ax = plt.subplots(figsize=(10, 4))
        ax.plot(x, mo_max.values, marker="o", label="Max", color="#e15c2b")
        ax.plot(x, mo_min.values, marker="o", label="Min", color="#2563eb")
        ax.set(title=f"Monthly max/min — {var} (2025)",
               xlabel="Month", ylabel=var.capitalize())
        ax.legend()
        ax.grid(True, alpha=0.3)
        fig.tight_layout()
        plt.show(block=False)


# ── Q4: rainiest month ──────────────────────────────────
def rainiest_month(df):
    df = df.copy()
    df["month"] = df["timestamp"].dt.to_period("M")
    totals = df.groupby("month")["rain"].sum()
    peak = totals.idxmax()
    print(f"\nQ4  Maximum rainfall month: {peak}  ({totals[peak]:.1f} mm)")
    return peak


# ── Q5: specific humidity ───────────────────────────────
def add_specific_humidity(df):
    T  = df["temp"]
    RH = df["humidity"]
    P  = df["pressure"]

    # Tetens formula for saturation vapour pressure (hPa)
    es = 6.112 * np.exp((17.67 * T) / (T + 243.5))
    e  = (RH / 100.0) * es
    q  = 0.622 * e / (P - 0.378 * e)

    df = df.copy()
    df["q"] = q
    return df


def coldest_month(df, exclude):
    df = df.copy()
    df["month"] = df["timestamp"].dt.to_period("M")
    monthly_t = df.groupby("month")["temp"].mean()
    if exclude in monthly_t.index:
        monthly_t = monthly_t.drop(exclude)
    chosen = monthly_t.idxmin()
    print(f"Q5  Winter month selected: {chosen}")
    return chosen


def plot_specific_humidity(df, rainy, winter):
    df = df.copy()
    df["month"] = df["timestamp"].dt.to_period("M")
    daily_q = df.groupby("date")["q"].mean()
    dates   = pd.to_datetime(daily_q.index)
    periods = dates.to_period("M")

    for label, mo, colour in [("Rainy",  rainy,  "#0ea5e9"),
                               ("Winter", winter, "#9333ea")]:
        mask = periods == mo
        fig, ax = plt.subplots(figsize=(10, 4))
        ax.plot(dates[mask], daily_q[mask],
                marker="o", ms=4, color=colour)
        ax.set(title=f"Q5  Daily mean specific humidity — {label} month ({mo})",
               xlabel="Date", ylabel="Specific humidity (kg/kg)")
        ax.grid(True, alpha=0.3)
        fig.tight_layout()
        plt.show(block=False)


# ── Q6: diurnal variation ───────────────────────────────
def plot_diurnal(df, month):
    df = df.copy()
    df["month"] = df["timestamp"].dt.to_period("M")
    df["hour"]  = df["timestamp"].dt.hour
    subset = df[df["month"] == month]

    variables = ["temp", "humidity", "solar", "pressure", "windspeed"]
    for var in variables:
        hourly = subset.groupby("hour")[var].mean()
        fig, ax = plt.subplots(figsize=(9, 4))
        ax.plot(hourly.index, hourly.values,
                marker="o", ms=4, color="#2563eb")
        ax.set(title=f"Q6  Diurnal variation of {var} — {month}",
               xlabel="Hour of day", ylabel=var.capitalize())
        ax.set_xticks(range(0, 24, 2))
        ax.grid(True, alpha=0.3)
        fig.tight_layout()
        plt.show(block=False)


# ── Q7: pressure-drop events (cyclone check) ────────────
def check_cyclone(df):
    d = df.sort_values("timestamp").copy()
    d["dp"] = d["pressure"].diff()
    drops = d[d["dp"] < -8]

    print("\n=== Q7  Large pressure drops (> 8 mbar per step) ===")
    if drops.empty:
        print("  None found — no cyclone signature detected.")
    else:
        print(drops[["timestamp", "pressure", "windspeed", "dp"]].to_string())


# ── Q8: pressure at 10 km ───────────────────────────────
def pressure_at_10km(df, date_str):
    day = df[df["timestamp"].dt.date == pd.to_datetime(date_str).date()]
    P0  = day["pressure"]

    # Barometric formula: P(z) = P0 * exp(-z / H), scale height H = 8400 m
    P10 = P0 * np.exp(-10_000 / 8_400)

    fig, ax = plt.subplots(figsize=(10, 4))
    ax.plot(day["timestamp"], P10, color="#e15c2b", lw=1.2)
    ax.set(title=f"Q8  Estimated pressure at 10 km — {date_str}",
           xlabel="Time", ylabel="Pressure (mbar)")
    ax.tick_params(axis="x", rotation=45)
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    plt.show(block=False)


# ── main ────────────────────────────────────────────────
def main():
    df = load_data(DATA_FILE)
    df = filter_period(df, START_DATE, END_DATE)

    daily_mean, daily_rain = daily_stats(df)

    plot_timeseries(daily_mean, daily_rain)   # Q1
    global_extremes(df)                       # Q2
    plot_monthly_extremes(df)                 # Q3

    rainy  = rainiest_month(df)               # Q4

    df_q   = add_specific_humidity(df)        # Q5
    winter = coldest_month(df_q, rainy)
    plot_specific_humidity(df_q, rainy, winter)

    plot_diurnal(df, rainy)                   # Q6
    check_cyclone(df)                         # Q7
    pressure_at_10km(df, "2025-07-15")        # Q8

    input("\nAll plots open — press ENTER to close.")


if __name__ == "__main__":
    main()
