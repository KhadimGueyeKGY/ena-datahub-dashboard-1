# ena-datahub-dashboard

This is a dashboard for Data Hub users, with information and graphs on their data hub.
The dashboard has been created in [Python Dash](https://dash.plotly.com/introduction#:~:text=Dash%20is%20a%20productive%20Python,works%20with%20data%20in%20Python.), which embeds interactive Plotly graphs.

### Usage
1. Clone this repository:

`git clone https://github.com/nadimm-rahman/ena-datahub-dashboard.git`
   
2. Check the requirements and ensure that you have them installed.
   
3. Download the data by specifying the data hub you're interested in. Dcc_grusin (a public SARS-CoV-2 data hub) has been used in the following example:

`python scripts/visualisation_prep.py -u dcc_grusin -p <PASSWORD>`

4. Configure the application script, but completing the 'CONFIGURATION' section at the top of `app.py`.

5. Good to go! Run the application:

`python app.py` and head to http://127.0.0.1:8050/
 on your browser.

### Requirements

