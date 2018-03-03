[Français](README_fr.md)

Get Canadian Weather Observations
=============

Introduction
------------

`get_canadian_weather_obervation.py` is a python3 software used to download the [observation files from Environment and Climate change Canada](http://climate.weather.gc.ca/historical_data/search_historic_data_e.html) (ECCC) to a computer. This software is originally a personnel project of Miguel Tremblay and does not belong to ECCC.

This script is based on the information provided on the [ECCC Climate web site README](ftp://client_climate@ftp.tor.ec.gc.ca/Pub/Get_More_Data_Plus_de_donnees/Readme.txt). More information about the data format can be found on the [Digital Archive of Canadian Climatological Data Technical Documentation](ftp://client_climate@ftp.tor.ec.gc.ca/Pub/Documentation_Technical/Technical_Documentation.pdf). While this software is distributed under the GPL Version 3 license, the downloaded data is under the [License Agreement for Use of Environment and Climate Change Canada Data](http://climate.weather.gc.ca/prods_servs/attachment1_e.html).

This software works under GNU/Linux, Windows and Mac OS X.
___

Requirements
------------

* [python3](https://www.python.org/downloads/)
* [python3-dateutil](https://pypi.python.org/pypi/python-dateutil)
* [python3-progress](https://pypi.python.org/pypi/progress)

___

Download
--------
The latest version can be downloaded here:<br>
https://framagit.org/MiguelTremblay/get_canadian_weather_observations   

The git version can be accessed here:<br>
 ```git clone https://framagit.org/MiguelTremblay/get_canadian_weather_observations.git```


Manual
--------

In a general way, this software should be called in command line like this:
```bash
python get_canadian_weather_obervation.py [OPTIONS] [PERIOD] INPUT
```
<br />
where:
* OPTIONS are described in the table below.
* PERIOD is the period of requested observations. This option is valid for these types of observations [--hourly&#124;--daily&#124;--monthly]
* INPUT is one or many of these values:
 * [ECCC internal station ID](ftp://client_climate@ftp.tor.ec.gc.ca/Pub/Get_More_Data_Plus_de_donnees/Station%20Inventory%20EN.csv)
 * [two-letter province code](http://www12.statcan.gc.ca/census-recensement/2011/ref/dict/table-tableau/table-tableau-8-eng.cfm)
 * [three-letter IATA airport code](https://en.wikipedia.org/wiki/List_of_airports_by_IATA_code:_Y) (when there is more than one station corresponding to an airport code, all the stations are appended to the list)
 * `all` for all available stations


| Options                                  | Description |
| -------                                  | ------------|
| `-h`, `--help`                           | Show help message and exit.|
| `-o` `--output-directory`&nbsp;DIRECTORY | Directory where the files will be downloaded, in their corresponding sub-directory when requested (see `--no-tree` option). Default value is where the script get_canadian_weather_observations.py is located. Sub-directories take the form of STATION-ID/OBS-TYPE, where "STATION-ID" is the ECCC station ID number, and "OBS-TYP" is one of the four observation types: "hourly", "daily", "monthly" or "almanac".|
| `-n` `--no-tree`                         | Do not create directories, download all the files in the output directory.|
| `-N` `--no-clobber`                      | Do not overwrite an existing file. File is not downloaded.|
| `-S` `--station-list`&nbsp;PATH          | Use the file for the station list located at PATH on your local computer instead of downloading the online version on the ECCC Climate web site. You can download the station list file (in [English](ftp://client_climate@ftp.tor.ec.gc.ca/Pub/Get_More_Data_Plus_de_donnees/Station%20Inventory%20EN.csv) or in [French](ftp://client_climate@ftp.tor.ec.gc.ca/Pub/Get_More_Data_Plus_de_donnees/R%E9pertoire%20des%20stations%20FR.csv)). Using local file can save a lot of time. If you use this file, you have to set the corresponding language by using the `--lang` option.|
| `-l` `--lang` [en&#124;fr]               | Language in which the data will be downloaded (en = English, fr = French). Default is English.|
|`-t`  `--dry-run`                         | Execute the program, print the URL but do not download the files.|
|`-F` `--format`&nbsp;[csv&#124;xml]       | Download the files in CSV or XML format. Default value is CSV.|
|`-d` `--date` YYYY[-MM]                   | Get the observations for this specific date only.  `--end-date` and  `--start-date` are ignored if provided. If no date is provided, download the date for the full period.|
|`-e` `--start-date` YYYY[-MM]             | Get
the observations after this date. Stops at `--end-date` if specified, otherwise download the observations until the last observation available.|
|`-f` `--end-date` YYYY[-MM]               | Get the observations before this date. Stops at `--start-date` if specified, otherwise download the observations until the first observation available.|
|`-H` `--hourly`                           | Get data values for observations taken on an hourly basis (1 file per month).|
|`-D` `--daily`                            | Get data values for observations taken once in a 24-hour period (1 file per year).|
|`-M` `--monthly`                          | Get averages for each month, derived from daily data values (1 file for the whole period).|
|`-C` `--climate`                          | Get the Almanac Averages and Extremes for this station (1 file for the whole period).|
|`-I` `--info`                             | Get and display the information (lat, lon, code, start/end date, etc.) for the selected station(s) and exit.|
|`-v` `--verbose`                          | Explain what is being done.|
|`-V` `--version`                          | Output version information and exit.|

Usage
-----

Get the monthly averages for the [Bagotville Airport station](https://en.wikipedia.org/wiki/CFB_Bagotville) in XML French format (no date required, as all the historical monthly averages are contained in one file):
```bash
 python get_canadian_weather_obervation.py --monthly -o /home/miguel/bagotville -f xml -l fr YBG
```
<br />

Get all the hourly observations for all the Canadian stations for the year 2012 in CSV English format:
```bash
 python get_canadian_weather_obervation.py --hourly -o /home/miguel/download --date 2012 all
```
<br />

Get all the hourly and daily observations for all the British-Columbian stations for the decade 1980-1989 in CSV English format:
```bash
 python get_canadian_weather_obervation.py --hourly --daily --start-date 1980-01 --end-date 1990-01 -o /home/miguel/download BC
```
<br />

Display the information for the Bagotville station:
```bash
 python get_canadian_weather_observations.py --info YBG
----
Station ID: 5889
Name:BAGOTVILLE A
DLY Last Year:2017
HLY Last Year:2017
MLY First Year:1942
Elevation (m):159.1
TC ID:YBG
Station ID:5889
First Year:1942
MLY Last Year:2014
Longitude:-710000000
Latitude:482000000
Climate ID:7060400
Province:QUEBEC
Longitude (Decimal Degrees):-71
Last Year:2017
HLY First Year:1953
DLY First Year:1942
Latitude (Decimal Degrees):48.33
WMO ID:71727
```

