# pcs_scraper
**v0.1**
A python package to query, organize and prepare pandas dataframes from procyclingstats.com data to facilitate further analysis

## Project Description

This project was undertaken as a side project while working as a data/race analyst with professional cycling teams. While commonplace for many other major sports, I couldn't find any available packages that provided access to professional cycling datasets. There were, however, already fantastic websites devoted to cataloguing this data and presenting it for free. The most user-friendly website I found was procyclingstats.com (PCS) but they didn't have a publicly available api, so I decided to make this package to interact with their posted data programmatically. 

_pcs_scraper_ lets users interact with PCS through three fundamental and distinct classes:
1. Riders
2. Teams
3. Races

In the next versions of this project I would like to link the statistical data from PCS with rider strata data.

## Installation

###### Via pip:
Coming soon

###### **Via conda**:
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
Coming soon
###### Practical Examples
Coming soon

## Documentation
Coming soon


