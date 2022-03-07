import re
import requests as req
from bs4 import BeautifulSoup
import pandas as pd
import utility as utl

class Team:
    def __init__(self, name: str, year: int):
        """
        Initiates the Team class to get html page relavent to team requested

        Args:
            name (str): the team name
                - either in "Team Name" or "team-name" format
                    - With "Team Name" format, all ' ' are turned into '-' and everything is made lowercase
                    - Preferred to use "team-name" format from utl.list_teams_by_year().loc[:,'pcs_name'] or Rider.get_team_history().loc[:,'pcs-name]
                        - PCS can store name slightly different to what you expect from actual team name
            year (int): the year of the team
        """
        
        # returns the url to request
        self.url = utl.get_team_url(name, year)
        # get the response from url
        self.response = req.get(self.url)
        # create the soup
        self.soup = BeautifulSoup(self.response.content, "html.parser")
        
    def get_riders(self):
        """
        Returns a dataframe of the riders on the team ordered alphabetically 

        Returns:
            rider_frame (pd.DataFrame): dataframe with columns of ['rider_name', 'rider_href', 'pcs_name']
                - Rider: the name of the rider
                - Rider_Link: the url to request to get a rider's page
        """
        
        # isolate the soup
        soup = self.soup
        # table including all riders for year
        riders_table = soup.find("div", class_ = "ttabs tabb").find("ul", class_ = "list pad2").find_all("li")
        
        # preset empty list for riders
        riders = []
        
        # loop through the table of riders
        for row in riders_table:
            
            # get the name
            rider_name = row.find('a').text
            new_rider_name = utl.convert_printed_rider_to_first_last(rider_name)
            
            # the link to for the rider
            rider_href = row.find('a', href=True).get('href')
            # just their pcs name
            pcs_name = rider_href[6:]
                        
            # add nested list to list of riders
            riders = riders + [[new_rider_name, rider_href, pcs_name]]
        
        # turn nested list into a dataframe
        rider_frame = pd.DataFrame(data = riders,
                                   columns = ['rider_name', 'rider_href', 'pcs_name'])
        
        return rider_frame
    
    def get_race_history(self):
        """
        Returns the races the team participated in

        Returns:
            races_frame (pd.DataFrame): dataframe with columns of ['date', 'race_name', 'race_href', 'pcs_name']
                - Date: the start date of the race
                - Race: the name of the race the team was in
                - Race_Link: the url to request to get a races page
        """
        # id for searching using php is team name
        id = self.url[37:]
        # since year is used in php as well
        since_year = self.url[-4:]
        
        # the 2 race types that will incorperate all of the races a team was in
        race_types = ['Stage Race', 'One Day']
        
        # preset an empty list
        races = []
        
        # loop through the types of races
        for race_type in race_types:
            # set the type loc
            if race_type == 'Stage Race':
                type_loc = str(4)
            elif race_type == 'One Day':
                type_loc = str(8)
            # generate the request url based on type loc
            url = (
                "https://www.procyclingstats.com/team.php" +
                "?racetype=" + type_loc + 
                "&race_nation=&" +
                "since_year=" + since_year +  
                "&psince_year=largerorequal&parcours_type=&limit=250&filter=Filter&" + 
                "id=" + id +  
                "&p=results&s=best-result-per-race"
            )
            
            # get the request and turn to soup
            response = req.get(url)
            soup = BeautifulSoup(response.content, "html.parser")
            
            # the table of interest
            race_table = soup.find("table", class_ = "basic").find("tbody").find_all("tr")
            
            # loop through each row
            for row in race_table:
                # find each column of the row
                columns = row.find_all("td")
                # loop through the columns
                for i, column in enumerate(columns):
                    # take the date of the race
                    if i == 1:
                        date = column.text
                    # take the name of the race and the link
                    elif i == 4:
                        # text
                        race_name = column.find('a').text
                        # href
                        race_href = column.find('a', href = True).get('href')
                        # the name of the race in href
                        pcs_race_loc = race_href[5:].find('/')
                        pcs_race_name = race_href[5:pcs_race_loc+5]
                
                # store as a nested list
                races = races + [[date, race_name, race_href, pcs_race_name]]

        # turn nested lists into a dataframe
        races_frame = pd.DataFrame(data = races, 
                                   columns = ['date', 'race_name', 'race_href', 'pcs_name'])
        
        # remove any national championships
        races_frame = races_frame.loc[(races_frame.loc[:,'Race'].str.contains("National") == False), :]
        
        return races_frame            