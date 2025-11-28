import dash
from dash import Dash, html, dcc, Input, Output, dash_table
import pandas as pd
import os


# ---------------- App Initialization ----------------
app = Dash(__name__)
server = app.server

# ---------------- Load Data ----------------
df = pd.read_excel("LocalWorkshopBarrierSummary.xlsx", sheet_name="Sheet1")

# ---------------- Layout ----------------
app.layout = html.Div([

    # ---------------- Title ----------------
    html.H1(
        "Local Workshop Dashboard",
        style={
            "textAlign": "left",
            "margin": "20px",
            "fontSize": "36px",
            "fontWeight": "bold"
        }
    ),

    # ---------------- Filters ----------------
    html.Div([
        html.H2("Filters", style={"margin-bottom": "20px"}),
        
        dcc.Dropdown(
            id="category-filter",
            options=[{"label": c, "value": c} for c in sorted(df["Category"].unique())],
            placeholder="Select Category",
            multi=True,
            style={"margin-bottom": "15px"}
        ),
        dcc.Dropdown(
            id="subcategory-filter",
            options=[{"label": sc, "value": sc} for sc in sorted(df["Sub-Category"].unique())],
            placeholder="Select Subcategory",
            multi=True,
            style={"margin-bottom": "15px"}
        ),
        dcc.Dropdown(
            id="location-filter",
            options=[{"label": loc, "value": loc} for loc in sorted(df["Location Identified"].unique())],
            placeholder="Select Location",
            multi=True,
            style={"margin-bottom": "15px"}
        ),
        dcc.Dropdown(
            id="stakeholder-filter",
            options=[{"label": s, "value": s} for s in sorted(df["Stakeholder(s)"].unique())],
            placeholder="Select Stakeholder/Owner Category",
            multi=True,
            style={"margin-bottom": "20px"}
        ),
    ], style={
        "padding": "30px",
        "margin": "20px",
        "border-radius": "15px",
        "box-shadow": "0 2px 5px rgba(0,0,0,0.1)"
    }),

    # ---------------- Tabs ----------------
    dcc.Tabs([
        # ---------------- Dashboard Tab ----------------
        dcc.Tab(
            label='Dashboard View',
            children=[
                html.Div([
                    html.H2("Dashboards", style={"margin-bottom": "20px"}),
                    html.Hr(),
                    html.Div(id="image-container")
                ], style={
                    "padding": "30px",
                    "margin": "20px",
                    "border-radius": "15px",
                    "box-shadow": "0 2px 5px rgba(0,0,0,0.1)"
                })
            ],
            style={
                "textAlign": "left",
                "padding-left": "20px",
                "font-weight": "bold",
                "border-radius": "10px"
            },
            selected_style={
                "textAlign": "left",
                "padding-left": "20px",
                "font-weight": "bold",
                "color": "#000",
                "border-radius": "10px"
            }
        ),

        # ---------------- Initiatives Tab ----------------
        dcc.Tab(
            label='Initiatives View',
            children=[
                html.Div([
                    html.H2(
                        "Initiatives Overview",
                        style={
                            "margin-bottom": "20px",
                            "textAlign": "left",
                            "fontSize": "28px",
                            "fontWeight": "bold"
                        }
                    ),
                    dash_table.DataTable(
                        id='initiatives-table',
                        columns=[
                            {"name": "Opportunities/ Initiative", "id": "Opportunities/ Initiative"},
                            {"name": "Category", "id": "Category"},
                            {"name": "Location Identified", "id": "Location Identified"},
                            {"name": "Stakeholder(s)", "id": "Stakeholder(s)"}
                        ],
                        data=[],
                        page_action="native",
                        page_size=10,
                        style_table={
                            "width": "100%",
                            "margin": "0 auto",
                            "overflowX": "hidden"
                        },
                        style_cell={
                            "textAlign": "left",
                            "padding": "10px",
                            "whiteSpace": "normal",
                            "height": "auto",
                            "wordBreak": "break-word"
                        },
                        style_cell_conditional=[
                            {"if": {"column_id": "Opportunities/ Initiative"}, "maxWidth": "250px"},
                            {"if": {"column_id": "Category"}, "maxWidth": "150px"},
                            {"if": {"column_id": "Location Identified"}, "maxWidth": "150px"},
                            {"if": {"column_id": "Stakeholder(s)"}, "maxWidth": "200px"},
                        ],
                        style_header={
                            "fontWeight": "bold",
                            "textAlign": "left"
                        }
                    )
                ], style={
                    "padding": "30px",
                    "margin": "20px",
                    "border-radius": "15px",
                    "box-shadow": "0 2px 5px rgba(0,0,0,0.1)"
                })
            ],
            style={
                "textAlign": "left",
                "padding-left": "20px",
                "font-weight": "bold",
                "border-radius": "10px",
            },
            selected_style={
                "textAlign": "left",
                "padding-left": "20px",
                "font-weight": "bold",
                "color": "#000",
                "border-radius": "10px"
            }
        )
    ],
    style={
        "margin-bottom": "20px",
        "border-radius": "15px",
        "overflow": "hidden",
        "box-shadow": "0 2px 5px rgba(0,0,0,0.1)",
        "margin": "20px"
    })
])

# ---------------- Callbacks ----------------

# Category ↔ Subcategory dependent dropdowns
@app.callback(
    Output("subcategory-filter", "options"),
    Output("category-filter", "options"),
    Input("category-filter", "value"),
    Input("subcategory-filter", "value")
)
def update_dropdowns(selected_categories, selected_subcategories):
    filtered = df.copy()

    # If subcategories are selected, restrict categories
    if selected_subcategories:
        filtered = filtered[filtered["Sub-Category"].isin(selected_subcategories)]
        categories = sorted(filtered["Category"].unique())
    else:
        categories = sorted(df["Category"].unique())

    # If categories are selected, restrict subcategories
    if selected_categories:
        filtered2 = df[df["Category"].isin(selected_categories)]
        subcategories = sorted(filtered2["Sub-Category"].unique())
    else:
        subcategories = sorted(df["Sub-Category"].unique())

    category_options = [{"label": c, "value": c} for c in categories]
    subcategory_options = [{"label": sc, "value": sc} for sc in subcategories]

    return subcategory_options, category_options

# Update images in Dashboard tab
@app.callback(
    Output("image-container", "children"),
    Input("category-filter", "value"),
    Input("subcategory-filter", "value"),
    Input("location-filter", "value"),
    Input("stakeholder-filter", "value")
)
def update_images(selected_categories, selected_subcategories, selected_locations, selected_stakeholders):
    filtered = df.copy()

    if selected_categories:
        filtered = filtered[filtered["Category"].isin(selected_categories)]
    if selected_subcategories:
        filtered = filtered[filtered["Sub-Category"].isin(selected_subcategories)]
    if selected_locations:
        filtered = filtered[filtered["Location Identified"].isin(selected_locations)]
    if selected_stakeholders:
        filtered = filtered[filtered["Stakeholder(s)"].apply(
            lambda cell: any(s in str(cell) for s in selected_stakeholders)
        )]

    if filtered.empty:
        return html.P("No images match your filters.")

    images = []
    for img_id in filtered["ID"]:
        file_path = f"assets/{img_id}.png"
        if os.path.exists(file_path):
            images.append(html.Img(
                src=f"/assets/{img_id}.png",
                style={
                        "width": "70%",       # bigger image
                        "margin-bottom": "20px",
                        "display": "block",
                        "margin-left": "auto",
                        "margin-right": "auto"
                    }
            ))
        else:
            images.append(html.P(f"Missing image: {img_id}.png"))

    return images

# Update initiatives table
@app.callback(
    Output("initiatives-table", "data"),
    Input("category-filter", "value"),
    Input("subcategory-filter", "value"),
    Input("location-filter", "value"),
    Input("stakeholder-filter", "value")
)
def update_table(selected_categories, selected_subcategories, selected_locations, selected_stakeholders):
    filtered = df.copy()

    if selected_categories:
        filtered = filtered[filtered["Category"].isin(selected_categories)]
    if selected_subcategories:
        filtered = filtered[filtered["Sub-Category"].isin(selected_subcategories)]
    if selected_locations:
        filtered = filtered[filtered["Location Identified"].isin(selected_locations)]
    if selected_stakeholders:
        filtered = filtered[filtered["Stakeholder(s)"].apply(
            lambda cell: any(s in str(cell) for s in selected_stakeholders)
        )]

    return filtered[
        ["Opportunities/ Initiative", "Category", "Location Identified", "Stakeholder(s)"]
    ].to_dict("records")




# ---------------- Run app ----------------
if __name__ == "__main__":
    app.run(debug=True)

# if __name__ == "__main__":
#     app.run_server(host="0.0.0.0", port=8050)