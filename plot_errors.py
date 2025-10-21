import matplotlib.pyplot as plt
import numpy as np
import os
from utilities import FileReader


def plot_controller_errors(csv_path, controller_type):
    """
    Plot controller error data (angular or linear)
    """
    headers, values = FileReader(csv_path).read_file()
    
    # Calculate time values (convert from nanoseconds and normalize to start at 0)
    first_stamp = values[0][-1]
    time_list = [(val[-1] - first_stamp) / 1e9 for val in values]  # Convert to seconds
    
    # Extract error data
    error = [val[0] for val in values]
    error_dot = [val[1] for val in values]
    error_int = [val[2] for val in values]
    
    # Create the plot with 3 subplots
    fig, axes = plt.subplots(1, 3, figsize=(18, 6))
    fig.suptitle(f'{controller_type.title()} Controller Error Results', fontsize=16, fontweight='bold')
    
    # Subplot 1: Error vs Time
    axes[0].plot(time_list, error, 'b-', linewidth=2, label='Error')
    axes[0].set_xlabel('Time [s]')
    axes[0].set_ylabel('Error')
    axes[0].set_title('Error vs Time')
    axes[0].grid(True, alpha=0.3)
    axes[0].legend()
    
    # Subplot 2: Derivative Error vs Time
    axes[1].plot(time_list, error_dot, 'r-', linewidth=2, label='Derivative Error')
    axes[1].set_xlabel('Time [s]')
    axes[1].set_ylabel('Derivative Error')
    axes[1].set_title('Derivative Error vs Time')
    axes[1].grid(True, alpha=0.3)
    axes[1].legend()
    
    # Subplot 3: Error vs Derivative Error (Phase Plot)
    axes[2].plot(error, error_dot, 'g-', linewidth=2, label='Phase Plot')
    axes[2].set_xlabel('Error')
    axes[2].set_ylabel('Derivative Error')
    axes[2].set_title('Error vs Derivative Error')
    axes[2].grid(True, alpha=0.3)
    axes[2].legend()
    
    plt.tight_layout()
    
    # Save the plot
    output_path = os.path.join(os.path.dirname(csv_path), f'{controller_type}.png')
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Saved {controller_type} controller plot to: {output_path}")


def plot_robot_pose(csv_path):
    """
    Plot robot pose data with two separate figures
    """
    headers, values = FileReader(csv_path).read_file()
    
    # Calculate time values (convert from nanoseconds and normalize to start at 0)
    first_stamp = values[0][-1]
    time_list = [(val[-1] - first_stamp) / 1e9 for val in values]  # Convert to seconds
    
    # Extract pose data
    x_pos = [val[0] for val in values]
    y_pos = [val[1] for val in values]
    theta = [val[2] for val in values]
    
    # First figure: Robot Pose Data vs Time
    fig1, axes = plt.subplots(3, 1, figsize=(12, 10))
    fig1.suptitle('Robot Pose Data', fontsize=16, fontweight='bold')
    
    # X position vs time
    axes[0].plot(time_list, x_pos, 'b-', linewidth=2, label='X Position')
    axes[0].set_xlabel('Time [s]')
    axes[0].set_ylabel('X Position [m]')
    axes[0].set_title('X Position vs Time')
    axes[0].grid(True, alpha=0.3)
    axes[0].legend()
    
    # Y position vs time
    axes[1].plot(time_list, y_pos, 'r-', linewidth=2, label='Y Position')
    axes[1].set_xlabel('Time [s]')
    axes[1].set_ylabel('Y Position [m]')
    axes[1].set_title('Y Position vs Time')
    axes[1].grid(True, alpha=0.3)
    axes[1].legend()
    
    # Theta vs time
    axes[2].plot(time_list, theta, 'g-', linewidth=2, label='Theta Orientation')
    axes[2].set_xlabel('Time [s]')
    axes[2].set_ylabel('Theta [rad]')
    axes[2].set_title('Theta Orientation vs Time')
    axes[2].grid(True, alpha=0.3)
    axes[2].legend()
    
    plt.tight_layout()
    
    # Save the first plot
    output_path1 = os.path.join(os.path.dirname(csv_path), 'robot_pose.png')
    plt.savefig(output_path1, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Saved robot pose data plot to: {output_path1}")
    
    # Second figure: Robot Path Mapping with time gradient
    fig2, ax = plt.subplots(figsize=(10, 8))
    fig2.suptitle('Robot Path Mapping', fontsize=16, fontweight='bold')
    
    # Create a time-based color gradient
    colors = plt.cm.viridis(np.linspace(0, 1, len(x_pos)))
    
    # Plot the path with gradient coloring
    for i in range(len(x_pos) - 1):
        ax.plot([x_pos[i], x_pos[i+1]], [y_pos[i], y_pos[i+1]], 
                color=colors[i], linewidth=2)
    
    # Add start and end markers
    ax.plot(x_pos[0], y_pos[0], 'go', markersize=10, label='Start', markeredgecolor='black')
    ax.plot(x_pos[-1], y_pos[-1], 'ro', markersize=10, label='End', markeredgecolor='black')
    
    # Create colorbar to show time progression
    sm = plt.cm.ScalarMappable(cmap='viridis', norm=plt.Normalize(vmin=time_list[0], vmax=time_list[-1]))
    sm.set_array([])
    cbar = plt.colorbar(sm, ax=ax)
    cbar.set_label('Time [s]', fontsize=12)
    
    ax.set_xlabel('X Position [m]')
    ax.set_ylabel('Y Position [m]')
    ax.set_title('Robot Trajectory (Color = Time Progression)')
    ax.grid(True, alpha=0.3)
    ax.legend()
    ax.axis('equal')
    
    plt.tight_layout()
    
    # Save the second plot
    output_path2 = os.path.join(os.path.dirname(csv_path), 'robot_path_mapping.png')
    plt.savefig(output_path2, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Saved robot path mapping plot to: {output_path2}")


def process_folder(folder_path):
    """
    Process all CSV files in a folder and generate plots
    """
    if not os.path.isdir(folder_path):
        print(f"Error: {folder_path} is not a valid directory")
        return
    
    # Expected CSV files
    csv_files = {
        'linear.csv': 'linear',
        'angular.csv': 'angular',
        'robot_pose.csv': 'robot_pose'
    }
    
    for filename, plot_type in csv_files.items():
        csv_path = os.path.join(folder_path, filename)
        
        if os.path.exists(csv_path):
            print(f"Processing {filename}...")
            
            if plot_type in ['linear', 'angular']:
                plot_controller_errors(csv_path, plot_type)
            elif plot_type == 'robot_pose':
                plot_robot_pose(csv_path)
        else:
            print(f"Warning: {filename} not found in {folder_path}")


import argparse

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Generate plots from CSV data in a folder')
    parser.add_argument('--folder', required=True, help='Folder containing CSV files to process')
    
    args = parser.parse_args()
    
    print(f"Processing folder: {args.folder}")
    process_folder(args.folder)



