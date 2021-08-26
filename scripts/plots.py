#!/usr/bin/env/python3
# This script handles the creation of plots from the created data frame

__author__ = 'Nadim Rahman'

import pandas as pd
import plotly.graph_objects as go

class GeneratePlots:
    def __init__(self, datahub, date):
        self.datahub = datahub
        self.date_today = date

    def cumulative_line(self):
        counts = pd.read_csv('data/{}_Cumulative_read_submissions_{}.txt'.format(self.datahub, self.date_today), sep="\t")
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