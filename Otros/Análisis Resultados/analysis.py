'''
    BP Device Analysis Script based on the Bland–Altman method and other metrics.
    Jorge F. García-Samartín
    www.gsamartin.es
    2025-10-21
'''

# Re-run analysis template with fixes:
# - Improved automatic pair detection (avoid Patient_ID pairing)
# - Removed failing attempt to save the running script source
# - Graceful execution and clear generated output listing
import os, math, numpy as np, pandas as pd, matplotlib.pyplot as plt
from sklearn.metrics import mean_absolute_error, mean_squared_error
from scipy import stats

# Get current directory
current_dir = os.path.dirname(os.path.abspath(__file__)) + "/"

csv_path = current_dir + "results.csv"
out_dir = current_dir + "bp_analysis_outputs"
os.makedirs(out_dir, exist_ok=True)

df = pd.read_csv(csv_path)
print("Loaded file:", csv_path)
print("Dataframe shape:", df.shape)
print("Columns:\n", df.columns.tolist())

# Filter numeric columns and exclude patient/id columns
numeric_cols = [c for c in df.columns if pd.api.types.is_numeric_dtype(df[c])]
numeric_cols = [c for c in numeric_cols if not any(k in c.lower() for k in ['patient','id','subject','code'])]
print("\nNumeric candidate columns (excluding patient/id):", numeric_cols)

# Try targeted matching for common BP tokens
tokens = ['sys','dia','sbp','dbp','ppm','map','pp','pulse','heart']
pairs = []

for t in tokens:
    cols_with_t = [c for c in numeric_cols if t in c.lower()]
    if not cols_with_t:
        continue
    # look for 'real'/'meas' or 'measured'/'real' patterns
    real_cols = [c for c in cols_with_t if 'real' in c.lower() or 'ref' in c.lower() or 'manual' in c.lower() or 'true' in c.lower() or 'gold' in c.lower()]
    meas_cols = [c for c in cols_with_t if 'meas' in c.lower() or 'device' in c.lower() or 'robot' in c.lower() or 'sensor' in c.lower() or 'est' in c.lower()]
    # fallback: any two distinct cols with token
    if real_cols and meas_cols:
        for rc in real_cols:
            for mc in meas_cols:
                pairs.append((rc, mc))
    elif len(cols_with_t) >= 2:
        # try to pair Real vs Measured by suffix or order
        # prefer names containing 'real' or 'meas'
        # else pair first two
        pairs.append((cols_with_t[0], cols_with_t[1]))

# If still no pairs found, try to find direct Real vs Measured columns by suffix
if not pairs:
    for c in numeric_cols:
        for d in numeric_cols:
            if c==d: continue
            if ('real' in c.lower() and 'meas' in d.lower()) or ('real' in d.lower() and 'meas' in c.lower()) or ('ref' in c.lower() and 'meas' in d.lower()):
                pairs.append((c,d))
# Final fallback: pair first two numeric columns
if not pairs and len(numeric_cols) >= 2:
    pairs.append((numeric_cols[0], numeric_cols[1]))

# Deduplicate and ensure ref appears first when possible (prefer Real/Ref as first element)
uniq_pairs = []
for a,b in pairs:
    # promote real/ref to first position if detected
    if not any(k in a.lower() for k in ['real','ref','true','gold']) and any(k in b.lower() for k in ['real','ref','true','gold']):
        a,b = b,a
    if (a,b) not in uniq_pairs and (b,a) not in uniq_pairs:
        uniq_pairs.append((a,b))
pairs = uniq_pairs

print("\nDetected pairs to analyze:")
for p in pairs:
    print(" -", p)

if not pairs:
    raise SystemExit("No pairs found for analysis. Please inspect column names.")

# Functions
def lin_cc(x,y):
    x = np.asarray(x); y = np.asarray(y)
    mean_x = np.mean(x); mean_y = np.mean(y)
    s_x = np.var(x, ddof=1)
    s_y = np.var(y, ddof=1)
    cov_xy = np.cov(x,y, ddof=1)[0,1]
    r = cov_xy / (np.sqrt(s_x*s_y)) if s_x>0 and s_y>0 else np.nan
    ccc = (2 * cov_xy) / (s_x + s_y + (mean_x - mean_y)**2) if (s_x + s_y + (mean_x - mean_y)**2)!=0 else np.nan
    return ccc, r

def deming_tls(x,y):
    x = np.asarray(x); y = np.asarray(y)
    xm = x.mean(); ym = y.mean()
    X = np.vstack((x-xm, y-ym)).T
    C = np.cov(X, rowvar=False)
    vals, vecs = np.linalg.eigh(C)
    idx = np.argmax(vals)
    v = vecs[:, idx]
    if abs(v[0]) < 1e-12:
        slope = np.nan
    else:
        slope = v[1] / v[0]
    intercept = ym - slope * xm
    return slope, intercept

def bland_altman_stats(x,y):
    mean = (x+y)/2.0
    diff = x - y
    md = np.mean(diff)
    sd = np.std(diff, ddof=1)
    loa_low = md - 1.96*sd
    loa_high = md + 1.96*sd
    return mean, diff, md, sd, loa_low, loa_high

# Analysis loop
summary_rows = []
for (ref_col, dev_col) in pairs:
    # ensure both columns exist
    if ref_col not in df.columns or dev_col not in df.columns:
        continue
    data = df[[ref_col, dev_col]].dropna()
    x = data[ref_col].values; y = data[dev_col].values
    if len(x) < 2:
        continue
    mae = mean_absolute_error(x,y)
    rmse = math.sqrt(mean_squared_error(x,y))
    medae = np.median(np.abs(x-y))
    perc_error = np.mean(np.abs(x-y) / np.maximum(np.abs(x), 1e-6)) * 100.0
    pearson_r, pearson_p = stats.pearsonr(x,y)
    ccc, r_for_ccc = lin_cc(x,y)
    slope, intercept = deming_tls(x,y)
    mean_vals, diffs, md, sd, loa_low, loa_high = bland_altman_stats(x,y)
    spearman_r, spearman_p = stats.spearmanr(np.abs(diffs), mean_vals)
    
    # save figures
    base_name = f"{ref_col}_vs_{dev_col}".replace(" ", "_")
    # Scatter
    plt.figure(figsize=(6,6))
    plt.scatter(x,y,s=40,alpha=0.7)
    mn = min(np.nanmin(x), np.nanmin(y)); mx = max(np.nanmax(x), np.nanmax(y))
    pad = 0.05*(mx-mn) if mx>mn else 1
    id_x = np.linspace(mn-pad, mx+pad, 100)
    plt.plot(id_x, id_x, linestyle='--', linewidth=1, label='Identity (y = x)')
    if not np.isnan(slope):
        plt.plot(id_x, slope*id_x + intercept, linestyle='-', linewidth=1.5, label=f'Deming/TLS: y={slope:.3f}x+{intercept:.2f}')
    plt.xlabel(f"Reference ({ref_col}) [mmHg]")
    plt.ylabel(f"Device ({dev_col}) [mmHg]")
    plt.title(f"Scatter: {ref_col} vs {dev_col}")
    plt.legend()
    plt.axis('square')
    plt.tight_layout()
    scatter_path = os.path.join(out_dir, f"{base_name}_scatter.png")
    plt.savefig(scatter_path, dpi=200); plt.close()
    
    # Bland-Altman
    plt.figure(figsize=(6,5))
    plt.scatter(mean_vals, diffs, s=40, alpha=0.7)
    plt.axhline(md, linestyle='-', label=f'Mean diff = {md:.2f} mmHg')
    plt.axhline(loa_high, linestyle='--', label=f'+1.96 SD = {loa_high:.2f} mmHg')
    plt.axhline(loa_low, linestyle='--', label=f'-1.96 SD = {loa_low:.2f} mmHg')
    try:
        slope_ba, intercept_ba, r_val_ba, p_val_ba, std_err_ba = stats.linregress(mean_vals, diffs)
        xreg = np.linspace(np.nanmin(mean_vals), np.nanmax(mean_vals), 100)
        plt.plot(xreg, slope_ba*xreg + intercept_ba, color='tab:green', linewidth=1, label=f'Reg diff~mean (slope={slope_ba:.3f})')
    except Exception:
        slope_ba = np.nan
    plt.xlabel("Mean of measurements [mmHg]")
    plt.ylabel("Reference - Device [mmHg]")
    plt.title(f"Bland–Altman: {ref_col} vs {dev_col}")
    plt.legend()
    plt.tight_layout()
    ba_path = os.path.join(out_dir, f"{base_name}_bland_altman.png")
    plt.savefig(ba_path, dpi=200); plt.close()
    
    # Boxplot by ranges
    ranges = [(-1e9, 99), (100,129), (130,159), (160,1e9)]
    labels = ['<100', '100-129', '130-159', '>=160']
    groups = []
    for lo,hi in ranges:
        mask = (mean_vals>lo) & (mean_vals<=hi)
        groups.append(diffs[mask])
    plt.figure(figsize=(7,4))
    plt.boxplot(groups, labels=labels, showmeans=True)
    plt.xlabel("Reference mean range (mmHg)")
    plt.ylabel("Reference - Device error (mmHg)")
    plt.title(f"Error by pressure range: {ref_col} vs {dev_col}")
    plt.tight_layout()
    box_path = os.path.join(out_dir, f"{base_name}_box_ranges.png")
    plt.savefig(box_path, dpi=200); plt.close()
    
    # Histogram
    plt.figure(figsize=(6,4))
    plt.hist(diffs, bins=12)
    plt.xlabel("Reference - Device error (mmHg)")
    plt.ylabel("Count")
    plt.title(f"Error histogram: {ref_col} vs {dev_col}")
    plt.tight_layout()
    hist_path = os.path.join(out_dir, f"{base_name}_error_hist.png")
    plt.savefig(hist_path, dpi=200); plt.close()
    
    # Save paired CSV
    out_df = pd.DataFrame({
        "reference": x, "device": y, "mean_ref_dev": mean_vals, "diff_ref_minus_dev": diffs
    })
    out_df_path = os.path.join(out_dir, f"{base_name}_paired.csv")
    out_df.to_csv(out_df_path, index=False)
    
    summary_rows.append({
        "reference_col": ref_col,
        "device_col": dev_col,
        "n_pairs": len(x),
        "mean_ref": np.mean(x),
        "mean_dev": np.mean(y),
        "mean_diff_ref_minus_dev": md,
        "sd_diff": sd,
        "loa_low": loa_low,
        "loa_high": loa_high,
        "MAE_mmHg": mae,
        "RMSE_mmHg": rmse,
        "MedAE_mmHg": medae,
        "Percent_error_mean_%": perc_error,
        "Pearson_r": pearson_r,
        "Pearson_p": pearson_p,
        "Lins_CCC": ccc,
        "Deming_slope": slope,
        "Deming_intercept": intercept,
        "Spearman_absdiff_vs_mean_r": spearman_r,
        "Spearman_p": spearman_p
    })

# Summary table
summary_df = pd.DataFrame(summary_rows)
summary_csv = os.path.join(out_dir, "summary_metrics.csv")
summary_df.to_csv(summary_csv, index=False)

# Calculate deciles for errors in sys, dia, and ppm
print("\n" + "="*80)
print("DECILES ANALYSIS FOR ERRORS (1st, 5th, 7th, 9th)")
print("="*80)

decile_results = []
for (ref_col, dev_col) in pairs:
    # Identify variable type
    var_type = None
    if any(t in ref_col.lower() for t in ['sys', 'sbp']):
        var_type = 'SYS'
    elif any(t in ref_col.lower() for t in ['dia', 'dbp']):
        var_type = 'DIA'
    elif any(t in ref_col.lower() for t in ['ppm', 'pulse', 'heart']):
        var_type = 'PPM'
    
    if var_type and ref_col in df.columns and dev_col in df.columns:
        data = df[[ref_col, dev_col]].dropna()
        if len(data) > 0:
            errors = np.abs(data[ref_col].values - data[dev_col].values)
            deciles = np.percentile(errors, [10, 50, 70, 90])
            decile_results.append({
                'Variable': var_type,
                'Reference_Column': ref_col,
                'Device_Column': dev_col,
                'Decile_1': deciles[0],
                'Decile_5': deciles[1],
                'Decile_7': deciles[2],
                'Decile_9': deciles[3]
            })

if decile_results:
    decile_df = pd.DataFrame(decile_results)
    print(decile_df.to_string(index=False))
    print("\n" + decile_df.to_markdown(index=False))
    decile_csv = os.path.join(out_dir, "error_deciles_analysis.csv")
    decile_df.to_csv(decile_csv, index=False)
    print(f"\nError deciles saved to: {decile_csv}")
else:
    print("No SYS, DIA, or PPM columns found for error decile calculation.")

print("="*80 + "\n")

# Display summary to console
print("\n" + "="*80)
print("BP COMPARISON SUMMARY")
print("="*80)
print(summary_df.to_string(index=False))
print("="*80)

print("\nGenerated outputs saved to:", out_dir)
for f in sorted(os.listdir(out_dir)):
    print(" -", f)

print("\nSummary metrics saved to:", summary_csv)
print("\nDownload links:")
print(f"- Summary CSV: sandbox:{summary_csv}")
print(f"- Output folder: sandbox:{out_dir}")
