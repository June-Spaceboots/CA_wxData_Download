Get Canadian Weather Observations
=============

Introduction
------------

The `get_canadian_weather_obervation.py` is a python3 script used to download the [observation files from Environment and Climate change Canada](http://climate.weather.gc.ca/historical_data/search_historic_data_e.html) (ECCC) on your local computer.

This script is based on the information provided on the [ECCC Climate web site README](ftp://client_climate@ftp.tor.ec.gc.ca/Pub/Get_More_Data_Plus_de_donnees/Readme.txt). More information about the data format can be found on the [Digital Archive of Canadian Climatological Data Technical Documentation](ftp://ftp.tor.ec.gc.ca/Pub/Documentation_Technical/Technical_Documentation.pdf). While this software is distributed under the GLP Version 3 licence, the downloaded data is under to the [License Agreement for Use of Environment and Climate Change Canada Data](http://climate.weather.gc.ca/prods_servs/attachment1_e.html).

This software works under GNU/Linux, Windows and Mac OS X.
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
python get_canadian_weather_obervation.py [OPTIONS] [PERIOD] INPUT
```
<br />
where:   
* OPTIONS are described in the table below.
* PERIOD is the period of requested observations: [--hourly&#124;--daily&#124;--monthly]
* INPUT is one or many of these values:
 * [ECCC internal station ID](ftp://client_climate@ftp.tor.ec.gc.ca/Pub/Get_More_Data_Plus_de_donnees/Station%20Inventory%20EN.csv)
 * [two-letter province code](http://www12.statcan.gc.ca/census-recensement/2011/ref/dict/table-tableau/table-tableau-8-eng.cfm)
 * [three-letter IATA airport code](https://en.wikipedia.org/wiki/List_of_airports_by_IATA_code:_Y)
 * `all` for all available stations


| Options        | Description   |
| ------------- |-------------| 
| `-h`, `--help` | Show help message and exit      | 
| `-o` `--output-directory`&nbsp;DIRECTORY   |Directory where the files will be downloaded. Default value is where the script get_canadian_weather_observations.py is located.      | 
| `-S` `--station-list`&nbsp;PATH|Use this local version located at PATH for the station list instead of the online version on the EC Climate web site.
| `-l` `--lang` [en&#124;fr]| Language in which the data will be downloaded (en = English, fr = French). Default is English.
|`-t`  `--dry-run`     |   Execute the program, but do not download the files    | 
|`-F` `--format`&nbsp;[csv&#124;xml]| Download the files in CSV or XML format. Default value is CSV.
|`-d` `--date` YYYY[-MM[-DD]]| Get the observations for this specific date only.  `--end-date` and  `--start-date` are ignored if provided.
|`-e` `--start-date` YYYY[-MM[-DD]]| Get the observations after this date. Stops at `--end-date` if specified, otherwise download the observations until the last observation available.
|`-f` `--end-date` YYYY[-MM[-DD]]| Get the observations before this date. Stops at `--start-date` if specified, otherwise download the observations until the first observation available.
|`-H` `--hourly`| Get data values for observations taken on an hourly basis. (1 file per month)
|`-D` `--daily`| Get data values for observations taken once in a 24-hour period. (1 file per year)
|`-M` `--monthly`| Get averages for each month, derived from daily data values (1 file for the whole period)
|`-v` `--verbose`  | Explain what is being done |
|`-V` `--version`|Output version information and exit|

Usage
-----

Get the monthly averages for the [Bagotville Airport station](https://en.wikipedia.org/wiki/CFB_Bagotville) in XML French format (note date required, since the all the historical monthly averages are contained in one file)
```bash
 python get_canadian_weather_obervation.py --monthly -o /home/miguel/bagotville -f xml -l fr YBG
```
<br />

Get all the hourly values for all the Canadian stations for the year 2012 in csv English format
```bash
 python get_canadian_weather_obervation.py --hourly -o /home/miguel/download --date 2012 all
```
<br />

Get all the hourly and daily values for all the British-Columbian stations for the decade 1980-1989 in csv English format
```bash
 python get_canadian_weather_obervation.py --hourly --daily --after-date 1980-01 --before-date 1990-01 -o /home/miguel/download BC
```
<br />


