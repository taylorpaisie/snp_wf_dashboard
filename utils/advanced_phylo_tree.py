import numpy as np
import pandas as pd
import plotly.graph_objects as go
from Bio import Phylo

def plot_tree_circular(tree, metadata_dict):
    """
    Generates a circular phylogenetic tree with metadata-based color annotation.
    """

    x_coords = {}
    y_coords = {}
    lines = []
    leaf_nodes = tree.get_terminals()
    num_leaves = len(leaf_nodes)

    # Compute the max depth to normalize branch lengths
    branch_lengths = tree.depths()
    max_depth = max(branch_lengths.values())

    def assign_coordinates(clade, depth=0, angle_start=0, angle_end=360):
        """
        Recursively assigns radial coordinates to ensure proper layout.
        """
        branch_length = clade.branch_length if clade.branch_length else 0.01
        normalized_depth = np.log1p(depth + branch_length) / np.log1p(max_depth) * 15

        if clade.is_terminal():
            angle = np.linspace(angle_start, angle_end, num_leaves)[leaf_nodes.index(clade)]
            x_coords[clade] = np.radians(angle)
            y_coords[clade] = normalized_depth
            return angle
        else:
            angles = []
            num_children = len(clade.clades)
            step = (angle_end - angle_start) / max(num_children, 1)

            for i, child in enumerate(clade.clades):
                child_angle = assign_coordinates(
                    child,
                    depth + branch_length,
                    angle_start + i * step,
                    angle_start + (i + 1) * step
                )
                angles.append(child_angle)

            mean_angle = np.mean(angles)
            x_coords[clade] = np.radians(mean_angle)
            y_coords[clade] = normalized_depth

            for child in clade.clades:
                lines.append(((x_coords[clade], y_coords[clade]), (x_coords[child], y_coords[child])))
            
            return mean_angle

    assign_coordinates(tree.root)

    fig = go.Figure()

    # Draw Tree Branches with True Radial Scaling
    for (theta_start, r_start), (theta_end, r_end) in lines:
        fig.add_trace(go.Scatterpolar(
            r=[r_start, r_end],
            theta=[np.degrees(theta_start), np.degrees(theta_end)],
            mode='lines',
            line=dict(color='black', width=1),
            hoverinfo='none'
        ))
    
    # Heatmap Coloring Based on Metadata
    heatmap_r = max(y_coords.values()) + 1.2
    for clade in tree.get_terminals():
        theta = np.degrees(x_coords.get(clade, 0))
        color = metadata_dict.get(clade.name, "gray")

        fig.add_trace(go.Scatterpolar(
            r=[heatmap_r],
            theta=[theta],
            mode='markers',
            marker=dict(color=color, size=6, symbol="square"),
            hoverinfo='text',
            text=f"{clade.name} ({color})"
        ))
    
    fig.update_layout(
        title="Circular Phylogenetic Tree with Metadata Coloring",
        polar=dict(
            radialaxis=dict(visible=False),
            angularaxis=dict(showticklabels=False),
        ),
        showlegend=False,
        height=1000,
        width=1000,
        plot_bgcolor="white"
    )

    return fig

