from dash import dcc, html
import dash_bootstrap_components as dbc
from .msa_layout import msa_layout
from .phylo_tree_layout import phylo_tree_layout
from .snp_heatmap_layout import snp_heatmap_layout
from .advanced_phylo_tree_layout import advanced_phylo_tree_layout  # ✅ Import the tab
from .info_layout import about_tab, how_to_use_tab

app_layout = dbc.Container([
    dbc.NavbarSimple(
        brand="SNP Workflow Dashboard",
        brand_href="#",
        color="primary",
        dark=True,
    ),
    dcc.Tabs([
        msa_layout,
        phylo_tree_layout,
        advanced_phylo_tree_layout,  # ✅ Add the "Advanced Phylogenetic Tree" tab
        snp_heatmap_layout,
        about_tab,
        how_to_use_tab
    ],
    colors={
        "border": "black",
        "primary": "black",
        "background": "grey"
    })
], fluid=True)
