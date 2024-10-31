import numpy as np
import itertools
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from collections import Counter
from typing import List, Tuple
from itertools import permutations

# Constants
MAIN_LENGTH = 13600  # Length of the main container
MAIN_WIDTH = 2400    # Width of the main container
CONTAINER_WIDTH = 1200  # Fixed width of incoming containers
MIN_LENGTH = 1500    # Minimum length of incoming containers
MAX_LENGTH = 13060   # Maximum length of incoming containers
INCREMENT = 5        # Length increment for containers
MAX_CONTAINERS = 10  # Maximum number of containers for feasibility

def check_total_area(container_lengths: List[int], container_width: int, main_length: int, main_width: int) -> bool:
    """
    Check if the total surface area of containers exceeds the main container's area.
    """
    total_container_area = sum([length * container_width for length in container_lengths])
    main_container_area = main_length * main_width
    return total_container_area <= main_container_area

def pair_containers(container_lengths: List[int]) -> Tuple[List[Tuple[int, int]], List[int]]:
    """
    Groups containers with the same length into pairs and keeps remaining unpaired containers.
    """
    length_count = Counter(container_lengths)
    paired_containers = []
    remaining_containers = []
    length_to_indices = {}

    # Prepare a mapping of lengths to indices
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
    max_length: int, 
    num_columns=2
) -> Tuple[List[Tuple[int, int]], List[int], int]:
    """
    Assign containers to columns, prioritizing paired containers first.
    If pairing fails, try all permutations of all containers without pairing.
    """
    assignments = []
    column_heights = [0] * num_columns

    # Attempt to assign paired containers
    try:
        if paired_containers:
            paired_assignments, column_heights = assign_paired_containers(paired_containers, container_lengths, num_columns)
            assignments.extend(paired_assignments)

        # Assign remaining containers
        if remaining_containers:
            remaining_assignments, column_heights = assign_remaining_containers(
                remaining_containers, container_lengths, column_heights, max_length, num_columns
            )
            assignments.extend(remaining_assignments)

        optimal_max_height = max(column_heights)
        return assignments, column_heights, optimal_max_height

    except ValueError:
        # If assignment with pairing fails, try all permutations of all containers
        print("Pairing failed, trying all permutations of all containers...")
        all_containers = list(range(len(container_lengths)))
        optimal_max_height = float('inf')
        optimal_assignment = None

        for perm in permutations(all_containers):
            temp_heights = [0] * num_columns
            valid = True
            temp_assignments = []

            for idx in perm:
                # Try to assign to the column with the least height
                col = min(range(num_columns), key=lambda c: temp_heights[c])
                temp_heights[col] += container_lengths[idx]
                if temp_heights[col] > max_length:
                    valid = False
                    break
                temp_assignments.append((idx, col))

            if valid:
                current_max = max(temp_heights)
                if current_max < optimal_max_height:
                    optimal_max_height = current_max
                    optimal_assignment = temp_assignments

        if optimal_assignment is not None:
            column_heights = [sum(container_lengths[idx] for idx, col in optimal_assignment if col == c) for c in range(num_columns)]
            return optimal_assignment, column_heights, optimal_max_height
        else:
            raise ValueError("No valid assignment found for all containers even with permutations.")

def assign_paired_containers(paired_containers: List[Tuple[int, int]], container_lengths: List[int], num_columns: int) -> Tuple[List[Tuple[int, int]], List[int]]:
    """
    Assign paired containers to columns in an alternating fashion.
    """
    column_heights = [0] * num_columns
    assignments = []

    for pair in paired_containers:
        for i, idx in enumerate(pair):
            col = i % num_columns  # Alternate between columns for pairing
            assignments.append((idx, col))
            column_heights[col] += container_lengths[idx]

    return assignments, column_heights

def assign_remaining_containers(remaining_containers: List[int], container_lengths: List[int], column_heights: List[int], max_length: int, num_columns: int) -> Tuple[List[Tuple[int, int]], List[int]]:
    """
    Assign remaining unpaired containers to columns using a brute-force approach to find the optimal assignment.
    """
    if not remaining_containers:
        return [], column_heights.copy()

    optimal_max_height = float('inf')
    optimal_assignment = None

    # Generate all possible assignments for remaining containers
    for assignment in itertools.product(range(num_columns), repeat=len(remaining_containers)):
        temp_heights = column_heights.copy()
        valid = True

        for idx, col in zip(remaining_containers, assignment):
            temp_heights[col] += container_lengths[idx]
            if temp_heights[col] > max_length:
                valid = False
                break

        if valid:
            current_max = max(temp_heights)
            if current_max < optimal_max_height:
                optimal_max_height = current_max
                optimal_assignment = assignment

    if optimal_assignment is not None:
        final_assignments = []
        for idx, col in zip(remaining_containers, optimal_assignment):
            final_assignments.append((idx, col))
            column_heights[col] += container_lengths[idx]
        return final_assignments, column_heights
    else:
        raise ValueError("No valid assignment found for remaining containers without exceeding column heights.")
    


def visualize_assignment(container_lengths: List[int], assignments: List[Tuple[int, int]], main_length: int, main_width: int, container_width: int):
    """
    Visualize the container assignments, highlighting paired containers.
    """
    num_columns = 2
    columns = [[] for _ in range(num_columns)]
    column_heights = [0] * num_columns

    # Organize containers into columns based on assignments
    for idx, col in assignments:
        columns[col].append(idx)
        column_heights[col] += container_lengths[idx]

    # Identify paired containers for visualization
    paired_indices = set()
    length_to_indices = {}
    for idx, length in enumerate(container_lengths):
        length_to_indices.setdefault(length, []).append(idx)

    for indices in length_to_indices.values():
        if len(indices) >= 2:
            paired_indices.update(indices[:2 * (len(indices) // 2)])

    # Create a new figure for visualization
    fig, ax = plt.subplots(figsize=(8, 6))
    ax.set_xlim(0, main_width)
    ax.set_ylim(0, main_length)
    ax.set_xlabel('Width')
    ax.set_ylabel('Length')
    ax.set_title('Optimal Container Packing Visualization')

    main_rect = patches.Rectangle((0, 0), main_width, main_length, linewidth=2, edgecolor='black', facecolor='none')
    ax.add_patch(main_rect)

    num_containers = len(container_lengths)
    cmap = plt.get_cmap('tab20', num_containers + 1)

    for col in range(num_columns):
        current_height = 0
        for idx in columns[col]:
            length = container_lengths[idx]
            rect = patches.Rectangle((col * container_width, current_height), 
                                     container_width, length, 
                                     linewidth=1, edgecolor='blue',
                                     facecolor=cmap(idx), alpha=0.6)
            # Highlight paired containers
            if idx in paired_indices:
                rect.set_edgecolor('red')
                rect.set_linewidth(2)
            ax.add_patch(rect)
            ax.text(col * container_width + container_width / 2, 
                    current_height + length / 2, 
                    str(idx + 1), 
                    ha='center', va='center', fontsize=8, color='white')
            current_height += length

    return [fig]

