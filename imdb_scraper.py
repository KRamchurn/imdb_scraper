#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Jun 13 12:54:35 2020

@author: kunalramchurn
"""

import requests
from requests import get
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np

from time import sleep
from random import randint

headers = {"Accept-Language": "en-US, en;q=0.5"}

titles = []
years = []
time = []
imdb_ratings = []
metascores = []
votes = []
us_gross = []

pages = np.arange(1,1001,50)

for page in pages:

    results = requests.get("https://www.imdb.com/search/title/?groups=top_1000&start=" + str(page) + "&ref_=adv_nxt", headers=headers)

    soup = BeautifulSoup(results.text, "html.parser")
    movie_div = soup.find_all('div', class_='lister-item mode-advanced')

    sleep(randint(2,10))

    for container in movie_div:

            #name
            name = container.h3.a.text
            titles.append(name)

            #year
            year = container.h3.find('span', class_='lister-item-year').text
            years.append(year)

            # runtime
            runtime = container.p.find('span', class_='runtime').text if container.p.find('span', class_='runtime').text else ''
            time.append(runtime)

            #IMDb rating
            imdb = float(container.strong.text)
            imdb_ratings.append(imdb)

            #metascore
            m_score = container.find('span', class_='metascore').text if container.find('span', class_='metascore') else ''
            metascores.append(m_score)

            #there are two NV containers, they hold both the votes and the grosses
            nv = container.find_all('span', attrs={'name': 'nv'})

            #filter nv for votes
            vote = nv[0].text
            votes.append(vote)

            #filter nv for gross earnings
            grosses = nv[1].text if len(nv) > 1 else '-'
            us_gross.append(grosses)

#create pandas dataframe
movies = pd.DataFrame({
'movie': titles,
'year': years,
'timeMin': time,
'imdb': imdb_ratings,
'metascore': metascores,
'votes': votes,
'us_grossMillions': us_gross,
})

movies['votes'] = movies['votes'].str.replace(',', '').astype(int)

movies.loc[:,'year'] = movies['year'].str[-5:-1].astype(int)

movies['timeMin'] = movies['timeMin'].astype(str)
movies['timeMin'] = movies['timeMin'].str.extract('(\d+)').astype(int)

movies['metascore'] = movies['metascore'].str.extract('(\d+)')
movies['metascore'] = pd.to_numeric(movies['metascore'], errors='coerce')

movies['us_grossMillions'] = movies['us_grossMillions'].map(lambda x: x.lstrip('$').rstrip('M'))
movies['us_grossMillions'] = pd.to_numeric(movies['us_grossMillions'], errors='coerce')

#export dataframe as csv file
movies.to_csv('movies.csv')
