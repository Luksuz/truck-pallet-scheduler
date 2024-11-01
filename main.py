import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from collections import Counter
from typing import List, Tuple
from itertools import permutations

# Import your custom modules
from sleper import (
    check_total_area as sleper_check_total_area,
    pair_containers as sleper_pair_containers,
    find_optimal_assignment as sleper_find_optimal_assignment,
    visualize_assignment as sleper_visualize_assignment,
    MAIN_LENGTH,
    MAIN_WIDTH,
    CONTAINER_WIDTH,
    MIN_LENGTH,
    MAX_LENGTH,
    MAX_CONTAINERS
)
from kip import (
    check_total_area as kip_check_total_area,
    pair_containers as kip_pair_containers,
    find_optimal_assignment as kip_find_optimal_assignment,
    visualize_assignment as kip_visualize_assignment,
    MAIN_CONTAINERS
)

# Constants (Ensure these are defined in your modules)
# MAIN_LENGTH, MAIN_WIDTH, CONTAINER_WIDTH, MIN_LENGTH, MAX_LENGTH, MAX_CONTAINERS, MAIN_CONTAINERS

# Initialize session state for pallets
if 'pallets' not in st.session_state:
    st.session_state.pallets = [{'length': MIN_LENGTH, 'count': 1}]

def add_pallet():
    if len(st.session_state.pallets) < MAX_CONTAINERS:
        st.session_state.pallets.append({'length': MIN_LENGTH, 'count': 1})
    else:
        st.warning(f"Maximum of {MAX_CONTAINERS} pallets reached.")

def remove_pallet():
    if len(st.session_state.pallets) > 1:
        st.session_state.pallets.pop()
    else:
        st.warning("At least one pallet input is required.")

def main():
    st.set_page_config(page_title="📦 Container Packing Application", layout="wide")
    st.title("📦 Container Packing Application")

    st.markdown("""
    This application allows you to input the lengths and counts of pallets to determine the optimal packing strategy 
    using two different algorithms (`sleper` and `kip`). You can visualize the packing assignments and receive 
    feedback on the success of the packing process.
    """)

    st.sidebar.header("Pallet Configuration")

    # Buttons to add or remove pallets
    add_pallet_btn = st.sidebar.button("➕ Add Pallet", on_click=add_pallet)
    remove_pallet_btn = st.sidebar.button("➖ Remove Pallet", on_click=remove_pallet)

    st.header("Enter Pallet Details")

    # Display pallet inputs
    for idx, pallet in enumerate(st.session_state.pallets):
        with st.expander(f"Pallet {idx + 1}"):
            col1, col2 = st.columns(2)
            with col1:
                length_key = f'pallet_length_{idx}'
                st.session_state.pallets[idx]['length'] = st.number_input(
                    f"Pallet {idx + 1} Length (mm)",
                    min_value=MIN_LENGTH,
                    max_value=MAX_LENGTH,
                    value=pallet['length'],
                    step=1,
                    key=length_key
                )
            with col2:
                count_key = f'pallet_count_{idx}'
                st.session_state.pallets[idx]['count'] = st.number_input(
                    f"Pallet {idx + 1} Count",
                    min_value=1,
                    max_value=MAX_CONTAINERS,  # Adjust as needed
                    value=pallet['count'],
                    step=1,
                    key=count_key
                )

    st.markdown("---")

    if st.button("Execute Packaging"):
        execute_packing()

def execute_packing():
    st.markdown("### Execution Status")
    try:
        # Extract container lengths based on pallets
        container_lengths = []
        for idx, pallet in enumerate(st.session_state.pallets, start=1):
            length = pallet['length']
            count = pallet['count']
            if length < MIN_LENGTH or length > MAX_LENGTH:
                raise ValueError(f"Pallet {idx} length {length} mm is out of allowed range ({MIN_LENGTH}-{MAX_LENGTH} mm).")
            if count < 1:
                raise ValueError(f"Pallet {idx} count must be at least 1.")
            # Repeat the length based on count
            container_lengths.extend([length] * count)

        total_containers = len(container_lengths)
        if total_containers > MAX_CONTAINERS:
            raise ValueError(f"Total number of containers ({total_containers}) exceeds the maximum allowed ({MAX_CONTAINERS}).")

        st.success("Input validation successful.")
        st.write(f"**Total Containers:** {total_containers}")
        st.write(f"**Container Lengths (mm):** {container_lengths}")

        # First attempt: Try using sleper.py logic
        st.info("Attempting packing using **sleper.py** logic...")
        if sleper_check_total_area(container_lengths, CONTAINER_WIDTH, MAIN_LENGTH, MAIN_WIDTH):
            paired_containers, remaining_containers = sleper_pair_containers(container_lengths)
            try:
                assignments, column_heights, optimal_max_height = sleper_find_optimal_assignment(
                    paired_containers, remaining_containers, container_lengths, MAIN_LENGTH
                )
                st.success("Packing successful using **sleper.py** logic.")
                st.write(f"**Assignments:** {assignments}")

                # Visualize the assignment
                figures = sleper_visualize_assignment(container_lengths, assignments, MAIN_LENGTH, MAIN_WIDTH, CONTAINER_WIDTH)
                if figures:
                    for fig in figures:
                        # Ensure that both axes are scaled correctly
                        fig.axes[0].set_aspect('equal', adjustable='box')
                        st.pyplot(fig)
                else:
                    st.warning("Visualization function did not return any figures for sleper.py logic.")
                return
            except ValueError as e:
                st.warning(f"Sleper logic failed: {e}")
        else:
            st.warning("Total area check failed for sleper.py logic.")

        # Second attempt: Use kip.py logic
        st.info("Attempting packing using **kip.py** logic...")
        if kip_check_total_area(container_lengths, CONTAINER_WIDTH, MAIN_CONTAINERS):
            paired_containers, remaining_containers = kip_pair_containers(container_lengths)
            optimal_assignment, column_heights, optimal_max_height = kip_find_optimal_assignment(
                paired_containers, remaining_containers, container_lengths, MAIN_CONTAINERS
            )
            if optimal_assignment is not None:
                st.success("Packing successful using **kip.py** logic.")
                st.write(f"**Optimal Assignment:** {optimal_assignment}")

                # Visualize the assignment
                figures = kip_visualize_assignment(container_lengths, optimal_assignment, MAIN_CONTAINERS, paired_containers, CONTAINER_WIDTH)
                if figures:
                    for fig in figures:
                        # Ensure that both axes are scaled correctly
                        fig.axes[0].set_aspect('equal', adjustable='box')
                        st.pyplot(fig)
                else:
                    st.warning("Visualization function did not return any figures for kip.py logic.")
            else:
                st.error("No valid assignment found using **kip.py** logic.")
        else:
            st.error("The total surface area of the containers exceeds that of the main containers in **kip.py** logic.")

    except ValueError as ve:
        st.error(f"**Invalid Input:** {ve}")
    except Exception as ex:
        st.error(f"**Error:** An unexpected error occurred: {ex}")

if __name__ == "__main__":
    main()
