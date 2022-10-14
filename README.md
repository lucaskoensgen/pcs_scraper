# pcs_scraper
**v0.1.0**
A python package to query, organize and prepare pandas dataframes from procyclingstats.com data to facilitate further analysis

## Project Description

This project was undertaken as a side project while working as a data/race analyst with professional cycling teams. While commonplace for many other major sports, I couldn't find any available packages that provided access to professional cycling datasets. There were, however, already fantastic websites devoted to cataloguing this data and presenting it for free. The most user-friendly website I found was procyclingstats.com (PCS) but they didn't have a publicly available api, so I decided to make this package to interact with their posted data programmatically. 

_pcs_scraper_ lets users interact with PCS through three fundamental and distinct classes:
1. Riders
2. Teams
3. Races

In the next versions of this project I would like to link the statistical data from PCS with rider Strava data.

## Installation

###### Via pip:
pip install pcs-scraper

###### Via conda:
Coming soon

###### Via source code:
Fork/clone this repo and create a conda environment to develop in using:
```
# create environment using existing environment file
conda env create -f environment.yml

# add pcs_scraper to path for environment
cd .../anaconda3/envs/pcs_env/lib/python3.9/site-packages
nano packages.pth 
# then in nano type **full path** to main pcs_scraper directory (ie. .../Users/name/Desktop/pcs_scraper)
# press control+O to save file, press control+X to exit nano
```

## Usage
###### Basic
```
# for specific rider

# import 
import pcs_scraper as pcs

# request rider object for tadej pogacar
pogacar = pcs.Rider(name = 'tadej-pogacar')

# get pogacar's entire race history 
pogacar_race_hx = pogacar.get_race_history()
```
```
# for specific race

# import
import pcs_scraper as pcs

# request race object for tour de france
tdf = pcs.Race(name = 'tour-de-france', year = 2021)

	# if unsure about spelling of race name according to PCS you can search using:
	# race_options = pcs.race_options_by_year(2021)
	# can refine output using race circuit or classification when requesting
	# race_options = pcs.race_options_by_year(2021, classification = '2.UWT', circuit = 'UCI World Tour')

# request the GC results
tdf_final_gc = tdf.get_results()
```
```
# for specific team

# import
import pcs_scraper as pcs

# request team object for Ineos 
ineos = pcs.Team(name = 'ineos-grenadiers', year = 2021)

	# if unsure about spelling of team name according to PCS you can search using:
	# team_options_2021 = pcs.teams_by_year(year = 2021, gender = 'M')

# get the riders from the team
ineos_2021_riders = ineos.get_riders()
```

###### Practical Examples
Coming soon

## Documentation
Coming soon


