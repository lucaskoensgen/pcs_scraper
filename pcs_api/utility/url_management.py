
### Functions that convert name strings for Rider, Team, Race inputs into url to use when requesting from pcs

def rider_url(name:str):
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

def team_url(name: str, year: int):
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

def race_url(name: str, year: int, **kwargs):
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