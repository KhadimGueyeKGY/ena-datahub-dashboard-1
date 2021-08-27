#!/usr/bin/env/python3
# This script handles the creation of data frames for plots in the app

__author__ = 'Nadim Rahman'

import pandas as pd
import argparse, requests
from datetime import datetime
from data_import import retrieve_data

months = {1: 'January', 2: 'February', 3: 'March', 4: 'April', 5: 'May', 6: 'June', 7: 'July', 8: 'August', 9: 'September', 10: 'October', 11: 'November', 12: 'December'}
ena_searches = {
    'datahub': {'search_fields': ['experiment_accession', 'study_accession', 'study_title', 'sample_accession', 'experiment_title', 'country', 'collection_date', 'center_name', 'tax_id', 'scientific_name', 'instrument_platform', 'instrument_model', 'library_layout', 'library_name', 'library_selection', 'library_source', 'library_strategy', 'first_public', 'first_created'], 'result_type': 'read_run', 'data_portal': 'pathogen', 'authentication': 'True'}
}

def get_args():
    """
    Handle script arguments
    :return: Script arguments
    """
    parser = argparse.ArgumentParser(prog='bulk_webincli.py', formatter_class=argparse.RawDescriptionHelpFormatter,
                                     epilog="""
        + =========================================================== +
        |  ENA Data Hubs Dashboard: visualisation_prep.py             |
        |  Python script to create custom dataframes                                            |    
        + =========================================================== +
        """)
    parser.add_argument('-u', '--username', help='Data Hub username (e.g. dcc_XXXXX)', type=str, required=True)
    parser.add_argument('-p', '--password', help='Password for the data hub', type=str, required=True)
    args = parser.parse_args()
    return args

class prepDf:
    """
    Prepare dataframes to form basis of plots
    """
    def __init__(self, date_today, args):
        self.date_today = date_today
        self.args = args
        self.read_data = pd.read_csv('data/{}_ENA_Search_read_run_{}.txt'.format(self.args.username, self.date_today), sep="\t")

    def datahub_stats(self):
        """
        Create a dataframe of data hub stats for the application
        :return:
        """
        datahub_stats = pd.DataFrame()
        stats = pd.DataFrame([['Total raw sequence datasets', len(self.read_data)],
                              ['Total sequencing platforms', self.read_data['instrument_platform'].nunique()],
                              ['Total sequencing platform models', self.read_data['instrument_model'].nunique()]],
                              columns=['field', 'value'], index=[0, 1, 2])
        datahub_stats = datahub_stats.append(stats, ignore_index=True)
        datahub_stats.to_csv('data/{}_Datahub_stats_{}.txt'.format(self.args.username, self.date_today), sep="\t", index=False)

    def submission_count(self):
        """
        Create a cumulative submissions dataframe
        :return:
        """
        # Remove the day from the column values
        first_created = self.read_data[['first_created']]        # Grab the first_created column
        first_created['first_created'] = first_created['first_created'].str[:-3]        # Remove the day from the first_created column values

        counts = first_created['first_created'].value_counts(sort=False).rename_axis('first_created').reset_index(name='submissions')       # Create a count for each month's submissions
        counts['first_created'] = pd.to_datetime(counts["first_created"])       # Configure the column as a datetime
        counts = counts.sort_values(by='first_created')     # Sort by the date records were first created/submitted
        counts['cumulative_submissions'] = counts['submissions'].cumsum()       # Add a cumulative submission count column

        # Do some tidying up - adding name of months and changing column headers slightly
        final_counts = {}
        for index, row in counts.iterrows():
            month_year = months.get(row[0].month) + " " + str(row[0].year)
            final_counts[index] = [month_year, row[1], row[2]]
        final_counts = pd.DataFrame.from_dict(final_counts, orient='index', columns=['month_year', 'submissions', 'cumulative_submissions'])
        final_counts.to_csv('data/{}_Cumulative_read_submissions_{}.txt'.format(self.args.username, self.date_today), sep="\t", index=False)

    def create_dfs(self):
        """
        Create all dataframes required for the application plots
        :return:
        """
        # Get ENA read data within the datahub
        data_retrieval = retrieve_data(ena_searches['datahub'], self.args.username,
                                       self.args.password)  # Instantiate class with information
        ena_results = data_retrieval.coordinate_retrieval()

        # Create a cumulative submissions dataframe
        prepDf.submission_count(self)

        # Obtain statistics for data hub
        prepDf.datahub_stats(self)


if __name__ == '__main__':
    today = datetime.now()
    date = today.strftime('%d%m%Y')

    args = get_args()       # Obtain script arguments
    prepare_dfs = prepDf(date, args)        # Instantiate preparation of dataframe
    prepare_dfs.create_dfs()