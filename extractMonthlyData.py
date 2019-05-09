import os
import urllib3
from bs4 import BeautifulSoup
import extractFINRAdata
import dynamodb_write_tables

# Monthly run to collect data
def prepare_csv_directory():
    # removes all existing files in the csv directory to allow new ones to be added
    print('Eliminating files in csv directory...')
    directory = os.fsencode('csv')

    for file in os.listdir(directory):
        file = os.fsdecode(file)
        print('csv/{}'.format(file))
        os.remove('csv/{}'.format(file))
        print('Removed {}'.format(file))
    return True

def get_FINRA_files():
    # get the last two months of files
    print('Acquiring FINRA files from website...')
    url = 'http://tps.finra.org/idc-index.html'
    http = urllib3.PoolManager()

    response = http.request('GET', url)
    soup = BeautifulSoup(response.data, 'html.parser')

    finra_reports = [link.get('href') for link in soup.find_all('a') if 'HISTORIC' in str(link)]

    # get last two reports
    for i in range(2):
        filename = str(finra_reports[i]).split('/')[-1]
        r = http.request('GET', finra_reports[i], preload_content=False)
        with open('csv/{}'.format(filename), 'wb') as out:
            while True:
                data = r.read(1024)
                if not data:
                    break
                out.write(data)
        r.release_conn()
    return True

# run the monthly data all together now!
prepare_csv_directory()
get_FINRA_files()
extractFINRAdata.get_prices_and_volumes('csv')
dynamodb_write_tables.writeAllTrades()
dynamodb_write_tables.writeAllPrices()
print('Done!')