Get Canadian Weather Observations
=============

Introduction
------------

The `get_canadian_weather_obervation.py` is a python script used to download the [observation files from Environment and Climate change Canada](http://climate.weather.gc.ca/historical_data/search_historic_data_e.html) (ECCC) on your local computer.

It works under GNU/Linux, Windows and Mac OS X.
___

Requirements
------------

* [Python3] (https://www.python.org/downloads/)

___

Download 
--------
The more recent package can be downloaded here:  
http://????.ca/climat/get_canadian_weather_obervation.py

git version can be accessed here:  
 git clone https://framagit.org/MiguelTremblay/get_canadian_weather_observations.git


Manual
--------
 
In a general way, this application should be called in command line like this:  
```bash
python get_canadian_weather_obervation.py [OPTIONS] INPUT
```
<br />
where:   
* INPUT: List of [stations ID](ftp://client_climate@ftp.tor.ec.gc.ca/Pub/Get_More_Data_Plus_de_donnees/Station%20Inventory%20EN.csv) or [two-letter province](http://www12.statcan.gc.ca/census-recensement/2011/ref/dict/table-tableau/table-tableau-8-eng.cfm) code or "all" for all available stations
* OPTIONS are described in the table below.


OPTIONS
------------



* `--output-directoy -o DIRECTORY`: output where the files will be downloaded. Default value is where the script get_canadian_weather_observations.py is located.
* `--format [CSV|XML]`: Download the files in CSV or XML format. Default value is CSV.

* `--date YYYY[-MM[-DD]]]`: get the observations for this specific date only.  `--before-date` and  `--after-date` are ignored if provided.
* `--after-date YYYY[-MM[-DD]]]`: get the observations after this date. Stops at `--before-date` if specified, otherwise download the observations until the last observation available.
* `--before-date "YYYY[-MM[-DD]]]`: get the observations before this date. Stops at `--after-date` if specified, otherwise download the observations until the first observation available.

* `--hourly`:  data values for observations taken on an hourly basis. (1 file per month)
* `--daily`: get data values for observations taken once in a 24-hour period. (1 file per year)
* `--monthly`: get averages for each month, derived from daily data values (1 file for the whole period)

Usage
-----

Copy the image directly in the folder where it is located:  
```bash
 python exif_rename_files.py /home/miguel/photo/DSC0000.JPG
```
<br />