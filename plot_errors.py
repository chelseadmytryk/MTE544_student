import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection
import numpy as np
import os
from utilities import FileReader
import argparse

# ---------- helpers ----------
def _read_error_csv(path):
    headers, vals = FileReader(path).read_file()
    t0 = vals[0][-1]
    t = [(v[-1] - t0) / 1e9 for v in vals]     # seconds from 0
    e = [v[0] for v in vals]
    edot = [v[1] for v in vals]
    return np.array(t), np.array(e), np.array(edot)

def _read_pose_csv(path):
    headers, vals = FileReader(path).read_file()
    t0 = vals[0][-1]
    t = [(v[-1] - t0) / 1e9 for v in vals]     # seconds from 0
    x = [v[0] for v in vals]
    y = [v[1] for v in vals]
    th = [v[2] for v in vals]
    return np.array(t), np.array(x), np.array(y), np.array(th)

def _safe_markevery(n):
    return max(1, n // 25)

# ---------- main plotting ----------
def make_four_plots(folder):
    lin_path = os.path.join(folder, "linear.csv")
    ang_path = os.path.join(folder, "angular.csv")
    pose_path = os.path.join(folder, "robot_pose.csv")

    if not (os.path.exists(lin_path) and os.path.exists(ang_path) and os.path.exists(pose_path)):
        missing = [p for p in [lin_path, ang_path, pose_path] if not os.path.exists(p)]
        raise FileNotFoundError(f"Missing required CSV(s): {missing}")

    # read
    tL, eL, edotL = _read_error_csv(lin_path)
    tA, eA, edotA = _read_error_csv(ang_path)
    tP, x, y, th = _read_pose_csv(pose_path)

    # ---------- Figure 1: two subplots ----------
    # Subplot A: LINEAR { e–t , ė–t } overlaid
    fig1, axes = plt.subplots(1, 2, figsize=(8, 4), sharex=False)
    fig1.suptitle("Errors vs Time", fontsize=12, fontweight='bold')

    meL = _safe_markevery(len(tL))
    meA = _safe_markevery(len(tA))

    # A) Linear channel
    axes[0].plot(tL, eL,    linewidth=1, label="e(t)")
    axes[0].plot(tL, edotL, linewidth=1, color="red", label="ė(t)")
    axes[0].set_title("Linear Controller: {e(t) , ė(t)}")
    axes[0].set_xlabel("Time [s]"); axes[0].set_ylabel("Value")
    axes[0].grid(True, alpha=0.3); axes[0].legend()

    # B) Angular channel
    axes[1].plot(tA, eA,    linewidth=1, label="e(t)")
    axes[1].plot(tA, edotA, linewidth=1, color="red", label="ė(t)")
    axes[1].set_title("Angular Controller: {e(t) , ė(t)}")
    axes[1].set_xlabel("Time [s]"); axes[1].set_ylabel("Value")
    axes[1].grid(True, alpha=0.3); axes[1].legend()

    out1 = os.path.join(folder, "fig1_errors_linear_and_angular_pairs.png")
    fig1.tight_layout()
    fig1.savefig(out1, dpi=300, bbox_inches='tight')
    plt.tight_layout()
    plt.close(fig1)
    print(f"Saved: {out1}")

    # ---------- Figure 2: phase {e–ė} linear & angular overlaid ----------
    plt.figure(figsize=(5, 4))
    plt.plot(eL, edotL, linewidth=1, label="Linear: e vs ė")
    plt.plot(eA, edotA, linewidth=1, color="red", label="Angular: e vs ė")
    plt.title("Phase Plot {e – ė}", fontsize=12, fontweight='bold')
    plt.xlabel("Error e"); plt.ylabel("Error derivative ė")
    plt.grid(True, alpha=0.3); plt.legend()
    out2 = os.path.join(folder, "fig2_phase_e_vs_edot_overlaid.png")
    plt.tight_layout()
    plt.savefig(out2, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Saved: {out2}")

    # ---------- Figure 3: {x–t, y–t, θ–t} overlaid ----------
    plt.figure(figsize=(7, 4))
    meP = _safe_markevery(len(tP))
    plt.plot(tP, x,  linewidth=1, label="x(t)")
    plt.plot(tP, y,  linewidth=1, color="red", label="y(t)")
    plt.plot(tP, th, linewidth=1, color="green", label="θ(t)")
    plt.title("Robot Pose vs Time {x–t , y–t , θ–t}", fontsize=12, fontweight='bold')
    plt.xlabel("Time [s]"); plt.ylabel("Value [m or rad]")
    plt.grid(True, alpha=0.3); plt.legend()
    out3 = os.path.join(folder, "fig3_pose_x_y_theta_overlaid.png")
    plt.tight_layout()
    plt.savefig(out3, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Saved: {out3}")


    # ---------- Figure 4: {x–y} with time colorbar ----------
    fig, ax = plt.subplots(figsize=(6, 4))
    plt.title("Robot Trajectory (x–y)", fontsize=12, fontweight='bold')
    colors = plt.cm.viridis(np.linspace(0, 1, len(x)))
    for i in range(len(x) - 1):
        ax.plot([x[i], x[i+1]], [y[i], y[i+1]], color=colors[i], linewidth=2)

    # start/end markers
    ax.plot(x[0], y[0], 'go', markersize=9, label='Start', markeredgecolor='black')
    ax.plot(x[-1], y[-1], 'ro', markersize=9, label='End', markeredgecolor='black')

    # colorbar for time
    sm = plt.cm.ScalarMappable(cmap='viridis', norm=plt.Normalize(vmin=tP[0], vmax=tP[-1]))
    sm.set_array([])
    cbar = plt.colorbar(sm, ax=ax)
    cbar.set_label('Time [s]')

    ax.set_xlabel('x [m]')
    ax.set_ylabel('y [m]')
    ax.grid(True, alpha=0.3)
    ax.legend()
    ax.axis('equal')
    ax.autoscale()                 # autoscale to colored segments

    out4 = os.path.join(folder, "fig4_trajectory_xy.png")
    fig.tight_layout()
    plt.tight_layout()
    fig.savefig(out4, dpi=300, bbox_inches='tight')
    plt.close(fig)
    print(f"Saved: {out4}")



if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Produce the 4 required Lab 2 figures from CSV logs")
    parser.add_argument("--folder", required=True, help="Folder containing linear.csv, angular.csv, robot_pose.csv")
    args = parser.parse_args()
    make_four_plots(args.folder)