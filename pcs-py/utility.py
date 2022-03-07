import requests as req
import datetime
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np

### String conversion functions 

def get_rider_url(name:str):
    """
    Retrieves the url associated with the requested rider

    Args:
        name (str): The name of the rider as it appears on their PCS page
                    - this can be either in format: 
                        1) "FirstName MiddleName LastName" (actual name)
                        2) "firstname-middlename-lastname" (format for webpage & preferred method)
                            - see 'pcs_name' column from Team.get_riders() or Race.get_results() for easy linking

    Returns:
        str: the full url in https://www...com/... format
    """
    
    # the leading url for request
    basic_url = "https://www.procyclingstats.com/rider/"
    # converting the rider name into how pcs needs it
    url_name = test_pcs_name(name)
    # add the two together
    full_url = basic_url + url_name
    
    return full_url

def get_team_url(name: str, year: int):
    """
    Retrieves the url associated with the requested team

    Args:
        name (str): The name of the team as it appears on their PCS page
                    - this can be either in format: 
                        1) "Team Name" (written name ie. with capitals first letter and spaces)
                        2) "team-name" (format for webpage ie. lowercase with dashes)
        year (int): The year of the season for which the team competed

    Returns:
        str: the full url in https://www...com format
    """
    
    # the leading url for request
    basic_url = "https://www.procyclingstats.com/team/"
    # converting the rider name into how pcs needs it
    url_name = test_pcs_name(name)
    # add the them together
    full_url = basic_url + url_name + '-' + str(year)
    
    return full_url

def get_race_url(name: str, year: int, **kwargs):
    """
    Get the various race page urls

    Args:
        name (str): the name of the race
        year (int): the year of the race
        
    Kwargs:
        suffix (str): the page of the race of interest
            - one of:
                1) '' (this gives basic results/final gc page)
                2) 'overview'
                3) 'startlist'
                4) 'history'
                5) 'stages'
                6) str of the pcs_stage_name

    Returns:
        str: the url to request
    """
    # unpack the suffix if presented
    suffix = kwargs.pop('suffix','')
    
    # leading url
    basic_url = "https://www.procyclingstats.com/race/"
    # converting race name and year into how pcs needs it
    url_race = test_pcs_name(name)
    # add all together
    full_url = basic_url + url_race + '/' + str(year) + '/' + suffix
    
    return full_url

def test_pcs_name(name: str):
    """
    Convert passed name into format required for url

    Args:
        name (str): refer to any of get_rider_url, get_team_url, get_race_url for input

    Returns:
        str: an all lowercase, firstname-lastname str
    """

    # check how many spaces there are in the name
    num_spaces = name.count(' ')
    
    # if there is at least one space, then 
    if num_spaces > 0:
        # convert to lowercase and replace the spaces with dashes
        url_name = name.lower()
        # catch error based on how some team names are on the website
        if ' - ' in url_name:
            url_name = url_name.replace(' - ', '-')
        # remove the spaces and turn into dashes
        if ' ' in url_name:
            url_name = url_name.replace(' ', '-')
    else:
        # convert to lowercase
        url_name = name.lower()

    return url_name

def convert_printed_rider_to_first_last(printed_name: str):
    """
    Changes a name written as LAST First on PCS website to First Last format

    Args:
        printed_name (str): the input name in LAST First format

    Returns:
        str: the output name in First Last format
    """
    
    # name is last first, need to re order - first step is split into seperate strings
    rider_names = printed_name.split(' ')
    # preset names to empty list
    first_name = []
    last_name = []
    # loop through the list of the name strings
    for name in rider_names:
        # if all uppercase then make lower and capitalize
        if name.isupper():
            last_name = last_name + [name.lower().capitalize()]
        # if not uppercase then its the first name
        else:
            first_name = [name]
    
    # make the organized name back into single string again
    rider_name_list = first_name + last_name
    new_name = " ".join(rider_name_list)
    
    return new_name

def convert_printed_time_to_seconds(printed_time: str):
    """
    converts the printed str time printed on website to a value of seconds

    Args:
        printed_time (str): a time value from PCS website

    Returns:
        int: the time in seconds
    """
    
    # remove any erroneous spaces
    time = printed_time.replace(' ','')
    
    # convert string to seconds
    # if in minutes
    if len(time) <= 5:
        seconds = (datetime.datetime.strptime(time, "%M:%S") - datetime.datetime(1900, 1, 1)).total_seconds()
    # if in hours, but less than 10
    elif len(time) == 7:
        seconds = (datetime.datetime.strptime(time, "%H:%M:%S") - datetime.datetime(1900, 1, 1)).total_seconds()
    # if in hours, but more than 10
    elif len(time) == 8:
        # check if there are more than 24 hours
        hours_extra = int(time[:2]) - 23
        # if the hours extra value is less than 1 that means there weren't any extra hours, proceed as normal
        if hours_extra < 1:
            seconds = (datetime.datetime.strptime(time, "%H:%M:%S") - datetime.datetime(1900, 1, 1)).total_seconds()
        # if hours extra is positive, then need to subtract that from time statement and add in the extra hours using timedelta
        else:
            time = '23' + time[2:]
            seconds = (datetime.datetime.strptime(time, "%H:%M:%S") - datetime.datetime(1900, 1, 1) + datetime.timedelta(hours = hours_extra)).total_seconds()
    # if over 100 hours, has to be above 24 hours 
    elif len(time) == 9:
        hours_extra = int(time[:3]) - 23
        time = '23' + time[3:]
        time = time[1:]
        seconds = (datetime.datetime.strptime(time, "%H:%M:%S") - datetime.datetime(1900, 1, 1) + datetime.timedelta(hours = hours_extra)).total_seconds()

    return seconds

def convert_printed_date_to_standard(printed_date):
    """
    Converts date printed as dd "Month" YYYY to "YYYY-mm-dd"

    Args:
        printed_date (str): the date as printed on pcs stage page

    Returns:
        str: properly formatted date in "YYYY-mm-dd"
    """
    
    # preset dictionary to turn key of named month to number
    months = {'January': '01' ,
              'February' : '02',
              'March' : '03',
              'April' : '04',
              'May' : '05',
              'June' : '06',
              'July' : '07',
              'August' : '08',
              'September' : '09',
              'October' : '10',
              'November' : '11',
              'December' : '12'}

    # split the text into a list
    printed_date = printed_date.split(' ')
    
    # first item is the day
    day = printed_date[0]
    # if only single digit turn into 0 leading
    if len(day) == 1:
        day = '0' + day
    
    # get the month
    month = printed_date[1]
    # convert month to '##'
    new_month = months[month]

    # year is last
    year = printed_date[2]
    
    # put back together as string with '-' sep
    new_date = year + '-' + new_month + '-' + day
    
    return new_date

### Useful functions to list some possible inputs for Race, Team & Rider classes

def list_selectable_race_circuits():
    """
    Creates a list of the circuit types that are supported to be passed to list_races_options()

    Returns:
        list: the supported race circuits to select
            - useful when using list_race_options()
    """
    
    circuits = ['UCI World Tour',
                'UCI Pro Series',
                'UCI World Championships']
    
    return circuits 

def list_selectable_race_classification():
    """
    Create a list of the classification types that are supported to be passed to list_race_options()

    Returns:
        list: the supported race classifications to select from
            - useful when using list_race_options()
    """
    
    classes = ['1.1',
               '1.2',
               '1.2U',
               '1.Ncup',
               '1.Pro',
               '1.UWT',
               '1.WWT',
               '2.1',
               '2.2',
               '2.2U',
               '2.Ncup',
               '2.Pro',
               '2.UWT',
               '2.WWT',
               'CC',
               'NC',
               'WC']
    
    return classes

def list_race_options(year: int, **kwargs):
    """
    Creates a list of all the races avaliable for the given year based on the year and race circuit requested

    Args:
        year (int): the calendar year of racing
    
    Kwargs:
        circuit (str): the circuit type you're interested in (refer to list_selectable_race_circuits())
        classification (str): the classification type you're interested in (refer to list_selectable_race_classification())

    Returns:
        pd.DataFrame: a dataframe of all the races requested with columns:
            - ['year', 'race_name', 'race_href', 'pcs_name', 'classification']
    """
    
    # set the kwargs
    circuit = kwargs.pop('circuit', '')
    classification = kwargs.pop('classification', '')
    
    # need to set the circuit_id based on the requested circuit
    if circuit == 'UCI World Tour':
        circuit_id = str(1)
    elif circuit == 'UCI Pro Series':
        circuit_id = str(26)
    elif circuit == 'UCI World Championships':
        circuit_id = str(2)
    else:
        circuit_id = ''
    
    # create the url based on year, circuit and classification
    url = (
        "https://www.procyclingstats.com/races.php?" + 
        "year=" + str(year) + 
        "&circuit=" + circuit_id + 
        "&class=" + classification + 
        "&filter=Filter"
    )
    # request the url and get soup
    response = req.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # get the table with data in it
    table = soup.find("table", class_ = "basic").find("tbody").find_all("tr")
    
    # preset empty list
    races = []
    
    # loop through each row of the table
    for row in table:
        # identify each column
        columns = row.find_all("td")
        # loop through the columns
        for i, column in enumerate(columns):
            # interested in the race name, href and the pcs name of the race
            if i == 2:
                # printed text
                race = column.find('a').text
                # the href
                race_link = column.find('a', href = True).get('href')
                # the name of the race in href
                pcs_race_loc = race_link[5:].find('/')
                pcs_race_name = race_link[5:pcs_race_loc+5]
                
            elif i == 4:
                race_class = column.text
                
        # concat to list
        races = races + [[year, race, race_link, pcs_race_name, race_class]]

    # convert to dataframe
    races_frame = pd.DataFrame(data = races,
                               columns = ['year', 'race_name',
                                          'race_href', 'pcs_name',
                                          'classification'])
     
    return races_frame

def list_teams_by_year(year: int):
    """
    Returns a list of avaliable teams to request based on the year 

    Args:
        year (int): the year of interest

    Returns:
        pd.DataFrame: the teams for the given year with columns:
            - ['year', 'tour', 'team_name', 'team_href', 'pcs_name']
    """
    # the url to request
    url = (
        "https://www.procyclingstats.com/teams.php?" + 
        "year=" + str(year) + 
        "&filter=Filter"
    )
    # request and soup
    response = req.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # the page 
    page = soup.find("div", class_ = "page-content page-object default")
    
    # the sub grouping of the lists and jerseys
    lists_and_jerseys = page.find_all("div", class_ = "mt20")
    
    # preset empty dictionary
    teams = []
    
    # loop through the sub grouping
    for i, grouping in enumerate(lists_and_jerseys):
        # preset empty list
        current_teams = []
        
        # known that 0 and 2 hold the names of teams
        if i == 0:
            # find the world teams
            wt = grouping.find_all("li")
            # loop through the teams
            for team in wt:
                # extract their names
                team_name = team.find('a').text
                # the href to the team
                team_href = team.find('a', href=True).get('href')
                # the pcs name
                pcs_name = team_href[5:-5]
                # concat to nested list
                current_teams = current_teams + [[year, 'world', team_name, team_href, pcs_name]]
            
            # concat
            teams = teams + current_teams
        
        # do the same for pro teams
        elif i == 2:
            # find the pro teams
            pt = grouping.find_all("li")
            # loop through the teams
            for team in pt:
                # extract their names
                team_name = team.find('a').text
                # the href to the team
                team_href = team.find('a', href=True).get('href')
                # the pcs name
                pcs_name = team_href[5:-5]
                # concat to nested list
                current_teams = current_teams + [[year, 'pro', team_name, team_href, pcs_name]]
            
            # concat   
            teams = teams + current_teams
    
    # convert to dataframe
    team_frame = pd.DataFrame(data = teams,
                              columns = ['year', 'tour', 'team_name', 'team_href', 'pcs_name'])
            
    
    return team_frame

### Functions for results tables

def determine_which_table(soup, type: str):
    
    return

def determine_column_indices(header, columns: list):
    """
    Finding the index of the columns to keep in table using the header

    Args:
        header (BeautifulSoup): the header of the table as a BS4 object
        columns (list): a list of the names of the columns to keep

    Returns:
        list: the indices where the input columns exist
    """

    # preset empty list for column indices
    column_indices = []
    
   # loop through the header
    for i, column in enumerate(header):
        # text of the header column
        text = column.text
        # if the header is in the acceptable list
        if text in columns:
            # concat index & text pairing
            column_indices = column_indices + [i] 
    
    return column_indices

def determine_result_cont_index(restabs, result_type):
    """
    To find the index of the requested result table from the tabs that select the tables

    Args:
        restabs (list): the list of soup objects which let you switch to different results types on PCS website
        result_type (str): the type of result desired 
        

    Returns:
        int: the index to access the desired result table
    """
    # loop through the tabs
    for i, tab in enumerate(restabs):
        # find the text for the tab
        tab_name = tab.find('a').text
        # if that text is the same as requested, take the index
        if tab_name == result_type:
            index = i
    
    return index

def determine_table_output(body, column_names: list, column_indices: list):
    """
    Untangles the data table on PCS and converts to nested list

    Args:
        body: soup object
        column_names (list): the names of the columns to extract - enter them in order as they are on PCS to retain order
        column_indices (list): the indices of the columns to extract

    Returns:
        list: nested list, ordered to be entered into dataframe - columns will change depending upon what is being requested
    """
    
    # preset empty list for the results
    results = []
    
    # loop through the rows in table
    for i, row in enumerate(body):
        
        # find all the columns for the given row
        cols = row.find_all('td')
        # only keep the column indices of choice
        cols = [x for i, x in enumerate(cols) if i in column_indices]
        
        # preset empty list for current row
        current_result = []
        
        # loop through the columns that have been kept
        for col, col_title in zip(cols, column_names):
            # extract rank
            if col_title == 'Rnk':
                rider_rank = col.text
                current_result = current_result + [rider_rank]
            # extract rider name
            elif col_title == 'Rider':
                rider_name = convert_printed_rider_to_first_last(col.find('a').text)
                rider_href = col.find('a', href = True).get('href')
                rider_pcs_name = rider_href[6:]
                current_result = current_result + [rider_name, rider_href, rider_pcs_name]
            # extract the team name
            elif col_title == 'Team':
                team_name = col.find('a').text
                team_href = col.find('a', href = True).get('href')
                team_pcs_name = team_href[5:-5]
                current_result = current_result + [team_name, team_href, team_pcs_name]
            # extract uci points
            elif col_title == 'UCI':
                uci_points = col.text
                current_result = current_result + [uci_points]
            # extract pcs points
            elif col_title == 'Pnt':
                pcs_points = col.text
                current_result = current_result + [pcs_points]
            # extract time
            elif col_title == 'Time':
                # first row has winning time
                if i == 0:
                    time = col.text
                    time = convert_printed_time_to_seconds(time)
                    winning_time = time
                    time_gap = 0
                # if not first row, need to reference the winning time to get total time of each rider
                else:
                    # when the rider recorded a time
                    try:
                        time_gap = col.find('div', class_="hide").text
                        time_gap = convert_printed_time_to_seconds(time_gap)
                        time = winning_time + time_gap
                    # when the rider didn't record a time (ie. DNF'ed)
                    except:
                        time = col.text
                        time = np.nan
                        time_gap = np.nan
                current_result = current_result + [time, time_gap]
            # extract points for kom/sprint
            elif col_title == 'Points':
                points = col.text
                current_result = current_result + [points]                

        # concat to nested list 
        results = results + [current_result]

    return results

def determine_complementary_points(soup: BeautifulSoup, startlist: pd.DataFrame, column_names: list, point_type: str):
    """_summary_

    Args:
        soup (BeautifulSoup): _description_
        startlist (pd.DataFrame): _description_
        column_names (list): _description_
        point_type (str): _description_
    
    Returns:
        list: 
    """
    
    # all the titles and corresponding tables within data
    possible_titles = soup.find("div", class_ = 'page-content page-object default').find_all('h3')
    possible_tables = soup.find("div", class_ = 'page-content page-object default').find_all('table', class_ = "basic")

    total_points = []
    
    # loop through the titles and tables, getting them together
    for i, (title, table) in enumerate(zip(possible_titles, possible_tables)):
        
        title_text = title.text
                    
        # based on the title of the table was this a sprint point?
        if point_type == 'Sprint':
            # based on the title of the table was this a sprint point?
            if any(['Sprint |' in title_text, 
                    'Points at finish' in title_text, 
                    'Finishline points' in title_text]):
                
                # if so, get header and body
                header = table.find('thead')
                body = table.find('tbody')
                
                # preset empty list for column indices
                column_indices = []
                
                # loop through the header
                for i, column in enumerate(header.find_all('th')):
                    # text of the header column
                    text = column.text
                    # if the header is in the acceptable list
                    if text in column_names:
                        # concat index & text pairing
                        column_indices = column_indices + [i] 
                
                for j, row in enumerate(body.find_all("tr")):
                                
                    # find all the columns for the given row
                    cols = row.find_all('td')
                    
                    # only keep the column indices of choice
                    cols = [x for i, x in enumerate(cols) if i in column_indices]
                    
                    # preset empty list for current row
                    current_points = [title_text]
                    
                    # loop through the columns that have been kept
                    for col, col_title in zip(cols, column_names):
                        
                        if col_title == 'Rnk':
                            current_points = current_points + [int(col.text)]
                        elif col_title == 'Rider':
                            
                            printed_name = col.find('a').text.split(' ')
                            printed_name = list(map(lambda x:x.upper(), printed_name))
                            printed_name[-1] = printed_name[-1].lower().capitalize()
                            printed_name = ' '.join(printed_name)
                            
                            rider_name = convert_printed_rider_to_first_last(printed_name)
                            rider_href = col.find('a', href = True).get('href')
                            rider_pcs_name = rider_href[6:]
                            
                            current_points = current_points + [rider_name, rider_href, rider_pcs_name]
                            
                        elif col_title == 'Team':
                            printed_team = col.text
                            
                            team_row = startlist.loc[(startlist.loc[:,'team_name'] == printed_team), :].copy()
                            team_name = team_row.loc[team_row.index.values[0], 'team_name']
                            team_href = team_row.loc[team_row.index.values[0], 'team_href']
                            team_pcs_name = team_row.loc[team_row.index.values[0], 'team_pcs_name']
                            
                            current_points = current_points + [team_name, team_href, team_pcs_name]
                        elif col_title == 'Points':
                            points = int(col.text)
                            current_points = current_points + [points]   
                        
                    # concat to nested list 
                    total_points = total_points + [current_points]
        elif point_type == 'KOM':
            
            if 'KOM' in title_text:
                
                # if so, get header and body
                header = table.find('thead')
                body = table.find('tbody')
                
                # preset empty list for column indices
                column_indices = []
                
                # loop through the header
                for i, column in enumerate(header.find_all('th')):
                    # text of the header column
                    text = column.text
                    # if the header is in the acceptable list
                    if text in column_names:
                        # concat index & text pairing
                        column_indices = column_indices + [i] 
                
                for j, row in enumerate(body.find_all("tr")):
                                
                    # find all the columns for the given row
                    cols = row.find_all('td')
                    
                    # only keep the column indices of choice
                    cols = [x for i, x in enumerate(cols) if i in column_indices]
                    
                    # preset empty list for current row
                    current_points = [title_text]
                    
                    # loop through the columns that have been kept
                    for col, col_title in zip(cols, column_names):
                        
                        if col_title == 'Rnk':
                            current_points = current_points + [int(col.text)]
                        elif col_title == 'Rider':
                            
                            printed_name = col.find('a').text.split(' ')
                            printed_name = list(map(lambda x:x.upper(), printed_name))
                            printed_name[-1] = printed_name[-1].lower().capitalize()
                            printed_name = ' '.join(printed_name)
                            
                            rider_name = utl.convert_printed_rider_to_first_last(printed_name)
                            rider_href = col.find('a', href = True).get('href')
                            rider_pcs_name = rider_href[6:]
                            
                            current_points = current_points + [rider_name, rider_href, rider_pcs_name]
                            
                        elif col_title == 'Team':
                            printed_team = col.text
                            
                            team_row = startlist.loc[(startlist.loc[:,'team_name'] == printed_team), :].copy()
                            team_name = team_row.loc[team_row.index.values[0], 'team_name']
                            team_href = team_row.loc[team_row.index.values[0], 'team_href']
                            team_pcs_name = team_row.loc[team_row.index.values[0], 'team_pcs_name']
                            
                            current_points = current_points + [team_name, team_href, team_pcs_name]
                        elif col_title == 'Points':
                            points = int(col.text)
                            current_points = current_points + [points]   
                        
                    # concat to nested list 
                    total_points = total_points + [current_points]

    return total_points