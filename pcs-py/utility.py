
import re 
import requests as req
from bs4 import BeautifulSoup
import pandas as pd

### General Purpose Functions

def get_rider_url(name:str):
    """
    Retrieves the url associated with the requested rider

    Args:
        name (str): The name of the rider as it appears on their PCS page
                    - this can be either in format: 
                        1) "FirstName MiddleName LastName" (actual name)
                        2) "firstname-middlename-lastname" (format for webpage)
                    * note in case of duplicate rider name *
                    - for example, Benjamin Thomas, also list the number associated to their name by PCS

    Returns:
        str: the full url in https://www...com format
    """
    
    # the leading url for request
    basic_url = "https://www.procyclingstats.com/rider/"
    # converting the rider name into how pcs needs it
    url_name = test_rider_name(name)
    # add the two together
    full_url = basic_url + url_name
    
    return full_url

def test_rider_name(name: str):
    """
    Convert passed name into format required for url

    Args:
        name (str): refer to get_rider_url

    Returns:
        str: an all lowercase, firstname-lastname str
    """

    # check how many spaces there are in the name
    num_spaces = name.count(' ')
    
    # if there is at least one space, then 
    if num_spaces > 0:
        # convert to lowercase and replace the spaces with dashes
        url_name = name.lower()
        url_name = url_name.replace(' ', '-')
    else:
        # convert to lowercase
        url_name = name.lower()

    return url_name

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
    url_name = test_team_name(name, year)
    # add the two together
    full_url = basic_url + url_name
    
    return full_url

def test_team_name(name: str, year: int):
    """
    Convert passed team into format required for url

    Args:
        name (str): refer to get_team_url
        year (int): refer to get_team_url

    Returns:
        str: an all lowercase, team-name-year str
    """

    # check how many spaces there are in the name
    num_spaces = name.count(' ')
    
    # if there is at least one space, then 
    if num_spaces > 0:
        # convert to lowercase and replace the spaces with dashes
        url_name = name.lower()
        url_name = url_name.replace(' ', '-')
    else:
        # convert to lowercase
        url_name = name.lower()
    
    # add the year
    url_name = url_name + '-' + str(year)

    return url_name

### Useful functions to list some possible inputs for Race, Team & Rider classes

def list_selectable_race_circuits():
    """
    Creates a list of the circuit types that are supported to be passed to list_races_by_circuit()

    Returns:
        circuits (list): a list of the supported race circuits to select
            - useful when using list_races_by_circuit()
    """
    
    circuits = ['UCI Worldtour',
                'UCI ProSeries',
                'UCI World Championships']
    
    return circuits 

def list_races_by_circuit(year: int, circuit: str):
    """
    Creates a list of all the races avaliable for the given year based on the year and race circuit requested

    Args:
        year (int): the calendar year of racing
        circuit (str): the race circuit (refer to list_selectable_race_circuits() for supported options)

    Returns:
        races (list) : a list of all the races for the given year and race circuit 
    """
    
    # need to set the circuit_id based on the requested circuit
    if circuit == 'UCI World Tour':
        circuit_id = str(1)
    elif circuit == 'UCI ProSeries':
        circuit_id = str(26)
    elif circuit == 'UCI World Championships':
        circuit_id = str(2)
    
    # create the url based on year and circuit
    url = (
        "https://www.procyclingstats.com/races.php?" + 
        "year=" + str(year) + 
        "&circuit=" + circuit_id + 
        "&class=&filter=Filter"
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
            #only interested in the race name
            if i == 2:
                race = column.find('a').text
        # add to list
        races = races + [race]

    return races

def list_teams_by_year(year: int):
    """
    Returns a list of avaliable teams to request based on the year 

    Args:
        year (int): the year of interest

    Returns:
        teams (dict): a dict of lists of teams for that year 
            - keys:
                - 'World Teams'
                - 'Pro Teams'
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
    teams = {}
    
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
                # if '-' in team_name: *** NEED TO SOLVE HOW TEAM WITH DASH WILL WORK WHEN REQUESTING
                
                # add to list
                current_teams = current_teams + [team_name]
            # assign key the list
            teams['World Teams'] = current_teams
        
        # do the same for pro teams
        elif i == 2:
 
            pt = grouping.find_all("li")
            
            for team in pt:
                
                team_name = team.find('a').text

                current_teams = current_teams + [team_name]
                
            teams['Pro Teams'] = current_teams
            
    
    return teams