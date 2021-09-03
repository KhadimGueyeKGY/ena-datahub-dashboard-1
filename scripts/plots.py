#!/usr/bin/env/python3
# This script handles the creation of plots from the created data frame

__author__ = 'Nadim Rahman, Carla Cummins'

import json, math, os, sys
import pandas as pd
import plotly.graph_objects as go
import pycountry as pc
import dash_html_components as html
import pycountry_convert as pcc
import plotly.express as px

continent_codes = {'EU': 'europe', 'AS': 'asia', 'AF': 'africa', 'NA': 'north america', 'SA': 'south america'}      # Note this is not a full list, these are continents that are within the scope of the Cholorpleth maps

class GeneratePlots:
    """
    Generate all plots and data to be presented in the application.
    """
    def __init__(self, datahub, date):
        self.datahub = datahub      # Name of data hub
        self.date_today = date      # Date (e.g. 03082021)
        self.read_run = pd.read_csv('data/{}_ENA_Search_read_run_{}.txt'.format(self.datahub, self.date_today), sep="\t")

    def return_stats(self):
        """
        Obtain general data hubs statistics and create HTML for the application
        :return: HTML object housing data hub statistics
        """
        datahub_stats = pd.read_csv('data/{}_Datahub_stats_{}.txt'.format(self.datahub, self.date_today), sep="\t")     # Read in data hub stats data
        children = []       # Create empty children HTML list object
        for index, row in datahub_stats.iterrows():
            children.append(
                html.Div(
                    children=[
                        html.H2(children=row[1]),       # Value
                        html.P(children=row[0],         # Field
                               className="banner-title"
                            ),
                    ],
                    className="tile",
                ),
            )
        return children

    def cumulative_line(self):
        """
        Create a line graph of cumulative read submissions
        :return: Line graph figure object
        """
        counts = pd.read_csv('data/{}_Cumulative_read_submissions_{}.txt'.format(self.datahub, self.date_today), sep="\t")      # Read in cumulative read submissions data

        # Edit the data hub name to ensure it is in the format 'DCC_[A-Z][a-z]+'
        datahub_edited = self.datahub.split("_")
        datahub_edited = datahub_edited[0].replace('dcc', 'DCC') + "_" + datahub_edited[1][0].upper() + datahub_edited[1][1:]       # Convert lowercase to uppercase for 'dcc' and first letter of datahub name

        cumulative_subs = go.Figure(data=go.Scatter(
            x=counts.month_year, y=counts.cumulative_submissions, line=dict(color='firebrick', width=4)
        ))
        cumulative_subs.update_layout(
            title='<b>{} Cumulative Raw Read Sequence Submissions</b>'.format(datahub_edited),
            height=600
        )
        cumulative_subs.update_xaxes(
            tickangle=45,
            title_text='Month and Year',
            title_font={"size": 15}
        )
        cumulative_subs.update_yaxes(
            title_text='Total Submissions',
            title_font={"size": 15}
        )
        return cumulative_subs

    def get_continents(self, country_info):
        """
        Get the continent data to see if the map plot needs to focus to a region
        :param country_info: The country information dictionary to be used for the plot
        :return: Whether a focused plot needs to be produced
        """
        # Get a dictionary of alpha 2 codes in order to convert to continents
        countries = {}
        for country in pc.countries:
            countries[country.name] = country.alpha_2
        codes = [countries.get(country, 'Unknown code') for country in country_info.keys()]     # Assign alpha 2 codes for the data to be plotted

        continents = []
        for code in codes:
            if code != "Unknown code":
                try:
                    continent = pcc.country_alpha2_to_continent_code(code)
                except:
                    continue
                continents.append(continent)
        continents = list(set(continents))      # Remove duplicates
        if len(continents) > 1:
            return True     # There is data from multiple continents in the dataset
        elif len(continents) == 1:
            return continents[0]        # There is data from one continent in the dataset
        elif len(continents) == 0:
            return True     # We don't necessarily know what is in the data, default to the large map

    def submissions_map(self):
        """
        Create a map of submissions
        ADAPTED FROM: https://github.com/enasequence/ena-content-dataflow/blob/master/scripts/plotly_map_advanced_search.py
        :return: Map figure object
        """
        # load set of polygons for each country
        geojson_path = "{0}/{1}".format("/".join(os.path.realpath(__file__).split('/')[:-1]),
                                        '../assets/custom_with_ids.geo.json')
        with open(geojson_path) as json_file:
            countries = json.load(json_file)

        # these countries are not named according to their official pycountry names
        # we need to include custom mapping
        custom_codes = {
            'Russia': 'RUS', 'USA': 'USA', 'Czech Republic': 'CZE', 'South Korea': 'KOR',
            'State of Palestine': 'PSE', 'Iran': 'IRN', 'West Bank': 'PSE'
        }

        ena_df = self.read_run[['run_accession', 'country', 'first_public']]

        # fetch ISO3 codes and counts for each country
        # and apply relevant filters
        map_data = {}
        for country in ena_df.country:
            try:
                country = country.split(':')[0]
            except AttributeError:
                continue

            this_country_code = ''
            try:
                this_country_code = custom_codes[country]
            except KeyError:
                try:
                    country_obj = pc.countries.get(name=country)
                    if country_obj == None:
                        country_obj = pc.countries.get(common_name=country)
                    this_country_code = country_obj.alpha_3
                except AttributeError:
                    print("Cannot find ISO3 code for '{0}'".format(country))
                    sys.exit()

            try:
                map_data[country] = [this_country_code, map_data[country][1]+1]
            except KeyError:
                map_data[country] = [this_country_code, 1]

        # get continents in data to identify whether a continent-zoomed in map is sufficient
        continents = self.get_continents(map_data)     # True (for when there are multiple or no known continents) OR continent name (for when only one continent)

        # format the data  specifically for map display
        for country in map_data:
            country_code, country_count = map_data[country]
            hover_text = 'Country : {0}<br>Count: {1}'.format(pc.countries.get(alpha_3=country_code).name, f"{country_count:,}")
            map_data[country] = [country, country_code, country_count, math.log(country_count), hover_text]

        df = pd.DataFrame.from_dict(map_data, orient='index', columns=['country', 'country_code', 'count', 'log_count', 'text'])

        # set up colorbar with raw counts in place of log values
        min_max_count = [f"{x:,}" for x in (df['count'].min(), int(df['count'].mean()), df['count'].max())]
        min_max_log = [0, 6, 12] # is 12 always the max or just this time - and why?
        count_colorbar = go.choroplethmapbox.ColorBar(
            tickmode='array', tickvals=min_max_log, ticktext=min_max_count, tickfont={"size":20}
        )

        # create the map and display
        map = go.Figure(go.Choroplethmapbox(
            geojson=countries, locations=df.country_code, z=df.log_count, colorscale='Blues', # colorscale="Viridis",
            zmin=0, zmax=12, marker_opacity=0.5, marker_line_width=0, colorbar=count_colorbar,
            text=df.text, hoverinfo='text'
        ))
        map.update_layout(mapbox_style="carto-positron",  mapbox_zoom=3, mapbox_center = {"lat": 50, "lon": 4})
        map.update_layout(margin={"r":10,"t":10,"l":10,"b":10}, coloraxis_colorbar_x=-0.15, height=650)

        if continents is not True and continents in continent_codes:
            scope = continent_codes.get(continents)
            map.update_geos(scope=scope)
        return map

    def datahub_pie(self, variable):
        """
        Creates pie chart describing data hub holdings [INTERACTIVE]
        :param variable: The variable to create a pie chart on
        :return: Pie chart object
        """
        fig = px.pie(self.read_run, names=variable, title="<b>Data hub holdings composition: {}</b>".format(variable.replace("_", " ").capitalize()))
        return fig