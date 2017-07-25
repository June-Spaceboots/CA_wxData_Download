man page
------------

get_canadian_weather_observations.py 


OPTIONS
------------


* `--station`: mandatory. 
 * List of stations ID (see the file here of a complete list of number related to stations ftp://client_climate@ftp.tor.ec.gc.ca/Pub/Get_More_Data_Plus_de_donnees/Station%20Inventory%20EN.csv).
 * Province/territory two letter code [AB|BC|...]: get the observations for all stations for this province or territory (voir [http://www12.statcan.gc.ca/census-recensement/2011/ref/dict/table-tableau/table-tableau-8-eng.cfm statcan pour la liste officiel des codes] 
 * "all": get all the observations of Canada
* `--output-directoy -o DIRECTORY`: output where the files will be downloaded. Default value is where the script get_canadian_weather_observations.py is located.
* `--format [CSV|XML]`: Download the files in CSV or XML format. Default value is CSV.

* `--date YYYY[-MM[-DD]]]`: get the observations for this specific date only.  `--before-date` and  `--after-date` are ignored if provided.
* `--after-date YYYY[-MM[-DD]]]`: get the observations after this date. Stops at `--before-date` if specified, otherwise download the observations until the last observation available.
* `--before-date "YYYY[-MM[-DD]]]`: get the observations before this date. Stops at `--after-date` if specified, otherwise download the observations until the first observation available.

* `--hourly`:  data values for observations taken on an hourly basis. (1 file per month)
* `--daily`: get data values for observations taken once in a 24-hour period. (1 file per year)
* `--monthly`: get averages for each month, derived from daily data values (1 file for the whole period)
