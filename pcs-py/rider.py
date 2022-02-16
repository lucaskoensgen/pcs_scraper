import os
import re

import requests as req
from bs4 import BeautifulSoup

import pandas as pd
import numpy as np



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

        self.url = get_rider_url(name)

        self.response = req.get(self.url)


        self.name = html_name(self.html_output)

        self.age = html_age(self.html_output)

        self.height = html_height(self.html_output)

        self.weight = html_weight(self.html_output)

        self.strava = html_strava(self.html_output)

        self.uci_rank = html_uci_rank(self.html_output)

        self.team = html_current_team(self.html_output)

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
