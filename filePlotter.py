# You can use this file to plot the loged sensor data
# Note that you need to modify/adapt it to your own files
# Feel free to make any modifications/additions here

import matplotlib as mpl
import matplotlib.pyplot as plt
from utilities import FileReader
from math import isfinite
import math
import os
import numpy as np

mpl.rcParams["savefig.bbox"] = "tight"       # trim on save by default
mpl.rcParams["savefig.pad_inches"] = 0.01    # tiny padding on save
mpl.rcParams["figure.constrained_layout.use"] = True  # pack subplots well

NS_TO_S = 1e-9


def _motion_from_filename(fname: str) -> str:
    f = fname.lower()
    for m in ("circle", "line", "spiral"):
        if m in f:
            return m
    return "unknown"

def _moving_avg(y, win=21):
    if win <= 1 or win % 2 == 0:
        return y
    k = win // 2
    # pad with edge values for same-length smoothing
    ypad = np.pad(y, (k, k), mode="edge")
    ker = np.ones(win) / win
    return np.convolve(ypad, ker, mode="valid")

def _extract_ranges_and_tail(row, headers):
    """Return (ranges:list[float], idx_after_ranges:int).
    idx_after_ranges points to the first column AFTER the closing '])' token."""
    r0 = headers.index("ranges")  # you have it
    # find the last column that belongs to 'ranges'
    rend = r0
    for j in range(r0, len(row)):
        s = str(row[j]).strip()
        rend = j
        if s.endswith("])") or s.endswith("])'") or "]" in s:
            # first cell containing the closing bracket—good enough for our messy CSV
            break
    # stitch tokens into one blob
    blob = " ".join(str(c) for c in row[r0:rend+1])
    # pull all float-like tokens
    toks = _FLOATS.findall(blob)
    ranges = []
    for t in toks:
        try:
            ranges.append(float(t))
        except Exception:
            pass
    return ranges, rend + 1  # next cell index

def plot_laser(filename):
    headers, values = FileReader(filename).read_file()
    if not values:
        print(f"[warn] '{filename}' has no data.")
        return

    row = values[0]  # one scan only (as per lab)
    print(f"Plotting first scan from '{filename}' with headers: {headers}")
    print(f"Row data: {row[:10]} ...")  # short preview

    # 1) ranges (stitched across columns)
    if "ranges" not in headers:
        print("[warn] no 'ranges' column header found.")
        return
    ranges, next_idx = _extract_ranges_and_tail(row, headers)
    if not ranges:
        print(f"[warn] couldn't parse numeric ranges from '{filename}'.")
        return

    # 2) angle_increment → next cell after ranges
    if next_idx >= len(row):
        print("[warn] angle_increment missing after ranges.")
        return
    try:
        angle_inc = float(row[next_idx])
    except Exception:
        # fallback: assume full 360° sweep
        angle_inc = 2 * math.pi / len(ranges)

    # 3) (optional) stamp → next cell after angle_increment
    # stamp_idx = next_idx + 1  # not required for plotting

    # Build angles with first beam at +x (per slide: arbitrary frame OK)
    N = len(ranges)
    angles = [i * angle_inc for i in range(N)]

    xs, ys = [], []
    for r, a in zip(ranges, angles):
        if math.isfinite(r):
            xs.append(r * math.cos(a))
            ys.append(r * math.sin(a))

    if not xs:
        print("[warn] all ranges are non-finite; nothing to plot.")
        return

    plt.figure()
    plt.scatter(xs, ys, s=5)
    plt.axis("equal")
    plt.xlabel("x [m]")
    plt.ylabel("y [m]")
    plt.title(f"Lidar scan (first message): {filename}")
    plt.grid(True)
    plt.show()


def plot_imu(filename):
    headers, values = FileReader(filename).read_file()
    if not values or not all(h in headers for h in ("acc_x","acc_y","angular_z","stamp")):
        print(f"[warn] '{filename}' missing required IMU columns.")
        return

    ax_i = headers.index("acc_x"); ay_i = headers.index("acc_y")
    wz_i = headers.index("angular_z"); ts_i = headers.index("stamp")

    t0 = float(values[0][ts_i])
    t  = np.array([(float(r[ts_i]) - t0) * NS_TO_S for r in values])
    ax = np.array([float(r[ax_i]) for r in values])
    ay = np.array([float(r[ay_i]) for r in values])
    wz = np.array([float(r[wz_i]) for r in values])

    motion = _motion_from_filename(filename)
    base   = os.path.splitext(os.path.basename(filename))[0]

    # --- Figure 1: RAW with title at top ---
    fig, axs = plt.subplots(3, 1, figsize=(6, 4), sharex=True, constrained_layout=True)
    axs[0].plot(t, ax, label="acc_x"); axs[0].set_ylabel("acc_x [m/s²]", labelpad=1); axs[0].grid(True, alpha=0.4); axs[0].legend(loc="best", frameon=False)
    axs[1].plot(t, ay, label="acc_y"); axs[1].set_ylabel("acc_y [m/s²]", labelpad=1); axs[1].grid(True, alpha=0.4); axs[1].legend(loc="best", frameon=False)
    axs[2].plot(t, wz, label="angular_z"); axs[2].set_xlabel("time [s]", labelpad=1); axs[2].set_ylabel("ω_z [rad/s]", labelpad=1); axs[2].grid(True, alpha=0.4); axs[2].legend(loc="best", frameon=False)
    for a in axs: a.margins(x=0); a.tick_params(length=3, pad=2)

    fig.suptitle(f"IMU Time Series — {motion}", fontsize=11)
    # give the suptitle a bit of headroom above the axes
    fig.subplots_adjust(top=0.93)

    fig.savefig(f"{base}_imu_timeseries.png", bbox_inches="tight", pad_inches=0.01, dpi=200)

    # --- Figure 2: SMOOTHED with title at top ---
    ax_s = _moving_avg(ax, win=21); ay_s = _moving_avg(ay, win=21); wz_s = _moving_avg(wz, win=21)

    fig2, axs2 = plt.subplots(2, 1, figsize=(6, 4), sharex=True, constrained_layout=True)
    axs2[0].plot(t, ax_s, label="acc_x (smoothed)")
    axs2[0].plot(t, ay_s, label="acc_y (smoothed)")
    axs2[0].set_ylabel("acc [m/s²]", labelpad=1); axs2[0].grid(True, alpha=0.4); axs2[0].legend(loc="best", frameon=False)
    axs2[1].plot(t, wz_s, label="angular_z (smoothed)")
    axs2[1].set_xlabel("time [s]", labelpad=1); axs2[1].set_ylabel("ω_z [rad/s]", labelpad=1); axs2[1].grid(True, alpha=0.4); axs2[1].legend(loc="best", frameon=False)
    for a in axs2: a.margins(x=0); a.tick_params(length=3, pad=2)

    fig2.suptitle(f"IMU Smoothed Signals — {motion}", fontsize=11)
    fig2.subplots_adjust(top=0.93)

    fig2.savefig(f"{base}_imu_smoothed.png", bbox_inches="tight", pad_inches=0.01, dpi=200)

    plt.show()

def plot_odom(filename):
    headers, values = FileReader(filename).read_file()
    if not values or not all(h in headers for h in ("x","y","th","stamp")):
        print(f"[warn] '{filename}' is missing x/y/theta/stamp.")
        return
    xi, yi = headers.index("x"), headers.index("y")
    ti = headers.index("th")
    si = headers.index("stamp")

    # Data
    xs = [float(r[xi]) for r in values]
    ys = [float(r[yi]) for r in values]
    th = [float(r[ti]) for r in values]
    t0 = float(values[0][si])
    time_s = [(float(r[si]) - t0) * NS_TO_S for r in values]

    motion = _motion_from_filename(filename)
    base = os.path.splitext(os.path.basename(filename))[0]

    # --- Figure 1: XY trajectory ---
    plt.figure(figsize=(4, 3.5))
    plt.plot(xs, ys, linewidth=1.3, label="trajectory")
    plt.axis("equal")
    plt.xlabel("x [m]")
    plt.ylabel("y [m]")
    plt.title(f"Odometry XY Path — {motion}")
    plt.grid(True, alpha=0.4)
    plt.legend(loc="best", frameon=False)
    plt.tight_layout()
    plt.savefig(f"{base}_xy.png", dpi=150)

    # Plot x, y, and theta over time in subplots for clarity
    # --- Figure 2: x, y, θ vs time ---
    fig, ax = plt.subplots(3, 1, figsize=(5, 4), sharex=True)
    ax[0].plot(time_s, xs, linewidth=1.2, label="x")
    ax[0].set_ylabel("x [m]")
    ax[0].grid(True, alpha=0.4)
    ax[0].legend(loc="upper right", frameon=False)

    ax[1].plot(time_s, ys, linewidth=1.2, label="y")
    ax[1].set_ylabel("y [m]")
    ax[1].grid(True, alpha=0.4)
    ax[1].legend(loc="upper right", frameon=False)

    ax[2].plot(time_s, th, linewidth=1.2, label=r"$\theta$")
    ax[2].set_xlabel("time [s]")
    ax[2].set_ylabel(r"$\theta$ [rad]")
    ax[2].grid(True, alpha=0.4)
    ax[2].legend(loc="upper right", frameon=False)

    fig.suptitle(f"Odometry Time Series — {motion}", y=0.9)
    fig.tight_layout(rect=[0, 0, 1, 0.96])
    fig.savefig(f"{base}_timeseries.png", dpi=150)

    # If you also want to show immediately:
    plt.show()

   
import argparse

if __name__=="__main__":

    parser = argparse.ArgumentParser(description='Process some files.')
    parser.add_argument('--files', nargs='+', required=True, help='List of files to process')
    
    args = parser.parse_args()
    
    print("plotting the files", args.files)
    
    # Determine file type and call appropriate plot function
    filenames=args.files
    for filename in filenames:
        print(f"Plotting file: {filename}")
        if "imu_content" in filename:
            plot_imu(filename)
        elif "odom_content" in filename:
            plot_odom(filename)
        elif "laser_content" in filename:
            plot_laser(filename)
        else:
            print(f"Unknown file type for: {filename}")
