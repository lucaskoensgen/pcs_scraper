
import requests as req
from bs4 import BeautifulSoup
import pandas as pd

### Useful functions to list some possible inputs for Race, Team & Rider classes

def selectable_race_circuits():
    """
    Creates a list of the circuit types that are supported to be passed to list_races_options()

    Returns:
        list: the supported race circuits to select
            - useful when using race_options_by_year()
    """
    
    circuits = ['UCI World Tour',
                'UCI Pro Series',
                'UCI World Championships']
    
    return circuits 

def selectable_race_classifications():
    """
    Create a list of the classification types that are supported to be passed to list_race_options()

    Returns:
        list: the supported race classifications to select from
            - useful when using race_options_by_year()
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
               'WC',
               'Olympics']
    
    return classes

def race_options_by_year(year: int, **kwargs):
    """
    Creates a list of all the races avaliable for the given year based on the year and race circuit requested

    Args:
        year (int): the calendar year of racing
    
    Kwargs:
        circuit (str): the circuit type you're interested in (refer to list_selectable_race_circuits())
        classification (str): the classification type you're interested in (refer to list_selectable_race_classification())

    Returns:
        pd.DataFrame: a dataframe of all the races requested with columns:
            - ['year', 'race_name', 'race_href', 'race_pcs_name', 'race_pcs_year', 'classification']
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
                race_href = column.find('a', href = True).get('href')
                # the name of the race in href
                split_href = race_href.split('/')
                race_pcs_name = split_href[1]
                race_pcs_year = split_href[2]
                
            elif i == 4:
                race_class = column.text
                
        # concat to list
        races = races + [[race, race_href, race_pcs_name, race_pcs_year, race_class]]

    # convert to dataframe
    races_frame = pd.DataFrame(data = races,
                               columns = ['race_name',
                                          'race_href', 'race_pcs_name', 'race_pcs_year',
                                          'classification'])
     
    return races_frame

def teams_by_year(year: int, gender: str):
    """
    Returns a list of avaliable teams to request based on the year & gender

    Args:
        year (int): the year of interest
        gender (str): the gender of interest

    Returns:
        pd.DataFrame: the teams for the given year with columns:
            - ['team_name', 
               'team_href', 'team_pcs_name', 'team_pcs_year', 
               'tour']
    """
    
    if gender == 'Male' or gender == 'M' or gender == 'Men':
        s = 'men'
    elif gender == 'Female' or gender == 'F' or gender == 'Women':
        s = 'women'

    # the url to request
    url = (
        "https://www.procyclingstats.com/teams.php?" + 
        "year=" + str(year) + 
        "&filter=Filter" + 
        "&s=" + s
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
            tour = 'world'
            # find the world teams
            wt = grouping.find_all("li")
            # loop through the teams
            for team in wt:
                # extract their names
                team_name = team.find('a').text
                # the href to the team
                team_href = team.find('a', href=True).get('href')
                # the pcs name
                team_pcs_name = team_href[5:-5]
                team_pcs_year = team_href[-4:]
                
                # concat to nested list
                current_teams = current_teams + [[team_name, 
                                                  team_href, team_pcs_name, team_pcs_year, 
                                                  tour]]
            
            # concat
            teams = teams + current_teams
        
        # do the same for pro teams
        elif i == 2:
            if gender == 'Male' or gender == 'M' or gender == 'Men':
                tour = 'pro'
            elif gender == 'Female' or gender == 'F' or gender == 'Women':
                tour = 'continental'
            # find the pro teams
            pt = grouping.find_all("li")
            # loop through the teams
            for team in pt:
                # extract their names
                team_name = team.find('a').text
                # the href to the team
                team_href = team.find('a', href=True).get('href')
                # the pcs name
                team_pcs_name = team_href[5:-5]
                team_pcs_year = team_href[-4:]
                # concat to nested list
                current_teams = current_teams + [[team_name, 
                                                  team_href, team_pcs_name, team_pcs_year, 
                                                  tour]]
            
            # concat   
            teams = teams + current_teams
    
    # convert to dataframe
    team_frame = pd.DataFrame(data = teams,
                              columns = ['team_name', 
                                         'team_href', 'team_pcs_name', 'team_pcs_year',
                                         'tour'])
            
    
    return team_frame

