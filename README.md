# ena-datahub-dashboard

This is a dashboard for Data Hub users, with information and graphs on their data hub.
The dashboard has been created in [Python Dash](https://dash.plotly.com/introduction#:~:text=Dash%20is%20a%20productive%20Python,works%20with%20data%20in%20Python.), which embeds interactive Plotly graphs.

### Usage
1. Clone this repository:

`git clone https://github.com/nadimm-rahman/ena-datahub-dashboard.git`
   
2. Check the requirements and ensure that you have them installed.
   
3. Download the data by specifying the data hub you're interested in. Dcc_grusin (a public SARS-CoV-2 data hub) has been used in the following example:

`python scripts/visualisation_prep.py -u dcc_grusin -p <PASSWORD>`

4. Include configuration fields within `config.yaml`. An example has been included within the file.

5. Good to go! Run the application:

`python app.py` and head to http://127.0.0.1:8050/
 on your browser.

### Requirements

- [Python 3.6+](https://www.python.org/downloads/)
- [Python Dash](https://dash.plotly.com/installation)
- [Python Pandas](https://pandas.pydata.org/docs/getting_started/install.html)
- [Python Plotly](https://plotly.com/python/getting-started/#installation)
- [pycountry](https://pypi.org/project/pycountry/)
- [pycountry-convert](https://pypi.org/project/pycountry-convert/)
- [requests](https://docs.python-requests.org/en/master/user/install/)

### Files
- <b>scripts/data_import.py</b> - Includes a class object which handles all data downloaded and required to create plots off of. The output is stored in the `data` directory.
- <b>scripts/visualisation_prep.py</b> - Run this script to coordinate the data download and generation of customised dataframe(s) for plots in the application.
- <b>scripts/plots.py</b> - Includes a class object which handles creation of certain plot(s), that is called when `python app.py` is run.
- <b>assets</b> - Contains all styling-related files.

![alt text](https://github.com/nadimm-rahman/ena-datahub-dashboard/blob/main/assets/example.png?raw=true)