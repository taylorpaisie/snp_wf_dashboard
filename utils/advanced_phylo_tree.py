import numpy as np
import pandas as pd
import plotly.graph_objects as go
from Bio import Phylo

def plot_tree_circular(tree, metadata_dict):
    """
    Radial tree layout with real branch length for internal branches,
    and a uniform outer ring with colored arcs like iTOL.
    """
    raw_depths = tree.depths()
    max_depth = max(raw_depths.values())
    scaling_factor = 13 / max_depth  # shrink slightly to make room for outer ring
    depths = {clade: d * scaling_factor for clade, d in raw_depths.items()}

    leaf_nodes = tree.get_terminals()
    num_leaves = len(leaf_nodes)
    leaf_angles = np.linspace(0, 2 * np.pi, num_leaves, endpoint=False)
    clade_angles = {clade: angle for clade, angle in zip(leaf_nodes, leaf_angles)}

    x_coords = {}
    y_coords = {}

    def assign_coords(clade):
        r = depths.get(clade, 0)
        if clade in clade_angles:
            theta = clade_angles[clade]
        else:
            child_thetas = []
            for child in clade.clades:
                assign_coords(child)
                child_thetas.append(x_coords[child])
            theta = np.mean(child_thetas)
        x_coords[clade] = theta
        y_coords[clade] = r

    assign_coords(tree.root)

    fig = go.Figure()

    for clade in x_coords:
        for child in clade.clades:
            r_vals = [y_coords[clade], y_coords[child]]
            theta_vals = [np.degrees(x_coords[clade]), np.degrees(x_coords[child])]
            fig.add_trace(go.Scatterpolar(
                r=r_vals,
                theta=theta_vals,
                mode='lines',
                line=dict(color='black', width=1.5),
                hoverinfo='none'
            ))

    # Outer metadata arcs at fixed radius
    outer_r = 15
    arc_width = 0.8
    arc_r_start = outer_r
    arc_r_end = outer_r + arc_width

    for i, clade in enumerate(leaf_nodes):
        theta_deg = np.degrees(clade_angles[clade])
        color = metadata_dict.get(clade.name, "gray")

        fig.add_trace(go.Scatterpolar(
            r=[arc_r_start, arc_r_end],
            theta=[theta_deg, theta_deg],
            mode='lines',
            line=dict(color=color, width=8),
            hoverinfo='text',
            text=f"{clade.name} ({color})"
        ))

    fig.update_layout(
        title="Radial Phylogenetic Tree with iTOL-style Metadata Ring",
        polar=dict(
            radialaxis=dict(visible=False),
            angularaxis=dict(showticklabels=False),
            bgcolor="white"
        ),
        showlegend=False,
        height=1000,
        width=1000,
        paper_bgcolor="white",
        plot_bgcolor="white",
        font_color="black"
    )

    return fig
