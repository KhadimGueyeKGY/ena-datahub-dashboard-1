import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import plotly.express as px
from dash.dependencies import Input, Output

#### CONFIGURATION ####
counts = pd.read_csv('data/dcc_XXX_Cumulative_read_submissions_XXX.txt', sep="\t")
datahub_metadata = pd.read_csv('data/dcc_XXX_ENA_Search_read_run_XXX.txt', sep="\t")
datahub = 'dcc_XXX'
#######################

external_stylesheets = [
    {
        "href": "https://fonts.googleapis.com/css2?"
                "family=Lato:wght@400;700&display=swap",
        "rel": "stylesheet",
    },
]


app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
app.title = "Data Hubs Dashboard"

app.layout = html.Div(
    children=[
        html.Div(
            children=[
                html.H1(children="Data Hub Dashboard",
                        className="header-title"
                ),
                html.H3(children=datahub,
                        className="sub-header",
                ),
                html.P(
                    children="This dashboard presents information related to your data hub.",
                    className="header-description",
                ),
            ],
            className="header",
        ),
        html.Div(
            children=[
                html.Div(
                    children=[
                        html.Div(
                            children=[
                                html.H2(children=len(datahub_metadata),
                                ),
                                html.P(children="Total raw sequence datasets",
                                       className="banner-title"
                                ),
                            ],
                            className="tile",
                        ),
                        html.Div(
                            children=[
                                html.H2(children=datahub_metadata['instrument_platform'].nunique(),
                                ),
                                html.P(children="Total sequencing platforms",
                                       className="banner-title"
                                ),
                            ],
                            className="tile",
                        ),
                        html.Div(
                            children=[
                                html.H2(children=datahub_metadata['instrument_model'].nunique(),
                                ),
                                html.P(children="Total sequencing platform models",
                                       className="banner-title"
                                ),
                            ],
                            className="tile",
                        ),
                    ],
                    className="tiles",
                ),
            ],
            className="banner",
        ),
        html.Div(
            children=[
                html.Div(
                    children=dcc.Graph(
                        id="price-chart",
                        config={"displayModeBar": False},
                        figure={
                            "data": [
                                {
                                    "x": counts["month_year"],
                                    "y": counts["cumulative_submissions"],
                                    "type": "lines",
                                    "hovertemplate": "%{y:}"
                                                        "<extra></extra>",
                                },
                            ],
                            "layout": {
                                "title": {
                                    "text": "Dcc_grusin cumulative raw read data submissions count",
                                    "x": 0.05,
                                    "xanchor": "left",
                                },
                                "xaxis": {"fixedrange": True, "tickangle": 45},
                                "yaxis": {
                                    "fixedrange": True,
                                },
                                "colorway": ["#17B897"]
                            },
                        },
                    ),
                    className="card",
                ),
                html.Div(
                    children=[
                        dcc.Dropdown(
                            id="variable",
                            value="instrument_platform",
                            options=[{'value': x, 'label': x}
                                     for x in ['instrument_platform', 'library_selection', 'library_source', 'library_strategy']],
                            clearable=False
                        ),
                        dcc.Graph(id="pie-chart"),
                        ],
                    className="card",
                ),
            ],
            className="wrapper",
        ),
        html.Div(
            children=[
                html.P(
                    children="Powered by",
                    className="header-description",
                ),
            ],
            className="footer",
        ),
    ],
)


@app.callback(
    Output("pie-chart", "figure"),
    [Input("variable", "value")]
)

def generate_chart(variable):
    fig = px.pie(datahub_metadata, names=variable)
    return fig

if __name__ == "__main__":
    app.run_server(debug=True)