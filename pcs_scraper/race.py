# general imports
import requests as req
from bs4 import BeautifulSoup
import pandas as pd
# pcs-py specific imports
from .utility import url_management as mgt
from .utility import table_manipulation as tbl
from .utility import convert_data as cvt

# define general race class and it's methods
class Race:
    def __init__(self, name: str, year: int):
        """
        Initiates the Race class and gets html page(s) relevant to race requested

        Args:
            name (str): the name of the race
                - can be in "Race Name" or "race-name" format
                    - "Race Name" should be the common version of what the race is called (will have to spell like what PCS expects)
                        - ' ' gets converted to '-' and everything becomes lowercase
                    - "race-name" is preferred, and is the pcs version of the name 
                        - to get the name, can refer to 'pcs_name' column in 
                            1) Rider.get_race_history()
                            2) Team.get_race_history()
                            3) list_race_options()
            year (int): the year of the race
        """
        
        # returns the url to request
        self.url = mgt.race_url(name, year, suffix = 'overview')
        # get the response from url
        self.response = req.get(self.url)
        # create the soup
        self.soup = BeautifulSoup(self.response.content, "html.parser")
        # get the pcs name out of the url
        self.pcs_name = self.url[37:-14]
        # set the year as a string
        self.year = str(year)
    
    def get_general_info(self):
        """
        Return general information about the race 

        Returns:
            dict: relevant race details with keys: 
                - ['race_name', 'race_edition', 'race_classification',
                   'start_date', 'end_date', 'num_stages']
        """
        
        # get printed name
        printed_name = self.get_printed_name()
        # get the race edition
        edition = self.get_edition()
        # get the race classification
        classification = self.get_race_classification()
        # get the start date
        start_date = self.get_start_date()
        # get the end date
        end_date = self.get_end_date()
        # get the number of stages
        num_stages = self.get_num_stages()
        
        # set up for export
        general_info = {'race_name':printed_name,
                        'race_edition':edition,
                        'race_classification':classification,
                        'start_date':start_date,
                        'end_date':end_date,
                        'num_stages':num_stages}
        
        return general_info
    
    def get_printed_name(self):
        """
        Gets the printed name of the race from preview page

        Returns:
            str: the name printed on the pcs page
        """
        
        # isolate soup
        soup = self.soup
        # extract the race name
        printed_name = soup.find('div', class_ = "page-title").find('div', class_ = "main").find("h1").text
        # remove erroneous extra spaces
        printed_name = printed_name.replace('  ', ' ')
        
        return printed_name
    
    def get_edition(self):
        """
        Gets the edition of the race according to PCS

        Returns:
            str: race edition without the 'th' or 'nd' or 'st'
        """
        
        # isolate soup
        soup = self.soup
        # extract the useful title details
        title_row = soup.find('div', class_ = "page-title").find('div', class_ = "main").find_all("font")
        # extract edition number
        edition = title_row[0].text[:-2]
        
        return edition
    
    def get_race_classification(self):
        """
        Gets the race classification from the title of the race
        
        Returns:
            str: the race classification (ie. 1.UWT)
        """

        # isolate soup
        soup = self.soup
        # extract the useful title details
        title_row = soup.find('div', class_ = "page-title").find('div', class_ = "main").find_all("font")
        # extract classification text without parenthases - if it's the first time the race is run, no edition so its the first in list
        if len(title_row) == 1:
            classification = title_row[0].text.replace('(', '').replace(')', '')
        else:
            classification = title_row[1].text.replace('(', '').replace(')', '')
        
        return classification
    
    def get_start_date(self):
        """
        Gets the first day of the race 

        Returns:
            str: the date the race starts in YYYY-MM-DD format
        """
        
        # isolate soup
        soup = self.soup
        # extract the useful table details
        table = soup.find('div', class_ = "page-content page-object default").find('div', class_ = "w47 left mb_w100").find("ul", class_ = "infolist fs13").find_all("li")
        # get start date text
        start_date = table[0].find_all("div")[1].text
        
        return start_date
    
    def get_end_date(self):
        """
        Gets the last day of the race

        Returns:
            str: the date the race ends in YYYY-MM-DD format
        """
        
        # isolate soup
        soup = self.soup
        # extract the useful table details
        table = soup.find('div', class_ = "page-content page-object default").find('div', class_ = "w47 left mb_w100").find("ul", class_ = "infolist fs13").find_all("li")
        # get end date text
        end_date = table[1].find_all("div")[1].text

        return end_date
    
    def get_num_stages(self):
        """
        Gets the number of stages

        Returns:
            int: the number of stages in this race (one day races are listed as having 1 stage)
        """
        
        # isolate soup
        soup = self.soup
        # if there are stages
        try:
            # extract the useful table details
            table = soup.find('div', class_ = "page-content page-object default").find('div', class_ = "w47 left mb_w100").find("ul", class_ = "list pad2 flex fs14").find_all("li")
            # get the number of stages by the length of the table then removing restdays
            num_stages = len(table)
            # loop through table
            for row in table:
                # remove a stage for every rest day
                if row.find_all("div")[3].text == 'Restday':
                    num_stages = num_stages - 1
        # if it's a one day race
        except:
            num_stages = 1
        
        return num_stages
     
    def get_startlist(self):
        """
        Returns the startlist of a race as a dataframe

        Returns:
            pd.DataFrame: the startlist with each rider and their team identified with columns:
                            - ['team_name', 'team_href', 'team_pcs_name', 'team_pcs_year'
                               'rider_name', 'rider_href', 'rider_pcs_name']
            
        """
        
        # get the soup for startlist page
        url = mgt.race_url(self.pcs_name, self.year, suffix = 'startlist')
        response = req.get(url)
        soup = BeautifulSoup(response.content, "html.parser")
        
        # the table of teams
        table = soup.find("ul", class_ = "startlist_v3").find_all("li", class_ = "team")
        
        # preset empty list
        startlist = []
        
        # loop through each team
        for team in table:
            
            # find basic team info
            team_name = team.find("b").find("a").text
            team_href = team.find("b").find("a", href = True).get('href')
            team_pcs_name = team_href[5:-5]
            team_pcs_year = team_href[-4:]
            
            # find all riders in team
            riders = team.find("ul").find_all("li")
            
            # loop through each rider
            for rider in riders:
                # extract text name and convert to First Last
                rider_name = rider.find("a").text
                new_rider_name = cvt.printed_rider_to_first_last(rider_name)
                
                # get rider href & pcs name
                rider_href = rider.find("a", href = True).get('href')
                rider_pcs_name = rider_href[6:]
                
                startlist = startlist + [[team_name, team_href, team_pcs_name, team_pcs_year,
                                          new_rider_name, rider_href, rider_pcs_name]]
                
        # export as dataframe
        startlist_frame = pd.DataFrame(data = startlist,
                                       columns = ['team_name', 'team_href', 'team_pcs_name', 'team_pcs_year',
                                                  'rider_name', 'rider_href', 'rider_pcs_name'])
        
        return startlist_frame
        
    def get_results(self):
        """
        Returns a dataframe of the general race results. 
        For one day races this is the result of the single race, whereas for stage races this is the overall GC results
        
        - If you're interested in individual stage results during a stage race, see get_stage_result()
        - If you're interested in GC/KOM/Sprint results after a stage, see get_running_gc_time(), get_running_kom_points(), get_running_sprint_points()
        - If you're interested in KOM/Sprint results during a stage, see get_stage_kom_points(), get_stage_sprint_points()
        - For all the above, refer to get_stages() for a dataframe of all the stages in the given race

        Returns:
            pd.DataFrame: the main results table for race 
                            - columns: ['rank',
                                        'rider_name', 'rider_href', 'rider_pcs_name',
                                        'team_name', 'team_href', 'team_pcs_name', 'team_pcs_year',
                                        'uci_points', 'pcs_points', 
                                        'time', 'time_gap',]
        """
        
        # get the soup for results page
        url = mgt.race_url(self.pcs_name, self.year)
        response = req.get(url)
        soup = BeautifulSoup(response.content, "html.parser")
        
        # the header of results - all the headers will be the same
        possible_headers = soup.find("div", class_ = "page-content page-object default").find_all("div", class_ = "result-cont")
        # the table of results - need the second one if a stage race
        possible_tables = soup.find("div", class_ = "page-content page-object default").find_all("div", class_ = "result-cont")
        
        # if only one, take it (this is for one day races)
        if len(possible_tables) == 1:
            table = possible_tables[0]
            header = possible_headers[0]
        # if multiple tables, take the second one (ie. final gc standings)
        else:
            table = possible_tables[1]
            header = possible_headers[1]
        
        # most all races fall into this category 
        try:
            table_header = header.find('table', class_ = "results basic moblist10").find('thead').find_all('th')
            table_body = table.find('table', class_ = "results basic moblist10").find('tbody').find_all('tr')
            
            # preset the acceptable strings for columns 
            columns_to_keep = ['Rnk', 'Rider', 'Team', 'UCI', 'Pnt', 'Time']
            
            column_indices = tbl.column_indices(table_header, columns_to_keep)
            
            results = tbl.table_output(table_body, columns_to_keep, column_indices)
        
        # exception is one day TTT races (ie. CC/WC TTT)
        except:
            # 
            table_body = table.find('table', class_ = "results-ttt").find('tbody').find_all('tr')
            table_header = table.find('table', class_ = "results-ttt").find('thead').find_all('th')
    
            # get the correct columns
            columns_to_keep = ['Pos.', 'Team', 'Time', 'PCS points', 'UCI points']
            column_indices = tbl.column_indices(table_header, columns_to_keep)
            
            # get nested list of table results
            results = tbl.table_output_ttt(table_body, columns_to_keep, column_indices)
                
        # convert to dataframe for export
        results_frame = pd.DataFrame(data = results,
                                     columns = ['rank', 
                                                'rider_name', 'rider_href', 'rider_pcs_name',
                                                'team_name', 'team_href', 'team_pcs_name', 'team_pcs_year',
                                                'uci_points', 'pcs_points',
                                                'time', 'time_gap'])
                
        return results_frame
    
    def get_stages(self):
        """
        Returns a dataframe of the stages in this race and their PCS reference names.
        Useful for querying information specific about a stage
            - ie. specfic stage results/gc standings after stage

        Returns:
            pd.DataFrame: dataframe of the stages in current race. 
                            - columns = ['date', 
                                         'stage_name', 'stage_number', 
                                         'stage_href', 'stage_pcs_name']
        """
        
        # get the soup for results page
        url = mgt.race_url(self.pcs_name, self.year, suffix = 'stages')
        response = req.get(url)
        soup = BeautifulSoup(response.content, "html.parser")
        
        # the data table
        table = soup.find('div', class_ = "page-content page-object default").find('tbody').find_all('tr')
        
        # preset empty list
        stages = []
        
        # loop through table rows
        for i, row in enumerate(table):
            # find the columns in row
            columns = row.find_all('td')
            
            stage_number = i + 1
            
            # loop through the columns
            for j, col in enumerate(columns):
                
                if j == 0:
                    date = str(self.year) + '-' + col.text.replace('/','-')
                elif j == 2:
                    stage_name = col.find('a').text
                    stage_href = col.find('a', href = True).get('href')
                    stage_pcs_name = stage_href.split('/')[-1]
                    
            
            stages = stages + [[date,
                                stage_name, stage_number,
                                stage_href, stage_pcs_name]]
        
        # special case of paris-nice 2020, race was cancelled at last stage
        if self.pcs_name == 'paris-nice' and self.year == '2020':
            stages = stages[:-1]
        # special case of uae tour 2020, race was cancelled at last 2 stages
        elif self.pcs_name == 'uae-tour' and self.year == '2020':
            stages = stages[:-2]
    
        stages_frame = pd.DataFrame(data = stages,
                                    columns = ['date', 
                                               'stage_name', 'stage_number',
                                               'stage_href', 'stage_pcs_name'])
        
        # account for if race had a prologue
        if 'Prologue' in stages_frame.loc[0,'stage_name']:
            stages_frame.loc[:, 'stage_number'] = stages_frame.loc[:, 'stage_number'] - 1
                                        
        return stages_frame
    
    def get_stage_info(self, pcs_stage: str):
        """
        Gets defining details about the stage as a dictionary

        Args:
            pcs_stage (str): the suffix to the stage for pcs, OR 'one-day-race'

        Returns:
            dict: a dict with general info about the stage
                    - keys: ['date', 'start_time', 'distance', 
                             'parcours_type', 'finish_type', 
                             'profile_score', 'vertical_meters',
                             'startlist_score']
        """
        
        if pcs_stage == 'one-day-race':
            # get the soup for results page
            url = mgt.race_url(self.pcs_name, self.year)
            response = req.get(url)
            soup = BeautifulSoup(response.content, "html.parser")
        else:
            # get the soup for results page
            url = mgt.race_url(self.pcs_name, self.year, suffix = pcs_stage)
            response = req.get(url)
            soup = BeautifulSoup(response.content, "html.parser")
        
        # the data table
        table = soup.find('div', class_ = 'w30 right mb_w100').find('ul', class_ = 'infolist').find_all('li')
        # preset empty dict
        info = {}
        
        # loop through the table rows
        for i, row in enumerate(table):
            # if first, it's the date
            if i == 0:
                # extract the date and convert to correct format
                printed_date = row.find_all('div')[1].text
                info['date'] = cvt.printed_date_to_standard(printed_date)
            # if second, its the start time
            elif i == 1:
                info['start_time_local'] = row.find_all('div')[1].text.split(' ')[0]
            # fifth = the course distance
            elif i == 4:
                info['distance_km'] = row.find_all('div')[1].text.split(' ')[0]
            # seventh, the parcours and finish
            elif i == 6:
                parcours_type = row.find_all('div')[1].find('span').get('class')[-1]
                if parcours_type == 'p1':
                    info['parcours_type'] = 'flat'
                    info['finish_type'] = 'flat'
                elif parcours_type == 'p2':
                    info['parcours'] = 'hilly'
                    info['finish_type'] = 'flat'
                elif parcours_type == 'p3':
                    info['parcours_type'] = 'hilly'
                    info['finish_type'] = 'uphill'
                elif parcours_type == 'p4':
                    info['parcours_type'] = 'mountain'
                    info['finish_type'] = 'flat'
                elif parcours_type == 'p5':
                    info['parcours_type'] = 'mountain'
                    info['finish_type'] = 'uphill'
            # eighth, profile score
            elif i == 7:
                info['profile_score'] = row.find_all('div')[1].text
            # ninth, vertical meters
            elif i == 8:
                info['vertical_meters'] = row.find_all('div')[1].text
                # thirteenth, how was the race won
            elif i == 12:
                info['startlist_score'] = row.find_all('div')[1].text

        return info
    
    def get_stage_result(self, pcs_stage: str):
        """
        Returns a dataframe of the time-based results from the requested stage

        Args:
            pcs_stage (str): the stage name according to PCS (usually in format: 'stage-#')
            
        Returns:
            pd.DataFrame: dataframe organized by finishing place
                            - columns: ['rank', 
                                        'rider_name', 'rider_href', 'rider_pcs_name',
                                        'team_name', 'team_href', 'team_pcs_name'
                                        'uci_points', 'pcs_points', 
                                        'time', 'time_gap']
        """     
        
        # preset the acceptable strings for columns 
        columns_to_keep = ['Rnk', 'Rider', 'Team', 'UCI', 'Pnt', 'Time']
        result_type = 'Stage'
        
        # get the soup for results page
        url = mgt.race_url(self.pcs_name, self.year, suffix = pcs_stage)
        response = req.get(url)
        soup = BeautifulSoup(response.content, "html.parser")
        
        
        if any([x in soup.find("div", class_ = "w68 left mb_w100").find("div").text for x in ["cancelled", "Cancelled",
                                                                                              "Coronavirus", "coronavirus", 
                                                                                              "Corona-virus", "corona-virus"]]):
            results = pd.DataFrame()
        else:
            # get the tabs and find the correct tab index
            restabs = soup.find("div", class_ = "page-content page-object default").find("ul", class_ = "restabs").find_all("li")
            tab_index = tbl.result_cont_index(restabs, result_type)
            
            # find table based on the tab index then break into head and body
            table = soup.find("div", class_ = "page-content page-object default").find("div", class_ = "w68 left mb_w100").find_all("div", class_ = "result-cont")[tab_index]
            
            # try this for everything non-TTT
            try:
                table_body = table.find('table', class_ = "results basic moblist10").find('tbody').find_all('tr')
                table_header = table.find('table', class_ = "results basic moblist10").find('thead').find_all('th')
                
                # get the correct columns
                column_indices = tbl.column_indices(table_header, columns_to_keep)
                
                # get nested list of table results
                results = tbl.table_output(table_body, columns_to_keep, column_indices)
            
            # assuming if it fails then it was a TTT (watch this space for updates)
            except:
                table_body = table.find('table', class_ = "results-ttt").find('tbody').find_all('tr')
                table_header = table.find('table', class_ = "results-ttt").find('thead').find_all('th')
                
                # get the correct columns
                columns_to_keep = ['Pos.', 'Team', 'Time', 'PCS points', 'UCI points']
                column_indices = tbl.column_indices(table_header, columns_to_keep)
                
                # get nested list of table results
                results = tbl.table_output_ttt(table_body, columns_to_keep, column_indices)
        
                
        # convert to dataframe for export
        stage_result = pd.DataFrame(data = results,
                                    columns = ['rank',
                                               'rider_name', 'rider_href', 'rider_pcs_name',
                                               'team_name', 'team_href', 'team_pcs_name', 'team_pcs_year',
                                               'uci_points', 'pcs_points',
                                               'time', 'time_gap'])
        
        return stage_result
    
    def get_running_gc_time(self, pcs_stage: str):
        """
        Returns a dataframe of the total sum of time accumulated for each rider by the end of the given stage

        Args:
            pcs_stage (str): the stage name according to PCS (usually in format: 'stage-#')

        Returns:
            pd.DataFrame: a dataframe organized by race time
                            - columns:['rank', 
                                       'rider_name', 'rider_href', 'rider_pcs_name',
                                       'team_name', 'team_href', 'team_pcs_name', 'team_pcs_year',
                                       'uci_points', 
                                       'time', 'time_gap']
        """
                
        # preset the acceptable strings for columns & tab of interest
        columns_to_keep = ['Rnk', 'Rider', 'Team', 'UCI', 'Time']
        result_type = 'GC'
        
        # get the soup for results page
        url = mgt.race_url(self.pcs_name, self.year, suffix = pcs_stage)
        response = req.get(url)
        soup = BeautifulSoup(response.content, "html.parser")
        
        # get the tabs and find the correct tab index
        restabs = soup.find("div", class_ = "page-content page-object default").find("ul", class_ = "restabs").find_all("li")
        tab_index = tbl.result_cont_index(restabs, result_type)
        
        # find table based on the tab index then break into head and body
        table = soup.find("div", class_ = "page-content page-object default").find("div", class_ = "w68 left mb_w100").find_all("div", class_ = "result-cont")[tab_index]
        table_body = table.find('table', class_ = "results basic moblist10").find('tbody').find_all('tr')
        table_header = table.find('table', class_ = "results basic moblist10").find('thead').find_all('th')
        
        # get the correct columns
        column_indices = tbl.column_indices(table_header, columns_to_keep)
        
        # get nested list of table results
        results = tbl.table_output(table_body, columns_to_keep, column_indices)
                
        # convert to dataframe for export
        stage_gc = pd.DataFrame(data = results,
                                columns = ['rank', 
                                           'rider_name', 'rider_href', 'rider_pcs_name',
                                           'team_name', 'team_href', 'team_pcs_name', 'team_pcs_year',
                                           'uci_points',
                                           'time', 'time_gap'])
        
        return stage_gc
    
    def get_stage_sprint_points(self, pcs_stage: str):
        """
        Returns a dataframe of each Sprint in a stage and the points awarded 

        Args:
            pcs_stage (str): the stage name according to PCS (usually in format: 'stage-#')

        Returns:
            pd.DataFrame: a dataframe organized by Sprints 
                            - columns = ['sprint_name', 'rank',
                                         'rider_name', 'rider_href', 'rider_pcs_name',
                                         'team_name', 'team_href', 'team_pcs_name', 'team_pcs_year',
                                         'sprint_points'])
        """
        
        startlist = self.get_startlist()
        columns_to_keep = ['Rnk', 'Rider', 'Team', 'Points']
        point_type = "Sprint"
        
        # get the soup for results page
        url = mgt.race_url(self.pcs_name, self.year, suffix = pcs_stage)
        # have to add extra details for this method
        url = url + "/live/complementary-results"
        # request and soup
        response = req.get(url)
        soup = BeautifulSoup(response.content, "html.parser")
        
        # find the points per sprint from complementary page
        sprint_points = tbl.complementary_points(soup, startlist, columns_to_keep, point_type)
        
        # output dataframe
        sprint_frame = pd.DataFrame(data = sprint_points,
                                    columns = ['sprint_name', 'rank',
                                               'rider_name', 'rider_href', 'rider_pcs_name',
                                               'team_name', 'team_href', 'team_pcs_name', 'team_pcs_year',
                                               'sprint_points'])
                        
        return sprint_frame
    
    def get_running_sprint_points(self, pcs_stage: str):
        """
        Returns a dataframe of the total sum of Sprint points accumulated by the end of the given stage

        Args:
            pcs_stage (str): the stage name according to PCS (usually in format: 'stage-#')

        Returns:
            pd.DataFrame: a dataframe organized by Sprint points.
                            - columns:['rank', 
                                       'rider_name', 'rider_href', 'rider_pcs_name',
                                       'team_name', 'team_href', 'team_pcs_name', 'team_pcs_year',
                                       'sprint_points']
        """
        
        # preset the acceptable strings for columns & tab of interest
        columns_to_keep = ['Rnk', 'Rider', 'Team', 'Points']
        result_type = 'Points'

        # get the soup for results page
        url = mgt.race_url(self.pcs_name, self.year, suffix = pcs_stage)
        response = req.get(url)
        soup = BeautifulSoup(response.content, "html.parser")
        
        # get the tabs and find the correct tab index
        restabs = soup.find("div", class_ = "page-content page-object default").find("ul", class_ = "restabs").find_all("li")
        tab_index = tbl.result_cont_index(restabs, result_type)
        
        # find table based on the tab index then break into head and body
        table = soup.find("div", class_ = "page-content page-object default").find("div", class_ = "w68 left mb_w100").find_all("div", class_ = "result-cont")[tab_index]
        table_body = table.find('table', class_ = "results basic moblist10").find('tbody').find_all('tr')
        table_header = table.find('table', class_ = "results basic moblist10").find('thead').find_all('th')
        
        # get the column indices to extract for each row
        column_indices = tbl.column_indices(table_header, columns_to_keep)
        
        # get nested list of table results
        results = tbl.table_output(table_body, columns_to_keep, column_indices)
                
        # convert to dataframe for export
        running_sprint = pd.DataFrame(data = results,
                                      columns = ['rank', 
                                                 'rider_name', 'rider_href', 'rider_pcs_name',
                                                 'team_name', 'team_href', 'team_pcs_name', 'team_pcs_year',
                                                 'sprint_points'])
        
        return running_sprint
    
    def get_stage_kom_points(self, pcs_stage: str):
        """
        Returns a dataframe of each KOM sprint in a stage and the points awarded 

        Args:
            pcs_stage (str): the stage name according to PCS (usually in format: 'stage-#')

        Returns:
            pd.DataFrame: a dataframe organized by KOM sprints 
                            - columns = ['kom_name', 'rank',
                                         'rider_name', 'rider_href', 'rider_pcs_name',
                                         'team_name', 'team_href', 'team_pcs_name', 'team_pcs_year',
                                         'kom_points'])
        """
        
        startlist = self.get_startlist()
        columns_to_keep = ['Rnk', 'Rider', 'Team', 'Points']
        point_type = "KOM"
        
        # get the soup for results page
        url = mgt.race_url(self.pcs_name, self.year, suffix = pcs_stage)
        # have to add extra details for this method
        url = url + "/live/complementary-results"
        # request and soup
        response = req.get(url)
        soup = BeautifulSoup(response.content, "html.parser")

        # find the points per sprint from complementary page
        kom_points = tbl.complementary_points(soup, startlist, columns_to_keep, point_type)
        
        kom_frame = pd.DataFrame(data = kom_points,
                                    columns = ['kom_name', 'rank',
                                               'rider_name', 'rider_href', 'rider_pcs_name',
                                               'team_name', 'team_href', 'team_pcs_name', 'team_pcs_year',
                                               'kom_points'])
        
        return kom_frame
    
    def get_running_kom_points(self, pcs_stage: str):
        """
        Returns a dataframe of the total sum of KOM points accumulated by the end of the given stage

        Args:
            pcs_stage (str): the stage name according to PCS (usually in format: 'stage-#')

        Returns:
            pd.DataFrame: a dataframe organized by KOM points.
                            - columns:['rank', 
                                       'rider_name', 'rider_href', 'rider_pcs_name',
                                       'team_name', 'team_href', 'team_pcs_name', 'team_pcs_year',
                                       'kom_points']
        """
        
        # preset the acceptable strings for columns & tab of interest 
        columns_to_keep = ['Rnk', 'Rider', 'Team', 'Points']
        result_type = "KOM"

        # get the soup for results page
        url = mgt.race_url(self.pcs_name, self.year, suffix = pcs_stage)
        response = req.get(url)
        soup = BeautifulSoup(response.content, "html.parser")
        
        # all the possible result tabs
        restabs = soup.find("div", class_ = "page-content page-object default").find("ul", class_ = "restabs").find_all("li")
        
        # the index to use when accessing result table
        tab_index = tbl.result_cont_index(restabs, result_type)
        
        # the table and it's components
        table = soup.find("div", class_ = "page-content page-object default").find("div", class_ = "w68 left mb_w100").find_all("div", class_ = "result-cont")[tab_index]
        table_body = table.find('table', class_ = "results basic moblist10").find('tbody').find_all('tr')
        table_header = table.find('table', class_ = "results basic moblist10").find('thead').find_all('th')
        
        # get the column indices to extract for each row
        column_indices = tbl.column_indices(table_header, columns_to_keep)
        
        # get nested list of table results
        results = tbl.table_output(table_body, columns_to_keep, column_indices)
                
        # convert to dataframe for export
        running_kom = pd.DataFrame(data = results,
                                   columns = ['rank', 
                                              'rider_name', 'rider_href', 'rider_pcs_name',
                                              'team_name', 'team_href', 'team_pcs_name', 'team_pcs_year',
                                              'kom_points'])
        
        return running_kom