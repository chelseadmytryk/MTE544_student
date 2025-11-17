import matplotlib.pyplot as plt
from utilities import FileReader

def plot_errors(filename):
    # Read headers and data from CSV
    headers, values = FileReader(filename).read_file()
    title = filename.split('e_')[-1].replace('.csv', '')
    title = title.replace('_', '.')
    title = title.replace('part', 'Part ')
    # Get indices of the required columns
    odom_x_idx = headers.index("odom_x")
    odom_y_idx = headers.index("odom_y")
    odom_th_idx = headers.index("odom_th")
    pf_x_idx = headers.index("pf_x")
    pf_y_idx = headers.index("pf_y")
    pf_th_idx = headers.index("pf_th")
    stamp_idx = headers.index("stamp")

    # Extract columns
    odom_x = [row[odom_x_idx] for row in values]
    odom_y = [row[odom_y_idx] for row in values]
    odom_th = [row[odom_th_idx] for row in values]
    pf_x = [row[pf_x_idx] for row in values]
    pf_y = [row[pf_y_idx] for row in values]
    pf_th = [row[pf_th_idx] for row in values]

    # Build time axis from ROS stamp (re-zero and scale)
    raw_times = [row[stamp_idx] for row in values]
    t0 = raw_times[0]
    time_list = [t - t0 for t in raw_times]

    # Simple heuristic to scale large ROS time values (e.g., ns or ms) to seconds
    max_dt = max(time_list) if time_list else 0.0
    if max_dt > 1e6:
        # likely nanoseconds
        time_list = [dt / 1e9 for dt in time_list]
    elif max_dt > 1e3:
        # likely milliseconds
        time_list = [dt / 1e3 for dt in time_list]

    # Create figure with two subplots: positions and theta comparison
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    fig.suptitle(f"{title}")
    # Position plot: odom vs particle filter in x-y
    axes[0].plot(odom_x, odom_y, color="green", label="Odometry")
    axes[0].plot(pf_x, pf_y, color="red", label="Particle Filter")
    axes[0].set_xlabel("x position [m]")
    axes[0].set_ylabel("y position [m]")
    axes[0].set_title("Particle Filter vs Odometry Position Tracking")
    axes[0].legend()
    axes[0].grid(True)

    # Theta comparison plot: theta (rad) vs time (s), time on y-axis
    axes[1].plot(time_list, odom_th, color="green", label="Odometry θ")
    axes[1].plot(time_list, pf_th, color="red", label="Particle Filter θ")
    axes[1].set_ylabel("theta [rad]")
    axes[1].set_xlabel("time [s]")
    axes[1].set_title("Particle Filter vs Odometry Orientation Tracking")
    axes[1].legend()
    axes[1].grid(True)

    plt.tight_layout()
    plt.show()


import argparse

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process some files.")
    parser.add_argument("--files", nargs="+", required=True, help="List of files to process")

    args = parser.parse_args()

    print("plotting the files", args.files)

    filenames = args.files
    for filename in filenames:
        plot_errors(filename)
