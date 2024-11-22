#!/usr/bin/env python3

import dash
from dash import dcc, html
from dash import dash_table
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
import dash_bootstrap_components as dbc
import base64
import io
import os
import sys

import self
import sqlite3
import pandas as pd


# Define the directory and file path to save uploaded files
try:
    UPLOAD_DIRECTORY = sys.argv[1]
except:
    UPLOAD_DIRECTORY = "uploads"


# Variable to store the file handle
# VCF_fh = None

# Variable to store the Self object
self_dna = None


# Ensure the directory exists
if not os.path.exists(UPLOAD_DIRECTORY):
    os.makedirs(UPLOAD_DIRECTORY)

# Initialize the app with a dark theme
app = dash.Dash(
    __name__,
    title="Self",
    external_stylesheets=[dbc.themes.DARKLY],
    suppress_callback_exceptions=True,
)

# Define the layout with centered title and tabs
app.layout = dbc.Container(
    [
        # Title
        html.H1(
            "self.dna",
            style={
                "text-align": "center",
                "font-family": "sans-serif",
                "margin-top": "50px",
                "color": "#00FF7F",
            },
        ),
        # Tabs
        dcc.Tabs(
            id="tabs",
            value=None,
            children=[
                dcc.Tab(
                    label="Upload VCF",
                    value="upload-vcf",
                    style={
                        "font-family": "sans-serif",
                        "backgroundColor": "#222",
                        "color": "#ccc",
                    },
                    selected_style={
                        "borderBottom": "3px solid #00FF7F",
                        "font-family": "sans-serif",
                        "color": "#00FF7F",
                        "backgroundColor": "#222",
                    },
                ),
                dcc.Tab(
                    label="GWAS Catalog",
                    value="gwas-catalog",
                    style={
                        "font-family": "sans-serif",
                        "backgroundColor": "#222",
                        "color": "#ccc",
                    },
                    selected_style={
                        "borderBottom": "3px solid #00FF7F",
                        "font-family": "sans-serif",
                        "color": "#00FF7F",
                        "backgroundColor": "#222",
                    },
                ),
                dcc.Tab(
                    label="Variant Pathogenicity",
                    value="variant-pathogenicity",
                    style={
                        "font-family": "sans-serif",
                        "backgroundColor": "#222",
                        "color": "#ccc",
                    },
                    selected_style={
                        "borderBottom": "3px solid #00FF7F",
                        "font-family": "sans-serif",
                        "color": "#00FF7F",
                        "backgroundColor": "#222",
                    },
                ),
                dcc.Tab(
                    label="Genome Statistics",
                    value="genome-statistics",
                    style={
                        "font-family": "sans-serif",
                        "backgroundColor": "#222",
                        "color": "#ccc",
                    },
                    selected_style={
                        "borderBottom": "3px solid #00FF7F",
                        "font-family": "sans-serif",
                        "color": "#00FF7F",
                        "backgroundColor": "#222",
                    },
                ),
                dcc.Tab(
                    label="Polygenic Risk Scores",
                    value="polygenic-risk-scores",
                    style={
                        "font-family": "sans-serif",
                        "backgroundColor": "#222",
                        "color": "#ccc",
                    },
                    selected_style={
                        "borderBottom": "3px solid #00FF7F",
                        "font-family": "sans-serif",
                        "color": "#00FF7F",
                        "backgroundColor": "#222",
                    },
                ),
                dcc.Tab(
                    label="Curated Knowledgebase",
                    value="curated-kb",
                    style={
                        "font-family": "sans-serif",
                        "backgroundColor": "#222",
                        "color": "#ccc",
                    },
                    selected_style={
                        "borderBottom": "3px solid #00FF7F",
                        "font-family": "sans-serif",
                        "color": "#00FF7F",
                        "backgroundColor": "#222",
                    },
                ),
                dcc.Tab(
                    label="About",
                    value="about",
                    style={
                        "font-family": "sans-serif",
                        "backgroundColor": "#222",
                        "color": "#ccc",
                    },
                    selected_style={
                        "borderBottom": "3px solid #00FF7F",
                        "font-family": "sans-serif",
                        "color": "#00FF7F",
                        "backgroundColor": "#222",
                    },
                ),
            ],
            colors={
                "border": "#444",
                "primary": "#00FF7F",  # This is green to highlight selected tab
                "background": "#222",
            },
            style={"padding": "20px"},
        ),
        # Content for each tab
        html.Div(id="tabs-content", style={"margin-top": "20px", "color": "#ccc"}),
    ],
    fluid=True,
)


def render_upload_vcf_tab(
    content_style: dict = {
        "color": "#00FF7F",
        "font-size": "20px",
        "margin-bottom": "10px",
    }
):
    return html.Div(
        [
            html.H3("Upload VCF", style=content_style),
            dcc.Upload(
                id="upload-data",
                children=html.Div(
                    [
                        "Drag and Drop or ",
                        html.A("Browse", style={"color": "#00FF7F"}),
                    ]
                ),
                style={
                    "width": "50%",
                    "height": "200px",
                    "lineHeight": "200px",
                    "borderWidth": "2px",
                    "borderStyle": "dashed",
                    "borderRadius": "10px",
                    "textAlign": "center",
                    "margin": "auto",
                    "color": "#ccc",
                    "backgroundColor": "#333",
                    "font-family": "sans-serif",
                },
                multiple=False,  # Allow only single file upload
            ),
            dcc.Loading(
                id="loading-upload",
                type="circle",
                children=html.Div(
                    id="output-data-upload",
                    style={"margin-top": "50px", "color": "#ccc"},
                ),
            ),
            html.Div(id="progress-container"),
            dcc.Interval(id="progress-interval", interval=1000, n_intervals=0),
        ],
        style={"text-align": "center", "margin-top": "40px"},
    )


def render_about_tab(content_style):
    # Path to your Markdown file
    markdown_file_path = os.path.join(
        os.getcwd(), "assets/about.md"
    )  # Ensure the file is in the same directory as the app

    # Read the Markdown file
    try:
        with open(markdown_file_path, "r") as file:
            markdown_content = file.read()
    except FileNotFoundError:
        markdown_content = "The About content is currently unavailable. Please ensure the `about.md` file exists."

    style_dict = {
        "color": "#FFFFFF",  # White text for the body
        "backgroundColor": "#222222",  # Dark gray background
        "padding": "20px",  # Padding around the text for better spacing
        "borderRadius": "10px",  # Rounded corners for the container
        "font-family": "sans-serif",  # Consistent font with the rest of the app
        "lineHeight": "1.6",  # Improve readability with increased line spacing
    }

    # Return a container with the Markdown content
    return html.Div(
        [
            # html.H3("About", style=content_style),
            dcc.Markdown(
                markdown_content,
                # style=style_dict,
                className="markdown",
            )
        ],
        style={"text-align": "left", "margin": "40px auto", "width": "75%"},
    )


# Function to render GWAS Catalog tab content with row selection dropdown
def render_gwas_catalog_tab(content_style, db_path):
    # Connect to SQLite database
    conn = sqlite3.connect(db_path)
    query = "SELECT CHROM, POS, ID, REF, ALT, QUAL, FILTER, REGION, FUNCTION, MINPVALUE, ASSOCIATIONS FROM variants WHERE ASSOCIATIONS IS NOT NULL AND ASSOCIATIONS != '';"
    df = pd.read_sql(query, conn)
    conn.close()

    # Layout for GWAS Catalog tab with row selection
    return html.Div(
        [
            html.H3("GWAS Catalog", style=content_style),
            # Dropdown for selecting page size
            html.Label("Rows per page:", style={"color": "#ccc"}),
            dcc.Dropdown(
                id="gwas-catalog-size-dropdown",
                options=[
                    {"label": str(size), "value": size} for size in [8, 16, 32, 64]
                ],
                value=8,  # Default page size
                clearable=False,
                style={
                    "width": "200px",
                    "backgroundColor": "#222",  # Dark background
                    "color": "#00FF7F",  # Green text
                    "font-family": "sans-serif",  # Consistent font
                    "border": "1px solid #444",  # Border color to blend with dark theme
                    # "border-radius": "5px",
                },
                className="page-size-dropdown",
            ),
            # Interactive DataTable
            dash_table.DataTable(
                id="gwas-catalog-table",
                columns=[{"name": col, "id": col} for col in df.columns],
                data=df.to_dict("records"),
                filter_action="native",
                sort_action="native",
                page_action="native",
                page_size=8,  # Default page size, will be controlled by the dropdown
                style_table={"overflowX": "auto"},
                style_header={"backgroundColor": "#333", "color": "#00FF7F"},
                style_cell={"backgroundColor": "#222", "color": "#ccc"},
            ),
        ]
    )


def render_variant_pathogenicity_tab(content_style, db_path):
    # Connect to SQLite database
    conn = sqlite3.connect(db_path)
    query = "SELECT CHROM, POS, ID, REF, ALT, QUAL, FILTER, REGION, FUNCTION, PATHOGENICITY FROM variants WHERE PATHOGENICITY IS NOT NULL AND PATHOGENICITY != '';"
    df = pd.read_sql(query, conn)
    conn.close()

    # Layout for Variant Pathogenicity tab with row selection
    return html.Div(
        [
            html.H3("Variant Pathogenicity", style=content_style),
            # Dropdown for selecting page size
            html.Label("Rows per page:", style={"color": "#ccc"}),
            dcc.Dropdown(
                id="variant-pathogenicity-size-dropdown",
                options=[
                    {"label": str(size), "value": size} for size in [8, 16, 32, 64]
                ],
                value=8,  # Default page size
                clearable=False,
                style={
                    "width": "200px",
                    "backgroundColor": "#222",  # Dark background
                    "color": "#00FF7F",  # Green text
                    "font-family": "sans-serif",  # Consistent font
                    "border": "1px solid #444",  # Border color to blend with dark theme
                    # "border-radius": "5px",
                },
                className="page-size-dropdown",
            ),
            # Interactive DataTable
            dash_table.DataTable(
                id="variant-pathogenicity-table",
                columns=[{"name": col, "id": col} for col in df.columns],
                data=df.to_dict("records"),
                filter_action="native",
                sort_action="native",
                page_action="native",
                page_size=8,  # Default page size, will be controlled by the dropdown
                style_table={"overflowX": "auto"},
                style_header={"backgroundColor": "#333", "color": "#00FF7F"},
                style_cell={"backgroundColor": "#222", "color": "#ccc"},
            ),
        ]
    )


# Update the table page size based on the dropdown selection
@app.callback(
    Output("gwas-catalog-table", "page_size"),
    Input("gwas-catalog-size-dropdown", "value"),
)
def gwas_catalog_update_size(page_size):
    return page_size


# Update the table page size based on the dropdown selection
@app.callback(
    Output("variant-pathogenicity-table", "page_size"),
    Input("variant-pathogenicity-size-dropdown", "value"),
)
def variant_pathogenicity_update_size(page_size):
    return page_size


# Callback to update content based on selected tab
@app.callback(Output("tabs-content", "children"), [Input("tabs", "value")])
def render_tab_content(tab):
    content_style = {"color": "#00FF7F", "font-size": "20px", "margin-bottom": "10px"}

    if tab == "upload-vcf":
        return render_upload_vcf_tab(content_style)

    elif tab == "gwas-catalog":
        if self_dna == None:
            return html.Div(
                [
                    html.H3("GWAS Catalog", style=content_style),
                    html.P("GWAS Catalog content goes here."),
                ]
            )
        else:
            return render_gwas_catalog_tab(
                content_style, list(self_dna.db_file_dict.items())[0][1]
            )

    elif tab == "polygenic-risk-scores":
        return html.Div(
            [
                html.H3("Polygenic Risk Scores", style=content_style),
                html.P("Polygenic Risk Scores content goes here."),
            ]
        )

    elif tab == "variant-pathogenicity":
        if self_dna == None:
            return html.Div(
                [
                    html.H3("Variant Pathogenicity", style=content_style),
                    html.P("Variant Pathogenicity prediction content goes here."),
                ]
            )
        else:
            return render_variant_pathogenicity_tab(
                content_style, list(self_dna.db_file_dict.items())[0][1]
            )

    elif tab == "curated-kb":
        return html.Div(
            [
                html.H3("Curated KB", style=content_style),
                html.P("Curated KB content goes here."),
            ]
        )

    elif tab == "genome-statistics":
        return html.Div(
            [
                html.H3("Genome Statistics", style=content_style),
                html.P("Genome Statistics content goes here."),
            ]
        )

    elif tab == "about":
        return render_about_tab(content_style)

    else:
        # Default content for other tabs or when no tab is selected
        return html.Div([html.P("Select a tab to see content.")])


progress_state = {"processed": 0, "total": 1}


def update_progress(processed, total):
    global progress_state
    progress_state["processed"] = processed
    progress_state["total"] = total


# Callback to handle file upload
@app.callback(
    [Output("output-data-upload", "children"), Output("progress-interval", "disabled")],
    [Input("upload-data", "contents"), State("upload-data", "filename")],
)
def get_self_from_vcf_upload(contents, filename):
    # global VCF_fh
    # if contents is not None:
    #    # Decode the uploaded file
    #    content_type, content_string = contents.split(",")
    #    decoded = base64.b64decode(content_string)
    #
    #    # Save the file handle to the VCF_fh variable
    #    VCF_fh = io.BytesIO(decoded)
    #
    #    # Optional display message
    #    return html.Div([html.H5(f"File '{filename}' uploaded successfully!")])
    # TODO: if filename is not None, warn about overwriting data
    global self_dna

    if contents is not None:
        # Decode the uploaded file
        content_type, content_string = contents.split(",")
        decoded = base64.b64decode(content_string)

        # Save the file
        file_path = os.path.join(UPLOAD_DIRECTORY, filename)
        with open(file_path, "wb") as f:
            f.write(decoded)

        # build the self object
        global self_dna
        self_dna = self.Self(file_path)

        # process variants
        internal_id = list(self_dna.internal_id_dict.keys())[0]
        internal_db = self_dna.db_file_dict[internal_id]
        self_dna.vcf_to_sqlite(file_path, internal_db, update_progress)

        # Optional display message
        return html.Div(
            [html.H5(f"File '{filename}' uploaded and processed successfully!")]
        )

    else:
        raise PreventUpdate


@app.callback(
    Output("progress-container", "children"),
    [Input("progress-interval", "n_intervals")],
)
def update_progress_display(n_intervals):
    global progress_state
    processed, total = progress_state["processed"], progress_state["total"]
    if total == 1:
        return ""
    progress = (processed / total) * 100
    return f"Processing: {processed}/{total} variants ({progress:.2f}%)."


# Run the app
if __name__ == "__main__":
    app.run_server(host="0.0.0.0", debug=False)
