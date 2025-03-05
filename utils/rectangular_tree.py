import pandas as pd
import plotly.graph_objects as go
from Bio import Phylo
from utils.color_utils import generate_location_colors

def create_tree_plot(tree_file, metadata_file, show_tip_labels, height=None, width=None):
    """Generates a rectangular phylogenetic tree plot with improved tip label visibility."""

    # Load tree and metadata
    tree = Phylo.read(tree_file, 'newick')
    tree.root_at_midpoint()

    metadata = pd.read_csv(metadata_file, sep='\t')
    if 'taxa' not in metadata.columns or 'location' not in metadata.columns:
        raise ValueError("Metadata file must contain 'taxa' and 'location' columns.")

    metadata['location'] = metadata['location'].fillna('Unknown')
    location_colors = generate_location_colors(metadata['location'])

    x_coords = tree.depths(unit_branch_lengths=True)
    y_coords = {}
    max_y = 0

    def assign_coordinates(clade, x_start=0, y_start=0):
        """Assigns X and Y coordinates to nodes in a rectangular layout."""
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

    # Count the number of terminal nodes (tips)
    num_tips = sum(1 for clade in tree.get_terminals())

    # Calculate the longest label length for width adjustment
    max_label_length = max(len(clade.name) for clade in tree.get_terminals())

    # Adjust figure size dynamically
    height = max(1000, num_tips * 25) if height is None else height  # Scale height
    width = max(1200, max_label_length * 10) if width is None else width  # Scale width

    # Create branch lines
    line_shapes = []
    for clade in tree.find_clades(order='level'):
        x_start = x_coords[clade]
        y_start = y_coords[clade]

        if clade.clades:
            y_positions = [y_coords[child] for child in clade.clades]

            # Vertical connecting line
            line_shapes.append(dict(
                type='line', x0=x_start, y0=min(y_positions),
                x1=x_start, y1=max(y_positions),
                line=dict(color='black', width=3)
            ))

            # Horizontal branches
            for child in clade.clades:
                x_end = x_coords[child]
                y_end = y_coords[child]
                line_shapes.append(dict(
                    type='line', x0=x_start, y0=y_end,
                    x1=x_end, y1=y_end,
                    line=dict(color='black', width=3)
                ))

    # Create scatter points for tips & support values
    tip_markers = []
    node_markers = []
    seen_locations = set()

    max_x = max(x_coords.values())  # Find max x-value for tip label positioning

    for clade in tree.find_clades():
        x, y = x_coords[clade], y_coords[clade]
        if clade.is_terminal():
            meta_row = metadata[metadata['taxa'] == clade.name]
            location = meta_row['location'].iloc[0] if not meta_row.empty else 'Unknown'
            color = location_colors.get(location, 'gray')

            show_legend = location not in seen_locations
            if show_legend:
                seen_locations.add(location)

            # Ensure long labels don't overlap by adding a line break every 30 characters
            formatted_label = "<br>".join([clade.name[i:i+75] for i in range(0, len(clade.name), 75)])

            tip_markers.append(go.Scatter(
                x=[x], y=[y], mode='markers+text' if show_tip_labels else 'markers',
                marker=dict(size=14, color=color, line=dict(width=1.5, color='black')),
                name=location if show_legend else None,
                text=f"{formatted_label}" if show_tip_labels else "",
                textposition="middle right",  # Keep text aligned
                textfont=dict(size=10),  # Reduce font size slightly
                hoverinfo='text',
                showlegend=show_legend
            ))

        else:
            if clade.confidence and clade.confidence > 90:
                node_markers.append(go.Scatter(
                    x=[x], y=[y], mode='markers',
                    marker=dict(size=12, color='black', symbol='diamond'),
                    hoverinfo='skip', showlegend=False
                ))

    # Add a scale bar
    scale_bar = [
        dict(
            type='line', x0=0, y0=-1, x1=0.05, y1=-1,
            line=dict(color='black', width=2)
        )
    ]

    x_margin = max_x * 0.35  # Increase x-axis space for text
    x_range = [0, max_x + x_margin]

    layout = go.Layout(
        title='Phylogenetic Tree with Midpoint Rooting and Support Values',
        xaxis=dict(title='Evolutionary Distance', showgrid=False, zeroline=False, range=x_range),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False, range=[-1, max_y + 1]),
        shapes=line_shapes + scale_bar,
        height=height, width=width,
        plot_bgcolor="rgb(240, 240, 250)",
        legend=dict(title="Locations", orientation="h", y=-0.2)
    )


    return go.Figure(data=tip_markers + node_markers, layout=layout)
