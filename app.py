import dash
from dash import Dash, html, dcc, Input, Output, dash_table
import pandas as pd
import os

app = dash.Dash(__name__)
server = app.server

df = pd.read_excel("LocalWorkshopBarrierSummary.xlsx", sheet_name="Sheet1")

app.layout = html.Div([

    html.Div([
        html.H1("Innovative Atlantic Housing Strategy", style={"textAlign": "left", "margin-left": "20px", "fontSize": "36px"})
    ], style={"padding-top": "20px"}),

    # ---------------- Filters (global) ----------------
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
            placeholder="Select Stakeholder(s)",
            multi=True,
            style={"margin-bottom": "20px"}
        )
    ], style={
        "padding": "30px",
        "margin": "20px",
        "border-radius": "15px",
        "box-shadow": "0 2px 5px rgba(0,0,0,0.1)"
    }),

    # ---------------- Tabs ----------------
    dcc.Tabs(
        [
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
            dcc.Tab(
                label='Initiatives View',
                children=[
                    html.Div([
                        html.H2("Example Table", style={"margin-bottom": "20px"}),
                        dash_table.DataTable(
                            id='initiatives-table',
                            columns=[
                                {"name": "Opportunities/ Initiative", "id": "Opportunities/ Initiative"},
                                {"name": "Category", "id": "Category"},
                                {"name": "Location Identified", "id": "Location Identified"},
                                {"name": "Stakeholder(s)", "id": "Stakeholder(s)"}
                            ],
                            data=[],
                            page_action="none",
                            page_size=10,
                            style_table={"width": "90%", "margin": "20px auto"},
                            style_cell={"textAlign": "left", "padding": "10px"},
                            style_header={"fontWeight": "bold"}
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
        }
    )
])

def filter_dataframe(selected_categories, selected_subcategories, selected_locations, selected_stakeholders):
    """
    Filters the main dataframe based on all the filter inputs.
    Supports substring matching for stakeholders.
    """
    filtered = df.copy()

    if selected_categories:
        filtered = filtered[filtered["Category"].isin(selected_categories)]
    if selected_subcategories:
        filtered = filtered[filtered["Sub-Category"].isin(selected_subcategories)]
    if selected_locations:
        filtered = filtered[filtered["Location Identified"].isin(selected_locations)]
    if selected_stakeholders:
        # Use regex to match any selected stakeholder
        pattern = "|".join(map(re.escape, selected_stakeholders))
        filtered = filtered[filtered["Stakeholder(s)"].str.contains(pattern, na=False)]

    return filtered

# ---------------- Callbacks ----------------

# 1️⃣ Bidirectional Category & Subcategory Dropdown
@app.callback(
    [Output("category-filter", "options"),
     Output("subcategory-filter", "options")],
    [Input("category-filter", "value"),
     Input("subcategory-filter", "value")]
)
def update_category_subcategory(selected_categories, selected_subcategories):
    """
    Updates both Category and Subcategory dropdown options.
    - If subcategories are selected, restrict categories to those that contain the selected subcategories.
    - If categories are selected, restrict subcategories to those belonging to the selected categories.
    """
    # Determine valid categories
    if selected_subcategories:
        valid_categories = df[df["Sub-Category"].isin(selected_subcategories)]["Category"].dropna().unique()
    else:
        valid_categories = df["Category"].dropna().unique()
    category_options = [{"label": c, "value": c} for c in sorted(valid_categories)]

    # Determine valid subcategories
    if selected_categories:
        valid_subcategories = df[df["Category"].isin(selected_categories)]["Sub-Category"].dropna().unique()
    elif selected_subcategories:
        valid_subcategories = df[df["Sub-Category"].isin(selected_subcategories)]["Sub-Category"].dropna().unique()
    else:
        valid_subcategories = df["Sub-Category"].dropna().unique()
    subcategory_options = [{"label": sc, "value": sc} for sc in sorted(valid_subcategories)]

    return category_options, subcategory_options

# 2️⃣ Update Dashboard Images
@app.callback(
    Output("image-container", "children"),
    [
        Input("category-filter", "value"),
        Input("subcategory-filter", "value"),
        Input("location-filter", "value"),
        Input("stakeholder-filter", "value")
    ]
)
def update_images(selected_categories, selected_subcategories, selected_locations, selected_stakeholders):
    filtered = filter_dataframe(selected_categories, selected_subcategories, selected_locations, selected_stakeholders)

    if filtered.empty:
        return html.P("No images match your filters.")

    images = []
    for img_id in filtered["ID"].dropna():
        file_path = os.path.join("assets", f"{img_id}.png")
        if os.path.exists(file_path):
            images.append(html.Img(src=f"/assets/{img_id}.png",
                                   style={"width": "60%", "margin-bottom": "20px"}))
        else:
            images.append(html.P(f"Missing image: {img_id}.png"))
    return images

# 3️⃣ Update Initiatives Table
@app.callback(
    Output("initiatives-table", "data"),
    [
        Input("category-filter", "value"),
        Input("subcategory-filter", "value"),
        Input("location-filter", "value"),
        Input("stakeholder-filter", "value")
    ]
)
def update_table(selected_categories, selected_subcategories, selected_locations, selected_stakeholders):
    filtered = filter_dataframe(selected_categories, selected_subcategories, selected_locations, selected_stakeholders)

    return filtered[
        [
            "Opportunities/ Initiative",
            "Category",
            "Location Identified",
            "Stakeholder(s)"
        ]
    ].to_dict("records")


# ---------------- Run app ----------------
if __name__ == "__main__":
    app.run(debug=True)

# if __name__ == "__main__":
#     app.run_server(host="0.0.0.0", port=8050)