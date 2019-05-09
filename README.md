# FINRA Agency Trading Visualization

## About
Fully automated visualization that displays last six months of agency trading volume data
from FINRA's website in a Dash/plotly app running on Heroku. The data is extracted, stored,
and read from Amazon DynamoDB. The repository contains:
<ol>
<li> The file to build the tables needed in Amazon DynamoDB (dynamodb_build_tables)</li>
<li> The files to download the data from FINRA, extract the data, and clean it 
(extractFINRAdata, extractMonthlyData)</li>
<li> The files to take the cleaned data and store it (extractMontlyData, 
dynamodb_write_tables)</li>
<li> The files to display the data through a Dash/plotly app (app.py, dataviz.py)</li>
</ol>

## Library
The visualization uses dash, boto3, BeautifulSoup4, urllib3, pandas, and numpy. 