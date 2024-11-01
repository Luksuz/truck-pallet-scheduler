import itertools
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from collections import Counter
from typing import List, Tuple

# Constants for the two main containers
def check_total_area(container_lengths: List[int], container_width: int, main_containers: List[dict]) -> bool:
    """
    Checks if the total area of incoming containers fits within the combined area of main containers.
    """
    total_container_area = sum([length * container_width for length in container_lengths])
    total_main_area = sum([mc["max_length"] * container_width for mc in main_containers])
    return total_container_area <= total_main_area

def pair_containers(container_lengths: List[int]) -> Tuple[List[Tuple[int, int]], List[int]]:
    """
    Groups containers with the same length into pairs and keeps remaining unpaired containers.

    Args:
        container_lengths (List[int]): List of container lengths.

    Returns:
        Tuple containing:
            - List of paired container indices as tuples.
            - List of remaining unpaired container indices.
    """
    length_count = Counter(container_lengths)
    paired_containers = []
    remaining_containers = []
    length_to_indices = {}

    # Map each length to its list of original indices
    for idx, length in enumerate(container_lengths):
        if length not in length_to_indices:
            length_to_indices[length] = []
        length_to_indices[length].append(idx)

    # Pair containers by length
    for length, indices in length_to_indices.items():
        while len(indices) >= 2:
            paired_containers.append((indices.pop(0), indices.pop(0)))
        if indices:
            remaining_containers.append(indices.pop(0))

    return paired_containers, remaining_containers

def find_optimal_assignment(
    paired_containers: List[Tuple[int, int]], 
    remaining_containers: List[int], 
    container_lengths: List[int], 
    columns: List[dict]
):
    """
    Assigns containers to the available columns optimally.

    Args:
        paired_containers (List[Tuple[int, int]]): Paired container indices.
        remaining_containers (List[int]): Remaining unpaired container indices.
        container_lengths (List[int]): Original container lengths.
        columns (List[dict]): List of columns with their properties.

    Returns:
        Tuple[List[Tuple[int, int]], List[int], float]: 
            Assignments, column heights, and optimal max height.
    """
    num_columns = len(columns)
    column_heights = [col["current_length"] for col in columns]
    assignments = []  # List of tuples (container_idx, column_idx)

    # Assign paired containers first
    for pair in paired_containers:
        # Try to assign each container in the pair to different columns
        assigned = False
        for col1, col2 in itertools.combinations(range(num_columns), 2):
            len1 = container_lengths[pair[0]]
            len2 = container_lengths[pair[1]]
            if (column_heights[col1] + len1 <= columns[col1]["max_length"] and
                column_heights[col2] + len2 <= columns[col2]["max_length"]):
                assignments.append((pair[0], col1))
                assignments.append((pair[1], col2))
                column_heights[col1] += len1
                column_heights[col2] += len2
                assigned = True
                break
        if not assigned:
            print(f"Cannot assign paired containers {pair} without exceeding capacities.")
            return None, None, None

    print(f"Paired assignments after pairing step: {assignments}")
    print(f"Column heights after pairing: {column_heights}")

    # Assign remaining containers
    optimal_max_height = float('inf')
    optimal_assignment = None

    # Generate all possible assignments for remaining containers
    for assignment in itertools.product(range(num_columns), repeat=len(remaining_containers)):
        temp_heights = column_heights.copy()
        valid = True

        for idx, col in zip(remaining_containers, assignment):
            length = container_lengths[idx]
            temp_heights[col] += length
            if temp_heights[col] > columns[col]["max_length"]:
                valid = False
                break

        if valid:
            current_max = max(temp_heights)
            if current_max < optimal_max_height:
                optimal_max_height = current_max
                optimal_assignment = assignment

    print(f"Optimal assignment for remaining containers: {optimal_assignment}")
    print(f"Optimal max height: {optimal_max_height}")

    # Apply the optimal assignment to remaining containers
    if optimal_assignment is not None:
        for idx, col in zip(remaining_containers, optimal_assignment):
            assignments.append((idx, col))
            column_heights[col] += container_lengths[idx]
    else:
        print("No valid assignment found for remaining containers.")
        return None, None, None

    print(f"Final assignments after adding remaining containers: {assignments}")
    print(f"Final column heights: {column_heights}")

    return assignments, column_heights, optimal_max_height



def visualize_assignment(
    container_lengths: List[int], 
    assignments: List[Tuple[int, int]], 
    columns: List[dict], 
    paired_containers: List[Tuple[int, int]], 
    container_width: int
) -> List[plt.Figure]:
    """
    Visualizes the container assignments to the columns within main containers.
    Ensures that containers with the same length have the same color across all main containers.

    Args:
        container_lengths (List[int]): List of container lengths.
        assignments (List[Tuple[int, int]]): List of assignments as (container_idx, column_idx).
        columns (List[dict]): List of columns with their properties.
        paired_containers (List[Tuple[int, int]]): List of paired container indices.
        container_width (int): Fixed width of incoming containers.

    Returns:
        List[plt.Figure]: List of figures for each main container.
    """
    # Create a set of all paired container indices for quick lookup
    paired_set = set(itertools.chain.from_iterable(paired_containers))

    # Organize assignments by main container
    container_a_columns = [0, 1]  # Indices for Container A's columns
    container_b_columns = [2, 3]  # Indices for Container B's columns

    assignments_a = [assignment for assignment in assignments if assignment[1] in container_a_columns]
    assignments_b = [assignment for assignment in assignments if assignment[1] in container_b_columns]

    # Extract all unique lengths for color mapping
    unique_lengths = sorted(set(container_lengths))
    cmap = plt.get_cmap('tab20', len(unique_lengths))
    length_color_map = {length: cmap(i) for i, length in enumerate(unique_lengths)}

    # Function to plot a single main container
    def plot_main_container(assignments, main_container_columns, main_container_name):
        fig, ax = plt.subplots(figsize=(8, 6))  # Adjusted figure size for better clarity

        # Determine the maximum length among the columns for setting plot limits
        max_length = max([columns[col]["max_length"] for col in main_container_columns])
        ax.set_xlim(0, container_width * len(main_container_columns) + 100)  # Extra space for clarity
        ax.set_ylim(0, max_length)
        ax.set_xlabel('Width (mm)')
        ax.set_ylabel('Length (mm)')
        ax.set_title(f'Optimal Pallet Packing for {main_container_name}')

        # Draw the main container boundaries
        for col_idx in main_container_columns:
            col = columns[col_idx]
            x_offset = (col_idx % 2) * (container_width + 50)  # Adjusted spacing between columns
            main_rect = patches.Rectangle((x_offset, 0), container_width, col["max_length"],
                                          linewidth=2, edgecolor='black', facecolor='none')
            ax.add_patch(main_rect)

            # Draw containers within the column
            current_height = 0
            for assignment in assignments:
                container_idx, assigned_col = assignment
                if assigned_col != col_idx:
                    continue
                length = container_lengths[container_idx]
                color = length_color_map[length]
                is_paired = container_idx in paired_set
                rect = patches.Rectangle(
                    (x_offset, current_height),
                    container_width,
                    length,
                    linewidth=1,
                    edgecolor='blue' if not is_paired else 'red',
                    facecolor=color,
                    alpha=0.7
                )
                ax.add_patch(rect)
                # Annotate the container with its index
                ax.text(
                    x_offset + container_width / 2,
                    current_height + length / 2,
                    str(container_idx + 1),
                    ha='center',
                    va='center',
                    fontsize=8,
                    color='white'
                )
                if is_paired:
                    rect.set_edgecolor('red')
                    rect.set_linewidth(2)
                current_height += length

        # Create a legend for container lengths
        handles = [
            patches.Patch(color=color, label=f'Length {length} mm')
            for length, color in length_color_map.items()
        ]
        ax.legend(handles=handles, title='Container Lengths', bbox_to_anchor=(1.05, 1), loc='upper left')

        # Set aspect ratio to equal to maintain scaling
        ax.set_aspect('equal', adjustable='box')

        return fig

    # Plot Container A
    fig_a = plot_main_container(assignments_a, container_a_columns, "Tandem Truck")

    # Plot Container B
    fig_b = plot_main_container(assignments_b, container_b_columns, "Tandem Trailer")

    return [fig_a, fig_b]

