import re
import requests as req
from bs4 import BeautifulSoup
import pandas as pd
class rider:

    def __init__(self, name: str):
        """
        Initiates the rider class to get html page relavent to athlete requested

        Args:
            name (str): The name of the rider as it appears on their PCS page
                        - this can be either in format: 
                            1) "FirstName MiddleName LastName" (actual name)
                            2) "firstname-middlename-lastname" (format for webpage)
                        * note in case of duplicate rider name *
                        - for example, Benjamin Thomas, also list the number associated to their name by PCS
        """

        # returns the url to request
        self.url = get_rider_url(name)

        # the response from the get request
        self.response = req.get(self.url)

        # the beautiful soup object
        self.soup = BeautifulSoup(self.response.content, "html.parser")

    def general_info(self):

        name = self.get_name()
        current_team = self.get_current_team()
        age = self.get_age()
        weight = self.get_weight()
        height = self.get_height()
        strava = self.get_strava()
        ranks = self.get_ranks()

        out = {'name':name, 
        'team':current_team, 
        'age':age, 
        'weight':weight, 
        'height':height, 
        'strava':strava, 
        'ranks':ranks}

        return out

    def get_name(self):
        """
        - Method of rider object
        - Gets the rider name from rider HTML

        Returns:
            printed_name (str): the string of the rider's name as printed on the website
        """

        # isolate the soup
        soup = self.soup

        # navigate through the html to return the name of the rider as printed on pcs
        printed_name = soup.body.find(class_="page-title").find("h1").text

        return printed_name

    def get_current_team(self):
        """
        - Method of rider object
        - Gets the rider's current team from rider HTML

        Returns:
            current_team (str): the string of the rider's current team as printed on PCS
        """

        # isolate the soup
        soup = self.soup

        # navigate through the html to return the name of the rider's current team as printed on pcs
        current_team = soup.body.find(class_="page-title").find(class_="main").find_all("span")[-1].text

        return current_team

    def get_age(self):
        
        # isolate the soup
        soup = self.soup

        reported_age = soup.body.find(class_ = "rdr-info-cont").text

        reported_age_start = reported_age.find('(')

        reported_age_end = reported_age.find(')')

        reported_age = int(reported_age[reported_age_start+1:reported_age_end])

        return reported_age

    def get_height(self):

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
        - Method of rider object
        - Gets the weight of a rider from the html
        - Returns the weight if exists as int or None obj is doesn't

        Returns:
            reported_weight (int): the weight of the rider in kg
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
            reported_weight = [int(s) for s in reported_weight.split() if s.isdigit()][0]

        return reported_weight
    
    def get_strava(self):

        # isolate the soup
        soup = self.soup

        # find the weight using 'kg' as the reference lookup and find the first instance
        links = soup.body.find(class_ = "list horizontal sites").find_all("a", class_="", href=True)

        strava_link = ''
        strava_id = ''

        for link in links:
            if 'strava' in link:
                strava_link = link.get('href')
                last_slash_loc = [i for i, x in enumerate(strava_link) if x == '/'][-1]
                strava_id = strava_link[last_slash_loc+1:]

        out = {'link':strava_link,
        'id':strava_id}

        return out

    def get_ranks(self):

        # isolate the soup
        soup = self.soup

        # find the weight using 'kg' as the reference lookup and find the first instance
        links = soup.body.find("ul", class_ = "list horizontal rdr-rankings").find_all("div", class_='rnk')

        for i, link in enumerate(links):
            if i == 0:
                pcs_rank = int(link.text)
            elif i == 1: 
                uci_rank = int(link.text)               

        out = {'pcs':pcs_rank,
        'uci':uci_rank}

        return out

    def get_team_history(self):
        
        # isolate the soup
        soup = self.soup

        # find the weight using 'kg' as the reference lookup and find the first instance
        teams = soup.body.find("ul", class_ = "list rdr-teams moblist moblist").find_all("li", class_ = "main")
        
        data = []
        
        for team in teams:
            year = team.find('div', class_='season').text
            team_name = team.find('a').text
            team_link = "https://www.procyclingstats.com/" + team.find('a', href=True).get('href')
            
            data = data + [[year, team_name, team_link]]
            
        team_frame = pd.DataFrame(data = data,
                                  columns = ['Year', 'Team_Name', 'Team_Link'])
        
        return team_frame

    def get_race_history(self):
        
        rider_id = self.url.split('/')[-1]
        
        results_url = (
            "https://www.procyclingstats.com/" + 
            "rider.php?xseason=&zxseason=&pxseason=equal&sort=date&race=&km1=&zkm1=&pkm1=equal&" +
            "limit=100&offset=0&topx=&ztopx=&ptopx=smallerorequal&type=&znation=&continent=&pnts=" + 
            "&zpnts=&ppnts=equal&level=&rnk=&zrnk=&prnk=equal&exclude_tt=0&racedate=&zracedate=&pracedate=equal" + 
            "&name=&pname=contains&category=&profile_score=&pprofile_score=largerorequal&filter=Filter&id=" + rider_id + "&p=results"
            )

        results_page = req.get(results_url)

        results_soup = BeautifulSoup(results_page.content, "html.parser")

        limits = results_soup.find("select", {'name':'offset'}).find_all('option')

        data_out = []

        for limit in limits:
            
            limit = str(limit['value'])

            results_url = (
                "https://www.procyclingstats.com/" + 
                "rider.php?xseason=&zxseason=&pxseason=equal&sort=date&race=&km1=&zkm1=&pkm1=equal&limit=100&" + 
                "offset=" + limit + "&topx=&ztopx=&ptopx=smallerorequal&type=&znation=&continent=&pnts=&zpnts=&ppnts=equal&level=&rnk=&zrnk=&prnk=equal&exclude_tt=0&racedate=&zracedate=&pracedate=equal&name=&pname=contains&category=&profile_score=&pprofile_score=largerorequal&filter=Filter&" + 
                "id=" + rider_id + "&p=results"
                )

            results_page = req.get(results_url)

            results_soup = BeautifulSoup(results_page.content, "html.parser")

            table_rows = results_soup.find("tbody").find_all('tr')

            for i, row in enumerate(table_rows):
                
                if i == len(table_rows) - 1:
                    pass
                else:
                    
                    items = row.find_all('td')

                    race_list = []

                    for j, val in enumerate(items):
                        if j == 0:
                            pass
                        elif j == 3:
                            race_list = race_list + [val.find('a').text]
                            race_list = race_list + ['https://www.procyclingstats.com/' + val.find('a', href = True).get('href')]
                        else:
                            race_list = race_list + [val.text]
                    
                    data_out = data_out + [race_list]
        
        results_frame = pd.DataFrame(data = data_out,
                                     columns = ['Date', 'Result', 
                                                'Race', 'Race_Result_Page',
                                                'Class', 'Distance', 
                                                'PCS_Points', 'UCI_Points'])


        return


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
    url_name = test_name(name)

    # add the two together
    full_url = basic_url + url_name
    
    return full_url

def test_name(name: str):
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

def send_request(url: str):
    """[summary]

    Args:
        url (str): [description]

    Returns:
        [type]: [description]
    """

    # get
    response = req.get(url)

    return response
