import requests
from bs4 import BeautifulSoup
import json
import sqlite3
from pprint import pprint

CACHE_FNAME = 'cache.json'
try:
    cache_file = open(CACHE_FNAME, 'r')
    cache_contents = cache_file.read()
    CACHE_DICTION = json.loads(cache_contents)
    cache_file.close()
except:
    CACHE_DICTION = {}

def params_unique_combination(baseurl, params):
    alphabetized_keys = sorted(params.keys())
    res = []
    for k in alphabetized_keys:
        res.append("{}-{}".format(k, params[k]))
    return baseurl + "_".join(res)

def make_request_using_cache(baseurl, params= {}, auth = None):
    unique_ident = params_unique_combination(baseurl,params)

    if unique_ident in CACHE_DICTION:
        cach_str='Getting data from cache.....'
        print(cach_str.upper())
        return CACHE_DICTION[unique_ident]
    else:
        request_str='Making new request.....'
        print(request_str.upper())
        resp = requests.get(baseurl, params, auth=auth)
        CACHE_DICTION[unique_ident] = resp.text
        dumped_json_cache = json.dumps(CACHE_DICTION)
        fw = open(CACHE_FNAME,"w")
        fw.write(dumped_json_cache)
        fw.close()
        return CACHE_DICTION[unique_ident]
#---------------------------------------------------------------------------------------------
#function will scrape the DVD home page and the top box office page
#return a list of all movies
def get_movie_list():
    movie_list=[]
    url1 = 'https://www.imdb.com/list/ls006625188/'
    request = make_request_using_cache(url1)
    soup = BeautifulSoup(request, "html.parser")
    content_div=soup.find('h3', class_="lister-item-header")
    # print(content_div)
    movie_titles=content_div.find_all('a')
    for x in movie_titles:
        movie_list.append(x.string)
    # print(movie_list)
    url2 = 'http://www.imdb.com/movies-in-theaters/?ref_=nv_mv_inth_1'
    request2 = make_request_using_cache(url2)
    soup2 = BeautifulSoup(request2, "html.parser")
    content_div2=soup2.find('div', class_='lister-item mode-grid')
    # print(soup2)
    movie_titles2=content_div2.find_all('a', class_='title')
    for x in movie_titles2:
        movie_list.append(x.string)
    # print(movie_list)
    # spaced_movie_list=[]
    # for movie in movie_list:
    #     if ' ' in movie:
    #         movie_replaced=movie.replace(' ', '_')
    #         spaced_movie_list.append(movie_replaced)
    #     else:
    #         spaced_movie_list.append(movie)
    # sorted_movie_list=sorted(spaced_movie_list)
    # return sorted_movie_list
get_movie_list()
#function will scrape each individual page
#will return nested dictionary with movie name as the key and dictionary of rewviews, movie rating,box office, genre, release date, plot and consensus review
def get_movie_info():
    movie_info_dict={}
    for movie in sorted_movie_list:
        url = 'http://www.rottentomatoes.com/m/{}'.format(movie)
        request = make_request_using_cache(url)
        soup = BeautifulSoup(request, "html.parser")
        content_div=soup.find('ul', class_='content-meta info')
        for x in content_div.find_all('li', class_='meta-row clearfix'):
            rating=x.find('div', class_='meta-value').text
            genre=x.find('a').text
            release_data=x.find('time', datetime='2017-12-07T16:00:00-08:00').text
            run_time=x.find('time', datetime_='P104M').text
            try:
                box_office=x.find('div', class_='meta-value').text
            except:
                box_office='NA'
        plot=soup.find('div', id='movieSynopsis')
        critic_rating=soup.find('span', {'class' : 'meter-value superPageFontColor'}).text
        audience_rating=soup.find('span', {'class' : 'meter popcorn numeric '}).text
        critic_consensus=soup.find('p',{'class' : 'meter-value superPageFontColor'}).text
        movie_info_dict[movie]['Genre']=genre
        movie_info_dict[movie]['Rating']=rating
        movie_info_dict[movie]['Release Data']=release_data[-1:4]
        movie_info_dict[movie]['Runtime']=run_time
        movie_info_dict[movie]['Box Office']=box_office
        movie_info_dict[movie]['Plot']=plot
        movie_info_dict[movie]['Reviews']['Critic Rating']=critic_rating+'%'
        movie_info_dict[movie]['Reviews']['Audience Rating']=audience_rating+'%'
        movie_info_dict[movie]['Reviews']['Critic Consensus']=critic_consensus
    return movie_info_dict
#will scrape wikipedia page about oscar winners
#returns a dictionary with movies as keys and the amount of oscars won as dictionaries
def scrape_wikipedia():
    for movie in sorted_movie_list:
        title_list=[]
        url = 'https://en.wikipedia.org/wiki/List_of_Academy_Award-winning_films'
        request = make_request_using_cache(url)
        soup = BeautifulSoup(request, "html.parser")
        content_div=soup.find('table', class_='wikitable sortable jquery-tablesorter')
        for row in content_div.find_all('tbody, ''tr'):
            title=row.find('a').text
            title_list.append(title)
            oscars_won=row.find('td')[1].text
            oscars_nominated=row.find('td')[2].text
            if movie in title_list:
                movie_info_dict[title]['Oscar Nominations']=oscars_nominated
                movie_info_dict[title]['Oscars Awarded']=oscars_won
            else:
                movie_info_dict[title]['Oscar Nominations']='None'
                movie_info_dict[title]['Oscars Awarded']='None'
    return movie_info_dict
#pprint(movie_info_dict)
# #------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
# #DATABASE-GOES-HERE
# DBNAME='movie_info.db'
# def init_db():
#     try:
#         conn=sqlite3.connect(DBNAME)
#         cur=conn.cursor()
#     except:
#         print('No connection!')
#
#     statement = '''
#         DROP TABLE IF EXISTS 'Reviews';
#     '''
#     cur.execute(statement)
#     statement = '''
#         DROP TABLE IF EXISTS 'Movie_Information';
#     '''
#     cur.execute(statement)
#     conn.commit()
#
#     statement = '''
#         CREATE TABLE 'Reviews' (
#             'Id' INTEGER PRIMARY KEY AUTOINCREMENT,
#             'CriticScore' REAL,
#             'AudienceScore' REAL,
#             'ConsensusReview' TEXT NOT NULL
#         );
#     '''
#     cur.execute(statement)
#     statement = '''
#         CREATE TABLE 'Movie_Information' (
#                 'Id' INTEGER PRIMARY KEY AUTOINCREMENT,
#                 'MovieName' TEXT NOT NULL,
#                 'Genre' TEXT NOT NULL,
#                 'Rating' TEXT NOT NULL,
#                 'BoxOfficeMoney' INTEGER,
#                 'ReleaseDate' TEXT NOT NULL,
#                 'Plot' TEXT NOT NULL
#         );
#     '''
#     cur.execute(statement)
#     conn.commit()
#     conn.close()
# def insert_data():
#     #------------------------------------------------------------------------------------------------------------------------------------------------------------------
#     #mapping dictionary
#     value_list=[]
#     for x in range(len(sorted_movie_list)):
#         value_list.append(x)
#     mapping_dict=dict(zip(sorted_movie_list, value_list))
#     # pprint(country_map)
#     #-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
#     conn = sqlite3.connect(DBNAME)
#     cur = conn.cursor()
#     for movie in sorted_movie_list:
#         CriticScore=movie_info_dict][movie]['Reviews']['Critic Rating']
#         AudienceScore=movie_info_dict[movie]['Reviews']['Audience Rating']
#         ConsensusReview=movie_info_dict[movie]['Reviews']['Critic Consensus']
#         insertion=(mapping_dict[movie], CriticScore, AudienceScore, ConsensusReview)
#         statement='''
#         INSERT INTO 'Reviews'
#         Values (?, ?, ?, ?)
#         '''
#         cur.execute(statement, insertion)
#         conn.commit()
#     conn = sqlite3.connect(DBNAME)
#     cur = conn.cursor()
#     for movie in sorted_movie_list:
#         MovieName=movie
#         Genre=movie_info_dict[movie]['Genre']
#         Rating=movie_info_dict[movie]['Rating']
#         BoxOfficeMoney=movie_info_dict[movie]['Box Office']
#         ReleaseDate=movie_info_dict[movie]['Release Data']
#         Plot=movie_info_dict[movie]['Plot']
#         insertion=(mapping_dict[movie], MovieName, Genre, Rating, BoxOfficeMoney, ReleaseDate, Plot)
#         statement='''
#         INSERT INTO 'Movie_Information'
#         Values (?, ?, ?, ?, ?, ?, ?)
#         '''
#         cur.execute(statement, insertion)
#         conn.commit()
# #---------------------------------------------------------------------------------------------
# __name__ == "__main__"
#     conn.close()
#     get_movie_list()
#     get_movie_info()
#     scrape_wikipedia()
#     init_db()
#     insert_data
# help_commands='''
# HELP COMMANDS START---------------5-COMMANDS-AVAILABLE------------------------------------
#          1. info <___>
#                  -
#          2. graph <___>
#                  -
#          3. exit
#                  -exits the program
#          4. help
#                  -lists available commands (these instructions)
# HELP COMMANDS END------------------------------------------------------------------------
# '''
# while True:
#     user_input = input("Enter command: ")
#     command = user_input.split()
#     if command[0]=='info':
#         pass
#     elif command[0]=='graph':
#         pass
#     elif command[0]=='exit':
#         print("GOODBYE! COME BACK FOR MORE MOVIES!")
#         break
#     elif command[0]=='help':
#         print(help_commands)
#         continue
#     else:
#         print("Please enter a valid command. Enter 'help' to see list of commands: ")
