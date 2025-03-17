import pandas as pd
import plotly.graph_objects as go
from Bio import Phylo
from utils.color_utils import generate_location_colors, generate_mlst_colors

def create_tree_plot(tree_file, metadata_file, show_tip_labels, mlst_palette, location_palette):
    """Generates a rectangular phylogenetic tree plot with MLST heatmap, bootstrap support, and location colors."""
    # Load tree
    print("MLST Palette:", mlst_palette)  # ✅ Debug MLST palette
    print("Location Palette:", location_palette)  # ✅ Debug Location palette

    # Load tree
    try:
        tree = Phylo.read(tree_file, 'newick')
        print("Tree Loaded Successfully")
    except Exception as e:
        print(f"Tree Load Error: {e}")
        return 0 

    tree.root_at_midpoint()

    # Load metadata
    metadata = pd.read_csv(metadata_file, sep='\t')
    if 'taxa' not in metadata.columns or 'location' not in metadata.columns or 'MLST' not in metadata.columns:
        raise ValueError("Metadata file must contain 'taxa', 'location', and 'MLST' columns.")

    metadata['location'] = metadata['location'].fillna('Unknown')
    metadata['MLST'] = metadata['MLST'].fillna('Unknown')

    # ✅ Generate colors using proper function
    location_colors = generate_location_colors(metadata['location'], palette=location_palette)
    mlst_colors = generate_mlst_colors(metadata['MLST'], palette=mlst_palette)


    # Compute tree node coordinates
    x_coords = tree.depths(unit_branch_lengths=True)
    y_coords = {}
    max_y = 0

    def assign_coordinates(clade, x_start=0, y_start=0):
        nonlocal max_y
        branch_length = clade.branch_length if clade.branch_length else 0.0
        x_current = x_start + branch_length

        if clade.is_terminal():
            x_coords[clade] = x_current
            y_coords[clade] = y_start
            max_y = max(max_y, y_start)
            return y_start + 1
        else:
            y_positions = []
            for child in clade.clades:
                y_start = assign_coordinates(child, x_current, y_start)
                y_positions.append(y_start - 1)

            x_coords[clade] = x_current
            y_coords[clade] = sum(y_positions) / len(y_positions)
            return y_start

    assign_coordinates(tree.root)

    # Set dynamic figure size based on the tree structure
    num_tips = sum(1 for _ in tree.get_terminals())  # Number of leaf nodes (taxa)
    max_label_length = max((len(clade.name) for clade in tree.get_terminals() if clade.name), default=10)

    # Dynamically adjust width and height
    height = max(800, num_tips * 25)  # Ensure enough space for tips
    width = max(1000, 800 + (max_label_length * 10))  # Ensure enough space for long labels

    # Set position for MLST heatmap squares
    mlst_x_position = max(x_coords.values()) + 0.02  

    # Lists for plot traces
    tree_line_traces = []
    bootstrap_markers = []
    tip_markers = []
    mlst_markers = []

    seen_locations = set()  
    seen_mlst = set()  

    # ** Add Legend Titles as Dummy Scatters **
    location_legend_title = go.Scatter(
        x=[None], y=[None], mode="markers",
        marker=dict(size=0, opacity=0),
        name="<b>Location</b>",
        showlegend=True
    )

    mlst_legend_title = go.Scatter(
        x=[None], y=[None], mode="markers",
        marker=dict(size=0, opacity=0),
        name="<b>MLST</b>",
        showlegend=True
    )

    # ** Draw Tree Branches as Scatter Lines **
    for clade in tree.find_clades(order='level'):
        x_start = x_coords[clade]
        y_start = y_coords[clade]

        if clade.clades:
            y_positions = [y_coords[child] for child in clade.clades]
            # Vertical line
            tree_line_traces.append(go.Scatter(
                x=[x_start, x_start], y=[min(y_positions), max(y_positions)],
                mode='lines', line=dict(color='black', width=2), showlegend=False
            ))
            # Horizontal lines
            for child in clade.clades:
                x_end = x_coords[child]
                y_end = y_coords[child]
                tree_line_traces.append(go.Scatter(
                    x=[x_start, x_end], y=[y_end, y_end],
                    mode='lines', line=dict(color='black', width=2), showlegend=False
                ))

        # Add bootstrap support markers (black diamonds) for nodes with confidence > 0.9
        if clade.confidence and clade.confidence > 0.9:
            bootstrap_markers.append(go.Scatter(
                x=[x_start], y=[y_start], mode='markers',
                marker=dict(size=12, color='black', symbol='diamond'),
                hoverinfo='text', text=f"Bootstrap: {clade.confidence}",
                showlegend=False
            ))

    # ** Draw Tip Markers Last (To Ensure They Appear on Top) **
    for clade in tree.get_terminals():
        x, y = x_coords[clade], y_coords[clade]
        meta_row = metadata[metadata['taxa'] == clade.name]

        if not meta_row.empty:
            location = meta_row['location'].iloc[0]
            mlst_value = meta_row['MLST'].iloc[0]
            color = location_colors.get(location, 'gray')
            mlst_color = mlst_colors.get(mlst_value, 'gray')

            show_location_legend = location not in seen_locations
            if show_location_legend:
                seen_locations.add(location)

            # **Conditionally render tip labels based on show_tip_labels**
            if show_tip_labels:
                tip_markers.append(go.Scatter(
                    x=[x], y=[y], mode='markers+text',
                    marker=dict(size=16, color=color, line=dict(width=2, color='black')),  
                    name=location if show_location_legend else None, 
                    text=f"{clade.name}",
                    textposition="middle right", textfont=dict(size=10), 
                    hoverinfo='text', showlegend=show_location_legend
                ))
            else:
                tip_markers.append(go.Scatter(
                    x=[x], y=[y], mode='markers',
                    marker=dict(size=16, color=color, line=dict(width=2, color='black')),  
                    name=location if show_location_legend else None, 
                    hoverinfo='text', showlegend=show_location_legend
                ))

            show_mlst_legend = mlst_value not in seen_mlst
            if show_mlst_legend:
                seen_mlst.add(mlst_value)

            mlst_markers.append(go.Scatter(
                x=[mlst_x_position], y=[y], mode='markers',
                marker=dict(size=20, color=mlst_color, symbol='square',
                    line=dict(width=2, color='black')),
                name=f"{mlst_value}" if show_mlst_legend else None,
                hoverinfo='text', text=f"MLST: {mlst_value}",
                showlegend=show_mlst_legend
            ))

    layout = go.Layout(
        title='Phylogenetic Tree with MLST Heatmap, Bootstrap Support, and Location Legend',
        xaxis=dict(title='Evolutionary Distance', showgrid=False, zeroline=False, range=[0, mlst_x_position + 0.01]),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False, range=[-1, max_y + 1]),
        height=height, width=width, plot_bgcolor="rgb(240, 240, 250)"
    )

    # ** Order Matters: Draw Tree Lines First, Then Bootstrap, Then Tip Markers Last **
    return go.Figure(
        data=[location_legend_title] + tree_line_traces + bootstrap_markers + tip_markers + [mlst_legend_title] + mlst_markers,
        layout=layout
    )
