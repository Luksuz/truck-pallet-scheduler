import streamlit as st

# Import your custom modules
from sleper import (
    check_total_area as sleper_check_total_area,
    pair_containers as sleper_pair_containers,
    find_optimal_assignment as sleper_find_optimal_assignment,
    visualize_assignment as sleper_visualize_assignment,
)
from kip import (
    check_total_area as kip_check_total_area,
    pair_containers as kip_pair_containers,
    find_optimal_assignment as kip_find_optimal_assignment,
    visualize_assignment as kip_visualize_assignment,
)


MAIN_LENGTH = 13300  # Length of the main container
MAIN_WIDTH = 2400    # Width of the main container
CONTAINER_WIDTH = 1200  # Fixed width of incoming containers
MIN_LENGTH = 800    # Minimum length of incoming containers
MAX_LENGTH = 30360   # Maximum length of incoming containers
MAIN_CONTAINERS = [
    {"name": "Container A - Column 1", "max_length": 7100, "current_length": 0},
    {"name": "Container A - Column 2", "max_length": 7100, "current_length": 0},
    {"name": "Container B - Column 1", "max_length": 8000, "current_length": 0},
    {"name": "Container B - Column 2", "max_length": 8000, "current_length": 0}
]


# Constants (Ensure these are defined in your modules)
# MAIN_LENGTH, MAIN_WIDTH, CONTAINER_WIDTH, MIN_LENGTH, MAX_LENGTH, MAX_CONTAINERS, MAIN_CONTAINERS

# Initialize session state for pallets
if 'pallets' not in st.session_state:
    st.session_state.pallets = [{'length': MIN_LENGTH, 'count': 1}]

def add_pallet():
    st.session_state.pallets.append({'length': MIN_LENGTH, 'count': 1})


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
    using two different permutation algorithms. You can visualize the packing assignments and receive 
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

        # First attempt: Try using sleper.py logic
        st.info("Attempting packing using the main truck...")
        if sleper_check_total_area(container_lengths, CONTAINER_WIDTH, MAIN_LENGTH, MAIN_WIDTH):
            paired_containers, remaining_containers = sleper_pair_containers(container_lengths)
            try:
                assignments, column_heights, optimal_max_height = sleper_find_optimal_assignment(
                    paired_containers, remaining_containers, container_lengths, MAIN_LENGTH
                )
                st.success("Packing successful using the main truck.")
                st.write(f"Space taken in first row: {column_heights[0]}")
                st.write(f"Space taken in second row: {column_heights[1]}")

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
                st.warning(f"Cannot execute packing the main truck: {e}")
        else:
            st.warning("Total surface area of the pallets exceeds the container surface, trying tandem truck packing.")

        # Second attempt: Use kip.py logic
        st.info("Attempting packing using tandem truck")
        if kip_check_total_area(container_lengths, CONTAINER_WIDTH, MAIN_CONTAINERS):
            paired_containers, remaining_containers = kip_pair_containers(container_lengths)
            optimal_assignment, column_heights, optimal_max_height = kip_find_optimal_assignment(
                paired_containers, remaining_containers, container_lengths, MAIN_CONTAINERS
            )
            if optimal_assignment is not None:
                st.success("Packing successful using tandem truck.")

                # Visualize the assignment
                figures = kip_visualize_assignment(container_lengths, optimal_assignment, MAIN_CONTAINERS, paired_containers, CONTAINER_WIDTH)
                if figures:
                    for fig in figures:
                        # Ensure that both axes are scaled correctly
                        fig.text(0.65, 0.6, f"right side = {column_heights.pop(0)} mm")
                        fig.text(0.65, 0.5, f"left side = {column_heights.pop(0)} mm")
                        fig.axes[0].set_aspect('equal', adjustable='box')
                        st.pyplot(fig)
                else:
                    st.warning("Visualization function did not return any figures for tandem truck.")
            else:
                st.error("No valid assignment found using tandem truck logic.")
        else:
            st.error("The total surface area of the containers exceeds that of tandem truck spaces.")

    except ValueError as ve:
        st.error(f"**Invalid Input:** {ve}")
    except Exception as ex:
        st.error(f"**Error:** An unexpected error occurred: {ex}")

if __name__ == "__main__":
    main()
