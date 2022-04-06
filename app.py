import dash, yaml
import dash_core_components as dcc
import dash_bootstrap_components as dbc
import dash_html_components as html
from dash.dependencies import Input, Output
from scripts.plots import GeneratePlots


external_stylesheets = [
    {
        "href": "https://fonts.googleapis.com/css2?"
                "family=Lato:wght@400;700&display=swap",
        "rel": "stylesheet",
    },
    dbc.themes.BOOTSTRAP
]


#----------[ Configuration ]----------#
config_file = 'config.yaml'
with open(config_file) as f:
    configuration = yaml.safe_load(f)           # DATA_IMPORT must be in format 'DDMMYYYY'


#----------[ Data Definition and Figure Generation ]----------#

plots = GeneratePlots(configuration['DATAHUB'], configuration['DATA_IMPORT'])

datahub_stats = plots.return_stats()        # Data hub general statistics HTML object
stacked_raw_subs = plots.submissions()          # Stacked line graph for raw number of submissions
stacked_cum_subs = plots.cumulative_submissions()           # Stacked line graph for cumulative number of submissions
sub_map = plots.submissions_map()       # Submissions map

# Pie chart is called on under 'Callbacks' as it is more interactive, with a drop-down


#----------[ App Information and Layout ]----------#

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
app.title = "Data Hubs Dashboard"

app.layout = html.Div(
    [
        # Top Title Banner #
        dbc.Row(
            dbc.Col(
                html.Div(
                    children=[
                        html.H1(children="Data Hub Dashboard",
                                className="header-title"
                        ),
                        html.H3(children=configuration['DATAHUB'],
                                className="sub-header",
                        ),
                        html.P(
                            children="This dashboard presents information related to your data hub.",
                            className="header-description",
                        ),
                    ],
                    className="header"
                ),
                width=12
            )
        ),
        # Statistics Banner #
        dbc.Row(
            children=[
                html.Div(
                    children=datahub_stats,
                    className="tiles",
                ),
            ],
            className="banner",
        ),
        # Submissions Map #
        dbc.Row(
            dbc.Col(
                children=[
                    html.Div(
                        html.Div(
                            children=dcc.Graph(
                                id="submissions_map",
                                figure=sub_map
                            ),
                            className="large-card"
                        ),
                        className="wide-wrapper",
                    )
                ],
                width=12
            )
        ),
        # Cumulative Read Submissions Plot #
        dbc.Row(
            [
                dbc.Col(
                    html.Div(
                        children=[
                            dcc.Dropdown(
                                id="variable",
                                value="instrument_platform",
                                options=[{'value': x, 'label': x.replace("_", " ").capitalize()}
                                        for x in ['instrument_platform', 'library_selection', 'library_source', 'library_strategy']],
                                clearable=False
                            ),
                            dcc.Graph(id="pie-chart"),
                        ],
                    ),
                    className="card",
                    width=6,
                )
            ],
            className="row-two"
        ),
        dbc.Row(
            [
                dbc.Col(
                    html.Div(
                        children=dcc.Graph(
                            id="stacked_cumulative_submissions",
                            config={"displayModeBar": False},
                            figure=stacked_cum_subs
                        ),
                    ),
                    className="card",
                    width=6,
                ),
                dbc.Col(
                    html.Div(
                        children=dcc.Graph(
                            id="stacked_raw_submissions",
                            config={"displayModeBar": False},
                            figure=stacked_raw_subs
                        ),
                    ),
                    className="card",
                    width=6,
                )
            ],
            className="row-two"
        ),
        # Footer Banner #
        dbc.Row(
            dbc.Col(
                html.Div(
                    children=[
                        html.P(
                            children="Powered by",
                            className="header-description",
                        )
                    ],
                    className="footer"
                ),
                width=12
            )
        )
    ]
)


#----------[ Callbacks ]----------#

@app.callback(
    Output("pie-chart", "figure"),
    [Input("variable", "value")]
)
def generate_chart(variable):
    fig = plots.datahub_pie(variable)       # Create pie chart
    return fig


#----------[ Main ]----------#

if __name__ == "__main__":
    app.run_server(debug=True)