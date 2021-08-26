import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import plotly.express as px
from dash.dependencies import Input, Output
from scripts.plots import GeneratePlots

#### CONFIGURATION ####
date_of_data_import = 'XXXX'        # e.g. 03082021
datahub = 'dcc_XXX'
#######################

datahub_metadata = pd.read_csv('data/{}_ENA_Search_read_run_{}.txt'.format(datahub, date_of_data_import), sep="\t")

external_stylesheets = [
    {
        "href": "https://fonts.googleapis.com/css2?"
                "family=Lato:wght@400;700&display=swap",
        "rel": "stylesheet",
    },
]

# Call Plots
cumulative_submissions = GeneratePlots(datahub, date_of_data_import)
cumulative_subs = cumulative_submissions.cumulative_line()


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
                        id="cumulative_read_submissions",
                        config={"displayModeBar": False},
                        figure=cumulative_subs
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