from dash import dcc, html
import dash_bootstrap_components as dbc

# About Tab Content
about_content = dbc.Container([
    html.H2("About This App"),
    html.P(
        "This application is designed to help visualize multiple sequence alignments, phylogenetic trees, and SNP distances."
        "It allows users to upload tree structures, metadata, and geographic data to create interactive visualizations."
    ),
    html.P(
        "The MSA Visualization, Phylogenetic Tree Visualization, and SNP Distance Heatmap tabs provides a way to analyze and visualize evolutionary relationships."
    ),
    html.P([
        "This application was created and maintained by Taylor K. Paisie. Check out my ",
        html.A("website", href="https://taylorpaisie.github.io/", target="_blank", className="text-primary fw-bold"),
        " or my ",
        html.A("Github Repositories", href="https://github.com/taylorpaisie", target="_blank", className="text-primary fw-bold"),
        "."
    ]),
    html.P(["If you have any questions or issues about the SNP Workflow Dashboard, please submit an issue on the ",
        html.A("SNP Workflow Github Repository", href="https://github.com/taylorpaisie/snp_wf_dashboard/", target="_blank", className="text-primary fw-bold"),
        "."
    ])


], className="mt-4")

# How to Use Tab Content
how_to_use_content = dbc.Container([
    html.H2("How to Use This App"),
    html.P("Follow these steps to use the application effectively:"),
    html.Ol([
        html.Li("Upload a fasta file in the MSA Visualization tab."),
        html.Li("Upload a Newick tree file in the Phylogenetic Tree Visualization tab."),
        html.Li("Upload a corresponding metadata file for additional information."),
        html.Li("Toggle the tip labels to show or hide tree node names."),
        html.Li("Upload a SNP Distance Matrix TSV file for SNP distance heatmap.")
    ]),

    html.P("The metadata file for uploading in the Phylogenetic Tree Visualization tab must be a tab-delimited text file with the following columns:"),
    html.Ol([
        html.Li("taxa"),
        html.Li("date (optional)"),
        html.Li("location")
    ]),
    html.P(["For more details or if you are experiencing any problems with the dashboard, please submit an issue on the ",
        html.A("SNP Workflow Github Repository", href="https://github.com/taylorpaisie/snp_wf_dashboard/", target="_blank", className="text-primary fw-bold"),
        "."
    ]),
    html.Img(
        src='/assets/hiding_ham.jpg',  # Path to the image
        alt='Do not be like Hamilton and hide from your data!',
        style={'width': '25%', 'height': 'auto', 'marginTop': '20px'}
    )
], className="mt-4")


# Exporting the layouts
about_tab = dcc.Tab(label='About', children=[about_content])
how_to_use_tab = dcc.Tab(label='How to Use', children=[how_to_use_content])