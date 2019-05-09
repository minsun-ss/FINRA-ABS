# FINRA Agency Trading Visualization

## The Actual Visualization
Is here: http://minsun-agencytrading.herokuapp.com/
## About
A fully automated visualization that displays the last six months of agency trading 
volume data from FINRA's website in a Dash/plotly app running on Heroku. The data is 
extracted with some dataframe munging, stored and read from Amazon DynamoDB, and 
displayed with Dash. The repository contains:
<ol>
<li> The file to build the tables needed in Amazon DynamoDB (dynamodb_build_tables).
Feel free to edit the read and write capacity units, but I'm working from a free account 
here, so parsimony is the order of the day.</li>
<li> The files to download the data from FINRA, extract the data, and clean it 
(extractFINRAdata, extractMonthlyData)</li>
<li> The files to take the cleaned data and store it (extractMontlyData, 
dynamodb_write_tables)</li>
<li> The files to display the data through a Dash/plotly app (app.py, dataviz.py)</li>
<li> Automating the monthly cron job to Heroku (clock, worker).
</ol>

## Library
The visualization uses dash, boto3, BeautifulSoup4, urllib3, pandas, and numpy. 