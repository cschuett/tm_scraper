from selenium import webdriver
from numpy import random
import pandas as pd
import numpy as np
import re
import time
import html
import csv
from tabulate import tabulate
from bs4 import BeautifulSoup

## öffnet den Edge Browser sucht alle Ergebnisse von 2016 und gibt dieses als formatierte Tabelle aus.


url = "https://www.transfermarkt.de/"
url1 = "https://www.transfermarkt.de/1-bundesliga/gesamtspielplan/wettbewerb/L1/saison_id/2016"
browser = webdriver.Edge()
browser.get(url1)
page = BeautifulSoup(browser.page_source,"html5lib")
browser.close()
tables = page.find_all('div', attrs={"class" : "table-header"})
i = 0


for table in tables:
    
    sibling = table.find_next_sibling()
    if i == 0:
        df = pd.read_html(str(sibling))
        i =  i + 1
    df.append(pd.read_html(str(sibling)))
    print( tabulate(df[i-1], headers='keys', tablefmt='psql') )

