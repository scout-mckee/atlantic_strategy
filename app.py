import dash
from dash import Dash, html, dcc, Input, Output, dash_table
import pandas as pd
import os

app = dash.Dash(__name__)
server = app.server

df = pd.read_excel("LocalWorkshopBarrierSummary.xlsx", sheet_name="Sheet1")

app.layout = html.Div([

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
        "background-color": "#f9f9f9",
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
                        "background-color": "#f9f9f9",
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
                    "backgroundColor": "#e0f7fa",
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
                            id='example-table',
                            columns=[
                                {"name": "Name", "id": "name"},
                                {"name": "Age", "id": "age"}
                            ],
                            data=[
                                {"name": "Alice", "age": 25},
                                {"name": "Bob", "age": 30},
                                {"name": "Charlie", "age": 22},
                                {"name": "Diana", "age": 28}
                            ],
                            style_table={"width": "50%", "margin-bottom": "20px"},
                            style_cell={"textAlign": "left", "padding": "10px", "border": "1px solid #ddd"},
                            style_header={"backgroundColor": "#f0f8ff", "fontWeight": "bold", "border": "1px solid #ddd"}
                        )
                    ], style={
                        "padding": "30px",
                        "margin": "20px",
                        "background-color": "#f0f8ff",
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
                    "backgroundColor": "#bbdefb",
                    "color": "#000",
                    "border-radius": "10px"
                }
            )
        ],
        style={
            "margin-bottom": "20px",
            "border-radius": "15px",
            "overflow": "hidden",
            "box-shadow": "0 2px 5px rgba(0,0,0,0.1)"
        }
    )
])


# ---------------- Callback to update subcategory options ----------------
@app.callback(
    Output("subcategory-filter", "options"),
    Input("category-filter", "value")
)
def update_subcategory_options(selected_categories):
    if selected_categories:
        filtered_df = df[df["Category"].isin(selected_categories)]
        subcategories = sorted(filtered_df["Sub-Category"].unique())
    else:
        subcategories = sorted(df["Sub-Category"].unique())
    return [{"label": sc, "value": sc} for sc in subcategories]

# ---------------- Callback to update displayed images ----------------
@app.callback(
    Output("image-container", "children"),
    Input("category-filter", "value"),
    Input("subcategory-filter", "value"),
    Input("location-filter", "value"),
    Input("stakeholder-filter", "value"),
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
        filtered = filtered[filtered["Stakeholder(s)"].isin(selected_stakeholders)]

    if filtered.empty:
        return html.P("No images match your filters.")

    images = []
    for img_id in filtered["ID"]:
        file_path = f"assets/{img_id}.png"
        if os.path.exists(file_path):
            images.append(html.Img(src=f"/assets/{img_id}.png", style={"width": "60%", "margin-bottom": "20px"}))
        else:
            images.append(html.P(f"Missing image: {img_id}.png"))

    return images

# ---------------- Run app ----------------
# if __name__ == "__main__":
#     app.run()

if __name__ == "__main__":
    app.run_server(host="0.0.0.0", port=8050)