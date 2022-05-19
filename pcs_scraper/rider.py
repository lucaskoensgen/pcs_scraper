# general imports
import re
import requests as req
from bs4 import BeautifulSoup
import pandas as pd
# pcs-py specific imports
from .utility import url_management as mgt

# defining the rider class and it's methods
class Rider:

    def __init__(self, name: str):
        """
        Initiates the rider class to get html page relavent to athlete requested

        Args:
            name (str): The name of the rider as it appears on their PCS page
                        - this can be either in format: 
                            1) "FirstName MiddleName LastName" (actual name)
                            2) "firstname-middlename-lastname" (format for webpage)
                        * note in case of duplicate rider name *
                        - also list the number associated to their name by PCS
                        - for example, Benjamin Thomas = benjamin-thomas-2
        """

        # returns the url to request
        self.url = mgt.rider_url(name)
        # the response from the get request
        self.response = req.get(self.url)
        # the beautiful soup object
        self.soup = BeautifulSoup(self.response.content, "html.parser")

    def general_info(self):
        """
        Returns dictionary of useful general purpose information about rider from scraping their PCS homepage

        Returns:
            dict: organized output of general rider info 
                    - keys = {'name', 'team', 'age', 
                              'nationality', 'weight', 'height', 
                              'strava', 'ranks'}
        """
        
        # get all the data for output - add nationality??
        name = self.get_name()
        current_team = self.get_current_team()
        age = self.get_age()
        nationality = self.get_nationality()
        weight = self.get_weight()
        height = self.get_height()
        strava = self.get_strava()
        ranks = self.get_ranks()

        # compose output as dictionary
        out = {'name':name, 
               'team':current_team, 
               'age':age, 
               'nationality':nationality,
               'weight':weight, 
               'height':height, 
               'strava':strava, 
               'ranks':ranks}

        return out
    
    def get_team_history(self):
        """
        Function that returns a riders complete season-by-season team history.
        Also returns teams in future if they are already signed for those seasons

        Returns:
            pd.DataFrame: columns = ['season', 'team_name', 'team_href', 'team_pcs_name', 'team_pcs_year']
        """
        
        # isolate the soup
        soup = self.soup
        # find the teams by current rider
        try: # this works for pre-2018 riders
            teams = soup.body.find("ul", class_ = "list rdr-teams moblist moblist").find_all("li", class_ = "main")
        except: # this works for post-2018 riders (removed a moblist)
            teams = soup.body.find("ul", class_ = "list rdr-teams moblist").find_all("li", class_ = "main")
        # preset empty list
        data = []
        
        # loop through all teams rider has been a part of
        for team in teams:
            # the year
            season = team.find('div', class_='season').text
            # the name of the team
            team_name = team.find('a').text
            # the href to the team
            team_href = team.find('a', href=True).get('href')
            # the pcs name
            team_pcs_name = '-'.join(team_href.split('/')[1].split('-')[:-1])
            # the pcs year
            team_pcs_year = team_href.split('/')[1].split('-')[-1]
            
            # create nested list
            data = data + [[season, team_name, team_href, team_pcs_name, team_pcs_year]]
            
        # turn nested list into dataframe 
        team_frame = pd.DataFrame(data = data,
                                  columns = ['season', 
                                             'team_name', 'team_href', 'team_pcs_name', 'team_pcs_year'])
        
        return team_frame

    def get_race_history(self, **kwargs):
        """
        Returns the rider's complete race history as known by PCS.
        Includes one day races, stages, GC and other minor classification results 

        Returns:
            pd.DataFrame: columns = ['date', 'result', 
                                     'race_name', 'race_href', 'race_pcs_name', 'race_pcs_year',
                                     'classification', 'distance', 
                                     'pcs_points', 'uci_points']
        """
        
        # set the kwargs
        # the season
        season = kwargs.pop('season', '')
        season = str(season)
        # to include ttt or not
        exclude_ttt = kwargs.pop('exclude_ttt', False)
        if exclude_ttt == False:
            exclude_tt = "0"
        elif exclude_ttt == True:
            exclude_tt = "1"
        # the type of race if interested in reducing returned results
        race_type = kwargs.pop('race_type', '')
        if race_type == '':
            pass
        elif race_type == 'stage':
            race_type = "1"
        elif race_type == 'prologue':
            race_type = "2"
        elif race_type == 'tt' or race_type == 'time_trial':
            race_type = "3"
        elif race_type == 'gc' or race_type == 'general_classification':
            race_type = "4"
        elif race_type == 'sprint' or race_type == 'points_classification':
            race_type = "5"
        elif race_type == 'youth' or race_type == 'youth_classification':
            race_type = "6"
        elif race_type == 'kom' or race_type == 'mountains_classification':
            race_type = "7"
        elif race_type == 'one-day':
            race_type = "8"

        # get rider name in pcs format back from the url
        rider_id = self.url.split('/')[-1]
        # use the basic results page for rider 
        results_url = (
            "https://www.procyclingstats.com/" + 
            "rider.php?xseason=" + season +  "&zxseason=" +  
            "&pxseason=equal&sort=date&race=&km1=&zkm1=&pkm1=equal&" +
            "limit=100&offset=0&topx=&ztopx=&ptopx=smallerorequal&" + 
            "type=&" + race_type + 
            "znation=&continent=&pnts=" + 
            "&zpnts=&ppnts=equal&level=&rnk=&zrnk=&prnk=equal&" + 
            "exclude_tt=" + exclude_tt +
            "&racedate=&zracedate=&pracedate=equal" + 
            "&name=&pname=contains&category=&profile_score=&pprofile_score=largerorequal&filter=Filter&"
            "id=" + rider_id + 
            "&p=results"
            )
        # request the page
        results_page = req.get(results_url)
        # turn into soup
        results_soup = BeautifulSoup(results_page.content, "html.parser")
        # find the number of queries needed (pcs will only display 100 results at a time)
        limits = results_soup.find("select", {'name':'offset'}).find_all('option')
        # preset empty list
        data_out = []
        
        # loop through the number of queries
        for limit in limits:
            # turn the value of the offset into str
            limit = str(limit['value'])
            # format new query
            results_url = (
                "https://www.procyclingstats.com/" + 
                "rider.php?xseason=" + season +  "&zxseason=" +  
                "&pxseason=equal&sort=date&race=&km1=&zkm1=&pkm1=equal&limit=100&" + 
                "offset=" + limit + 
                "&topx=&ztopx=&ptopx=smallerorequal&type=&znation=&continent=&pnts=&zpnts=&ppnts=equal&level=&rnk=&zrnk=&prnk=equal&exclude_tt=0&racedate=&zracedate=&pracedate=equal&name=&pname=contains&category=&profile_score=&pprofile_score=largerorequal&filter=Filter&" + 
                "id=" + rider_id + 
                "&p=results"
                )
            # request the page
            results_page = req.get(results_url)
            # turn into soup
            results_soup = BeautifulSoup(results_page.content, "html.parser")
            # find all the rows contained within the table body
            table_rows = results_soup.find("tbody").find_all('tr')
            
            # loop through each row
            for i, row in enumerate(table_rows):
                # if last row, skip
                if i == len(table_rows) - 1:
                    pass
                # otherwise
                else:
                    # find all the columns in given row
                    items = row.find_all('td')
                    # preset empty list
                    race_list = []
                    
                    # loop through the columns
                    for j, val in enumerate(items):
                        # don't need the row number
                        if j == 0:
                            pass
                        # if it's the race column, get the text, the href and the pcs race name
                        elif j == 3:
                            race_name = val.find('a').text
                            race_href = val.find('a', href = True).get('href')
                            race_pcs_name = race_href.split('/')[1]
                            race_pcs_year = race_href.split('/')[-2]
                            race_list = race_list + [race_name, race_href, race_pcs_name, race_pcs_year]
                            
                        # otherwise, just extract the text
                        else:
                            text = val.text
                            if text == '':
                                text = '-'
                            race_list = race_list + [text]
                            
                    # concat the list as nested list
                    data_out = data_out + [race_list]
                    
        # turn nested list of each row into dataframe
        results_frame = pd.DataFrame(data = data_out,
                                     columns = ['date', 'result', 
                                                'race_name', 'race_href', 'race_pcs_name', 'race_pcs_year',
                                                'classification', 'distance', 
                                                'pcs_points', 'uci_points'])


        return results_frame
    
    def get_palmares(self, top = 5):
        """
        Return the top n results for a rider's career in 5 categories
        Top results are based on PCS points for each result

        Parameters
        ----------
        top : int, optional
            The top results to return in each category. The default is 5.

        Returns
        -------
        palmares : dict
            collection of 5 dataframes, organized into 5 categories:
                1. one day races
                2. stage races
                3. final gc
                4. final kom
                5. final points

        """
        
        # get the rider's whole race history
        total_race_hx = self.get_race_history()
        total_race_hx.pcs_points = total_race_hx.pcs_points.replace('-','0')
        total_race_hx.pcs_points = total_race_hx.pcs_points.astype('int')
        
        # store categories in seperate dataframes
        one_day_race_hx = total_race_hx[total_race_hx.loc[:,'race_href'].str.contains('result')].sort_values(by = 'pcs_points', ascending = False).reset_index(drop = True).loc[:top-1, :]
        stage_race_hx = total_race_hx[(total_race_hx.loc[:,'race_name'].str.contains('Stage')) | (total_race_hx.loc[:,'race_name'].str.contains('Prologue'))].sort_values(by = 'pcs_points', ascending = False).reset_index(drop = True).loc[:top-1, :]
        gc_race_hx = total_race_hx[total_race_hx.loc[:,'race_href'].str.contains('gc')].sort_values(by = 'pcs_points', ascending = False).reset_index(drop = True).loc[:top-1, :]
        kom_race_hx = total_race_hx[total_race_hx.loc[:,'race_href'].str.contains('kom')].sort_values(by = 'pcs_points', ascending = False).reset_index(drop = True).loc[:top-1, :]
        points_race_hx = total_race_hx[total_race_hx.loc[:,'race_href'].str.contains('points')].sort_values(by = 'pcs_points', ascending = False).reset_index(drop = True).loc[:top-1, :]
        
        # for exporting
        palmares = {'one_day':one_day_race_hx,
                    'stages':stage_race_hx,
                    'gc':gc_race_hx,
                    'kom':kom_race_hx,
                    'points':points_race_hx}
        
        return palmares

    def get_name(self):
        """
        Gets the rider name from rider HTML

        Returns:
            str: the string of the rider's name as printed on the website
        """

        # isolate the soup
        soup = self.soup
        # navigate through the html to return the name of the rider as printed on pcs
        printed_name = soup.find(class_="page-title").find("h1").text
        
        if '  ' in printed_name:
            printed_name = printed_name.replace('  ', ' ')

        return printed_name
    
    def get_nationality(self):
        
        # isolate soup
        soup = self.soup
        # navigate through html to return the rider nationality 
        nationality = soup.find("div", class_ = "rdr-info-cont").find("a").text
        
        return nationality

    def get_current_team(self):
        """
        Gets the rider's current team from rider HTML

        Returns:
            str: the string of the rider's current team as printed on PCS
        """

        # isolate the soup
        soup = self.soup

        # navigate through the html to return the name of the rider's current team as printed on pcs
        current_team = soup.body.find(class_="page-title").find(class_="main").find_all("span")[-1].text

        return current_team

    def get_age(self):
        """
        Gets the rider's current age from rider HTML
        
        Returns:
            int: their age at time of request
        """
        
        # isolate the soup
        soup = self.soup
        # get the row with the age
        reported_age = soup.body.find(class_ = "rdr-info-cont").text
        # age will be in parenthases
        reported_age_start = reported_age.find('(')
        reported_age_end = reported_age.find(')')
        # slice out the age and turn into an integer
        reported_age = int(reported_age[reported_age_start+1:reported_age_end])

        return reported_age

    def get_height(self):
        """
        Gets the rider's height from rider HTML (if it exists)

        Returns:
            float/None: height of the rider in meters (if doesn't exist, None returned)
        """

        # isolate the soup
        soup = self.soup
        # find the weight using 'm' as the reference lookup and find the first instance
        reported_height = soup.body.find(class_ = "rdr-info-cont").find(string=re.compile(" m"))

        # test if height is reported
        if type(reported_height) == None:
            # return None obj if not there
            reported_height = None
        else:
            # convert to string and then only extract the number
            reported_height = str(reported_height)
            reported_height = float([s for s in reported_height.split()][0])

        return reported_height

    def get_weight(self):
        """
        Gets the weight of a rider from the html (if it exists)
        
        Returns:
            float/None: the weight of the rider in kilograms (None if doesn't exist)
        """

        # isolate the soup
        soup = self.soup
        # find the weight using 'kg' as the reference lookup and find the first instance
        reported_weight = soup.body.find(class_ = "rdr-info-cont").find(string=re.compile(" kg"))

        # test if weight is reported
        if type(reported_weight) == None:
            # return None obj if not there
            reported_weight = None
        else:
            # convert to string and then only extract the number
            reported_weight = str(reported_weight)
            reported_weight = [float(s) for s in reported_weight.split() if s.isdigit()][0]

        return reported_weight
    
    def get_strava(self):
        """
        Get details about the rider's strava page
        
        Returns:
            dict: the url to the rider's strava page and the id number associated with their account for api use
                - keys = {'link', 'id'}
        """

        # isolate the soup
        soup = self.soup
        # find the weight using 'kg' as the reference lookup and find the first instance
        links = soup.body.find(class_ = "list horizontal sites").find_all("a", class_="", href=True)
        # preset empty details
        strava_link = ''
        strava_id = ''
        
        # loop through the links in the horizontal sites
        for link in links:
            # if strava is in the link
            if 'strava' in link:
                # get the href
                strava_link = link.get('href')
                # isolate the strava id
                last_slash_loc = [i for i, x in enumerate(strava_link) if x == '/'][-1]
                strava_id = strava_link[last_slash_loc+1:]
                
        # output as a dictionary
        out = {'link':strava_link,
               'id':strava_id}

        return out

    def get_ranks(self):
        """
        Returns the PCS and UCI ranking for the rider at the time of the request

        Returns:
            dict: pcs and uci ranking
                - keys = {'pcs', 'uci'}
        """

        # isolate the soup
        soup = self.soup

        # find the weight using 'kg' as the reference lookup and find the first instance
        links = soup.body.find("ul", class_ = "list horizontal rdr-rankings").find_all("div", class_='rnk')

        # loop through their links
        for i, link in enumerate(links):
            # pcs is always first
            if i == 0:
                pcs_rank = int(link.text)
            # uci is always second
            elif i == 1: 
                uci_rank = int(link.text)               

        # organize output as dictionary
        out = {'pcs':pcs_rank,
               'uci':uci_rank}

        return out
    
    def get_uci_points_season(self, season):
        """
        Returns the summation UCI points for the season requested
        Does not work for all years on PCS (post 2018 only)
        
        Args:
            season (str/int): The season as a year

        Returns:
            int: number of points accumulated in season
        """        
        
        # the season
        season = str(season)

        # get rider name in pcs format back from the url
        rider_id = self.url.split('/')[-1]
        
        results_url = (
            "https://www.procyclingstats.com/rider.php?" + 
            "date=" + season + "-12-31" +
            "&filter=Filter&" + 
            "id=" + rider_id + 
            "&p=results&s=uci-world-ranking"
            )
        
        # request the page
        results_page = req.get(results_url)
        # turn into soup
        results_soup = BeautifulSoup(results_page.content, "html.parser")
        try:
            # the row with the sum
            points_sum_row = results_soup.find('tr', class_ = "sum").find_all('td')
            # the column with the sum
            uci_points = int(points_sum_row[-1].text)
        except:
            uci_points = int(0)
        
        return uci_points

    def get_pcs_points_season(self, season):
        """
        Returns the summation PCS points for the season requested
                
        Args:
            season (str/int): The season as a year

        Returns:
            int: number of points accumulated in season
        """        
        
        # the season
        season = str(season)

        # get rider name in pcs format back from the url
        rider_id = self.url.split('/')[-1]
        
        results_url = (
            "https://www.procyclingstats.com/rider.php?" + 
            "date=" + season + "-12-31" +
            "&filter=Filter&" + 
            "id=" + rider_id + 
            "&p=results&s=pcs-season-ranking"
            )
        
        # request the page
        results_page = req.get(results_url)
        # turn into soup
        results_soup = BeautifulSoup(results_page.content, "html.parser")
        try:
            # the row with the sum
            points_sum_row = results_soup.find('tr', class_ = "sum").find_all('td')
            # the column with the sum
            pcs_points = int(points_sum_row[-1].text)
        except:
            pcs_points = int(0)
            
        return pcs_points
        

             
    
        
