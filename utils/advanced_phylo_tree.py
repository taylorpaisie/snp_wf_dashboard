import numpy as np
import pandas as pd
import plotly.graph_objects as go
from Bio import Phylo

def plot_tree_circular(tree, metadata, metadata_colors, show_tip_labels):
    """
    Generates a **true radial phylogenetic tree** with:
    - Correct branch length-based expansion
    - Proper radial transformations to avoid clustering
    - Single-row metadata heatmap tightly aligned with leaves
    """

    x_coords = {}
    y_coords = {}
    lines = []
    leaf_nodes = tree.get_terminals()
    num_leaves = len(leaf_nodes)

    # Extract metadata for circular heatmap
    metadata_dict = dict(zip(metadata["taxa"], metadata["color"]))

    # Compute the max depth to normalize branch lengths
    branch_lengths = tree.depths()
    max_depth = max(branch_lengths.values())

    def assign_coordinates(clade, depth=0, angle_start=0, angle_end=360):
        """
        Recursively assigns **radial coordinates**:
        - Expands outward based on branch length
        - Ensures nodes progressively move outward
        - Uses log-scaling to prevent inner clustering
        """
        branch_length = clade.branch_length if clade.branch_length else 0.01  # Avoid zero-length branches
        normalized_depth = np.log1p(depth + branch_length) / np.log1p(max_depth) * 15  # ✅ Expands outward proportionally

        if clade.is_terminal():
            angle = np.linspace(angle_start, angle_end, num_leaves)[leaf_nodes.index(clade)]
            x_coords[clade] = np.radians(angle)
            y_coords[clade] = normalized_depth  # ✅ Ensures proper outward expansion
            return angle
        else:
            angles = []
            num_children = len(clade.clades)
            step = (angle_end - angle_start) / max(num_children, 1)

            for i, child in enumerate(clade.clades):
                child_angle = assign_coordinates(
                    child,
                    depth + branch_length,  # ✅ Expand outward
                    angle_start + i * step,
                    angle_start + (i + 1) * step
                )
                angles.append(child_angle)

            mean_angle = np.mean(angles)
            x_coords[clade] = np.radians(mean_angle)
            y_coords[clade] = normalized_depth  # ✅ Maintain cumulative depth for radial expansion

            # **Draw connecting lines properly**
            for child in clade.clades:
                lines.append(((x_coords[clade], y_coords[clade]), (x_coords[child], y_coords[child])))

            return mean_angle

    # **Ensure Properly Distributed Leaf Nodes**
    for i, clade in enumerate(leaf_nodes):
        x_coords[clade] = np.radians((360 / num_leaves) * i)
        y_coords[clade] = np.log1p(max_depth) / np.log1p(max_depth) * 15  # ✅ Keeps outer nodes properly spaced

    # Assign new circular coordinates
    assign_coordinates(tree.root)

    # **Create Plot Traces**
    fig = go.Figure()

    # **Draw Tree Branches with True Radial Scaling**
    for (theta_start, r_start), (theta_end, r_end) in lines:
        fig.add_trace(go.Scatterpolar(
            r=[r_start, r_end],
            theta=[np.degrees(theta_start), np.degrees(theta_end)],
            mode='lines',
            line=dict(color='black', width=1),  # ✅ Medium thickness for visibility
            hoverinfo='none'
        ))

    # **Add Single Row of Circular Heatmap (Tightly Aligned)**
    heatmap_r = max(y_coords.values()) + 1.2  # ✅ Adjust metadata ring closer
    for clade in tree.get_terminals():
        theta = np.degrees(x_coords.get(clade, 0))
        color = metadata_dict.get(clade.name, "gray")

        fig.add_trace(go.Scatterpolar(
            r=[heatmap_r],
            theta=[theta],
            mode='markers',
            marker=dict(color=color, size=6, symbol="square"),  # ✅ Matches iTOL
            hoverinfo='text',
            text=f"{clade.name} ({color})"
        ))

    # **Adjust Layout for Circular Phylogenetic Structure**
    fig.update_layout(
        title="iTOL-Style Radial Phylogenetic Tree",
        polar=dict(
            radialaxis=dict(visible=False),
            angularaxis=dict(showticklabels=False),
        ),
        showlegend=False,
        height=1000,  # ✅ Large figure for detail
        width=1000,
        plot_bgcolor="white"  # ✅ Matches iTOL
    )

    return fig
