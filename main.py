import streamlit as st
import matplotlib.pyplot as plt
from sleper import (
    check_total_area as sleper_check_total_area,
    pair_containers as sleper_pair_containers,
    find_optimal_assignment as sleper_find_optimal_assignment,
    visualize_assignment as sleper_visualize_assignment,
    MAIN_LENGTH, MAIN_WIDTH, CONTAINER_WIDTH, MIN_LENGTH, MAX_LENGTH, MAX_CONTAINERS
)
from kip import (
    check_total_area as kip_check_total_area,
    pair_containers as kip_pair_containers,
    find_optimal_assignment as kip_find_optimal_assignment,
    visualize_assignment as kip_visualize_assignment,
    MAIN_CONTAINERS
)

# Initialize session state for container lengths and number of containers
if 'num_containers' not in st.session_state:
    st.session_state.num_containers = 4  # Starting with 4 containers

if 'container_lengths' not in st.session_state:
    st.session_state.container_lengths = [MIN_LENGTH] * st.session_state.num_containers

def update_num_containers():
    num = st.session_state.num_containers
    current = len(st.session_state.container_lengths)
    if num > current:
        st.session_state.container_lengths += [MIN_LENGTH] * (num - current)
    elif num < current:
        st.session_state.container_lengths = st.session_state.container_lengths[:num]

def main():
    st.set_page_config(page_title="📦 Container Packing Application", layout="wide")
    st.title("📦 Container Packing Application")

    st.markdown("""
    This application allows you to input the lengths of containers and determine the optimal packing strategy 
    using two different algorithms (`sleper` and `kip`). You can visualize the packing assignments and receive 
    feedback on the success of the packing process.
    """)

    st.sidebar.header("Configuration")

    # Sidebar for number of containers
    num_containers = st.sidebar.number_input(
        "Number of Containers",
        min_value=1,
        max_value=MAX_CONTAINERS,
        value=st.session_state.num_containers,
        step=1,
        key='num_containers',
        on_change=update_num_containers
    )

    st.header("Enter Container Lengths (in mm)")

    # Create input fields for container lengths
    for i in range(st.session_state.num_containers):
        st.session_state.container_lengths[i] = st.number_input(
            f"Container {i+1} Length (mm)",
            min_value=MIN_LENGTH,
            max_value=MAX_LENGTH,
            value=st.session_state.container_lengths[i],
            step=1,
            key=f'container_{i}'
        )

    st.markdown("---")

    if st.button("Execute Packaging"):
        execute_packing()

def execute_packing():
    try:
        container_lengths = []
        for idx, length in enumerate(st.session_state.container_lengths, start=1):
            if length:
                if length < MIN_LENGTH or length > MAX_LENGTH:
                    raise ValueError(f"Container {idx} length {length} mm is out of allowed range ({MIN_LENGTH}-{MAX_LENGTH} mm).")
                container_lengths.append(int(length))
            else:
                raise ValueError(f"Container {idx} length is not provided.")

        if len(container_lengths) > MAX_CONTAINERS:
            raise ValueError(f"Number of containers exceeds the maximum allowed ({MAX_CONTAINERS}).")

        if sleper_check_total_area(container_lengths, CONTAINER_WIDTH, MAIN_LENGTH, MAIN_WIDTH):
            paired_containers, remaining_containers = sleper_pair_containers(container_lengths)
            try:
                assignments, column_heights, optimal_max_height = sleper_find_optimal_assignment(
                    paired_containers, remaining_containers, container_lengths, MAIN_LENGTH
                )

                # Visualize the assignment
                figures = sleper_visualize_assignment(container_lengths, assignments, MAIN_LENGTH, MAIN_WIDTH, CONTAINER_WIDTH)
                if figures:
                    for fig in figures:
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
