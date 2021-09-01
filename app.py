import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
from scripts.plots import GeneratePlots


#### CONFIGURATION ####
date_of_data_import = 'XXXX'        # e.g. 03082021
datahub = 'dcc_XXXX'
#######################


external_stylesheets = [
    {
        "href": "https://fonts.googleapis.com/css2?"
                "family=Lato:wght@400;700&display=swap",
        "rel": "stylesheet",
    },
]


#----------[ Data Definition and Figure Generation ]----------#

plots = GeneratePlots(datahub, date_of_data_import)

datahub_stats = plots.return_stats()        # Data hub general statistics HTML object
cumulative_subs = plots.cumulative_line()       # Cumulative submissions line graph
sub_map = plots.submissions_map()       # Submissions map
# Pie chart is called on under 'Callbacks' as it is more interactive, with a drop-down


#----------[ App Information and Layout ]----------#

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
                    children=datahub_stats,
                    className="tiles",
                ),
            ],
            className="banner",
        ),
        html.Div(
            html.Div(
                children=dcc.Graph(
                    id="submissions_map",
                    figure=sub_map
                ),
                className="large-card",
            ),
            className='wide-wrapper'
        ),
        html.Div(
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
                                options=[{'value': x, 'label': x.replace("_", " ").capitalize()}
                                         for x in ['instrument_platform', 'library_selection', 'library_source', 'library_strategy']],
                                clearable=False
                                ),
                            dcc.Graph(id="pie-chart"),
                            ],
                        className="card",
                    ),
                ],
            ),
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