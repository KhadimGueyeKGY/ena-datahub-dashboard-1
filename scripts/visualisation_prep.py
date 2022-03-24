#!/usr/bin/env/python3
# This script handles the creation of data frames for plots in the app

__author__ = 'Nadim Rahman'

import pandas as pd
import argparse, datetime, requests
from data_import import retrieve_data

months = {1: 'January', 2: 'February', 3: 'March', 4: 'April', 5: 'May', 6: 'June', 7: 'July', 8: 'August', 9: 'September', 10: 'October', 11: 'November', 12: 'December'}
ena_searches = {
    'read_run': {'search_fields': ['experiment_accession', 'study_accession', 'study_title', 'sample_accession', 'experiment_title', 'country', 'collection_date', 'center_name', 'broker_name', 'tax_id', 'scientific_name', 'instrument_platform', 'instrument_model', 'library_layout', 'library_name', 'library_selection', 'library_source', 'library_strategy', 'first_public', 'first_created'], 'result_type': 'read_run', 'data_portal': 'pathogen', 'authentication': 'True'},
    'analysis': {'search_fields': ['analysis_accession', 'analysis_title', 'analysis_type', 'study_accession', 'study_title', 'sample_accession', 'center_name', 'first_public', 'first_created', 'tax_id', 'scientific_name', 'pipeline_name', 'pipeline_version', 'country', 'collection_date'], 'result_type': 'analysis', 'data_portal': 'pathogen', 'authentication': 'True'}
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
        |  Python script to create custom dataframes                  |    
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

    def add_datahub_stats(self, stats, result_type):
        """
        Create a dataframe of data hub stats for the application
        :return:
        """
        if result_type == 'read_run':
            stats['Total raw sequence datasets'] = len(self.data)
            stats['Total sequencing platforms'] = self.data['instrument_platform'].nunique()
            stats['Total sequencing platform models'] = self.data['instrument_model'].nunique()
            stats['Data Providers (Collaborators)'] = self.data['center_name'].nunique()
        elif result_type == 'analysis':
            stats['Total analyses'] = len(self.data)
            stats['Analysis pipelines'] = self.data['pipeline_name'].nunique()
        return stats

    def create_earliest_row(self, df, cols, result_type):
        # Identify earliest date and set to 0
        earliest = df['first_created'].iloc[0] + '-01'
        earliest = datetime.datetime.strptime(earliest, '%Y-%m-%d')
        lastMonth = earliest - datetime.timedelta(days=1)
        lastMonth = str(lastMonth.date())[:-3]

        # Create a new row of data and add to the first row of the data frame
        row = pd.DataFrame([[lastMonth, 0, 0, result_type]], columns=cols)
        updated_df = pd.concat([row, df]).reset_index(drop=True)
        return updated_df

    def submission_count(self, result_types):
        """
        Create a cumulative submissions dataframe
        :return:
        """
        cols = ['first_created', 'submissions', 'cumulative_submissions', 'result_type']
        total_counts = pd.DataFrame(columns=cols)
        for result_type in result_types:
            df = pd.read_csv('data/{}_ENA_Search_{}_{}.txt'.format(self.args.username, result_type, self.date_today), sep="\t")
            first_created = df[['first_created']]           # Grab the first_created column
            first_created['first_created'] = first_created['first_created'].str[:-3]            # Remove the day from the first_created column values

            counts = first_created['first_created'].value_counts(sort=True).rename_axis('first_created').reset_index(name='submissions'.format(result_type))           # Create a count for each month's submissions
            counts = counts.sort_values(by='first_created')             # Sort by the first_created column to calculate cumulative sum appropriately
            counts['cumulative_submissions'.format(result_type)] = counts['submissions'.format(result_type)].cumsum()

            counts = self.create_earliest_row(counts, cols, result_type)            # Insert a row for the month of 0 submissions
            counts['result_type'] = result_type

            total_counts = pd.concat([total_counts, counts], ignore_index=True)
        total_counts.to_csv('data/{}_cumulative_submissions_{}.txt'.format(self.args.username, self.date_today), sep="\t", index=False)
        return total_counts

    def create_dfs(self):
        """
        Create all dataframes required for the application plots
        :return:
        """
        # Get ENA read data within the datahub
        datahub_statistics = {}
        for key, value in ena_searches.items():
            data_retrieval = retrieve_data(ena_searches[key], self.args.username,
                                       self.args.password)  # Instantiate class with information
            self.data = data_retrieval.coordinate_retrieval()

            # Obtain statistics for data hub
            datahub_statistics = prepDf.add_datahub_stats(self, datahub_statistics, key)

        # Convert the dictionary and save as a dataframe
        print('> Creating finalised data hub statistics data frame...')
        datahub_items = list(datahub_statistics.items())
        datahub_stats = pd.DataFrame(datahub_items, columns=['field', 'value'], index=[0, 1, 2, 3, 4, 5])
        datahub_stats.to_csv('data/{}_Datahub_stats_{}.txt'.format(self.args.username, self.date_today), sep="\t",
                             index=False)
        print('> Creating finalised data hub statistics data frame... [DONE]')

        # Create a cumulative submissions dataframe
        print('> Creating counts data frame...')
        counts = prepDf.submission_count(self, ena_searches.keys())
        print('> Creating counts data frame... [DONE]')



if __name__ == '__main__':
    print('---> Downloading data and creating dataframes...')
    today = datetime.datetime.now()
    date = today.strftime('%d%m%Y')

    args = get_args()       # Obtain script arguments
    prepare_dfs = prepDf(date, args)        # Instantiate preparation of dataframe
    prepare_dfs.create_dfs()
    print('---> Downloading data and creating dataframes... [COMPLETED]')
