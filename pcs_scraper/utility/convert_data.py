import datetime

def printed_rider_to_first_last(printed_name: str):
    """
    Changes a name written as "LAST First" on PCS website to "First Last" format

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
            first_name = first_name + [name]
    
    # make the organized name back into single string again
    rider_name_list = first_name + last_name
    new_name = " ".join(rider_name_list)
    
    return new_name

def printed_time_to_seconds(printed_time: str):
    """
    Converts the printed str time on pcs to a value of seconds

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

def printed_date_to_standard(printed_date):
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

# def team_info_from_soup(soup_text):
    
    
    
#     return team_info

# def rider_info_from_soup(soup_text):
    
#     return rider_info

# def race_info_from_soup(soup_text):
    
#     return race_info