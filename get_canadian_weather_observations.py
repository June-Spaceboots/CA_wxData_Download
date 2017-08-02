#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Copyright  2017  Miguel Tremblay

# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program; if not see  <http://www.gnu.org/licenses/>.
############################################################################

"""
Name:        get_canadian_weather_observations.py
Description: Download the observation files from Environment and Climate change Canada (ECCC) on your local computer.

Notes: 

Author: Miguel Tremblay (http://ptaff.ca/miguel/)
Date: July 25th 2017
"""

import sys
import os
import datetime
import urllib
import requests
import io
import csv

VERSION = "0.1"
# Verbose level:
## 1 Normal mode
## 2 Full debug
NORMAL= 1
VERBOSE= 2

nGlobalVerbosity = 1

# Dictionnary used for variables specific to the language of the request
dLang = {}

# URLs
ECCC_WEBSITE_URL = "http://climate.weather.gc.ca/"
ECCC_FTP_URL = "ftp://client_climate@ftp.tor.ec.gc.ca/Pub/Get_More_Data_Plus_de_donnees/"
STATION_LIST_EN = ECCC_FTP_URL + "Station%20Inventory%20EN.csv"
#FR_STATION_LIST=ECCC_FTP_URL + "R%E9pertoire%20des%20stations%20FR.csv"
# Forced to use bitly because of encoding problem with 'Répertoire' "
STATION_LIST_FR = "http://bit.ly/2uXbN9u" 

# CSV file station list
COLUMN_TITLE_EN=["Name","Province","Climate ID","Station ID","WMO ID","TC ID",\
                 "Latitude (Decimal Degrees)","Longitude (Decimal Degrees)",\
                 "Latitude","Longitude","Elevation (m)","First Year","Last Year",\
                 "HLY First Year","HLY Last Year","DLY First Year","DLY Last Year",\
                 "MLY First Year","MLY Last Year"]

# Dictionnaries to contain the station ID of the list
dStationList = {}
dStationAirport = {}
dProvTerrList = { "AB" : [], \
                  "BC" : [], \
                  "MB" : [], \
                  "NB" : [], \
                  "NL" : [], \
                  "NS" : [], \
                  "NT" : [], \
                  "NU" : [], \
                  "ON" : [], \
                  "PE" : [], \
                  "QC" : [], \
                  "SK" : [], \
                  "YT" : []  }

# Province and territory string and code management
lProvTerrCode = ["AB","BC","MB","NB","NL","NS","NT","NU", \
                 "ON","PE","QC","SK","YT" ]
dProvFR = { "ALBERTA" : "AB", \
            "COLOMBIE-BRITANNIQUE" : "BC" , \
            "MANITOBA" : "MB", \
            "NOUVEAU-BRUNSWICK" : "NB", \
            "TERRE-NEUVE" : "NL", \
            "NOUVELLE-ECOSSE" : "NS", \
            "TERRITOIRES DU NORD-OUEST" : "NT", \
            "NUNAVUT" : "NU", \
            "ONTARIO" : "ON", \
            "ILE DU PRINCE-EDOUARD" : "PE", \
            "QUEBEC" : "QC", \
            "SASKATCHEWAN" : "SK", \
            "YUKON" : "YT"  }
dProvEN = { "ALBERTA" : "AB" , \
            "BRITISH COLUMBIA" : "BC", \
            "MANITOBA" : "MB", \
            "NEW BRUNSWICK" : "NB", \
            "NEWFOUNDLAND" : "NL", \
            "NOVA SCOTIA" : "NS", \
            "NORTHWEST TERRITORIES" : "NT", \
            "NUNAVUT" : "NU", \
            "ONTARIO" : "ON", \
            "PRINCE EDWARD ISLAND" : "PE", \
            "QUEBEC" : "QC", \
            "SASKATCHEWAN" : "SK", \
            "YUKON TERRITORY" : "YT"  }
dProvCode = None # Will be set to EN or FR
                  

def my_print(sMessage, nMessageVerbosity=NORMAL):
   """
   Use this method to write the message in the standart output 
   """

   if nMessageVerbosity == NORMAL:
      print (sMessage)
   elif nMessageVerbosity == VERBOSE and nGlobalVerbosity == VERBOSE:
      print (sMessage)

def set_language(sLang):
   """
   Set the different values specific to the language (URL, station list header, etc.)
   """
   global dProvCode
   
   if sLang == "en":
      dLang['station_list_URL'] = STATION_LIST_EN      
      dProvCode = dProvEN
   elif sLang == "fr":
      dLang['station_list_URL'] = STATION_LIST_FR
      dProvCode = dProvFR

def check_input_dates(lDates):
   """
   Verify if the provided dates are in a valid format (YYYY or YYYY-MM).

   INPUT
   lDates: list of string of input dates: [tOptions.RequestedDate, tOptions.StartDate, tOptions.EndDate]

   OUTPUT
   lValidatedDates : list of strptime for input dates
   """

   # Variables initialisation
   [sRequestedDate, sStartDate, sEndDate] = lDates
   timeRequestedDate = None
   timeStartDate = None
   timeEndDate = None

   # Specific date
   if sRequestedDate is not None:
      my_print("Checking --date format " + sRequestedDate, nMessageVerbosity=VERBOSE)
      timeRequestedDate = check_date_format(sRequestedDate)
      if sStartDate != None:
         my_print("WARNING: --date is provided. Ignoring the value of --start-date: " + \
                  sStartDate, nMessageVerbosity=NORMAL)
         timeStartDate = None
      if sEndDate != None:
         my_print("WARNING: --date is provided. Ignoring the value of --end-date: " + \
                  sEndDate, nMessageVerbosity=NORMAL)
         timeEndDate = None
      return [timeRequestedDate, timeStartDate, timeEndDate]

   # Start/end date
   if sStartDate != None:
      my_print("Checking --start-date format: " + sStartDate, nMessageVerbosity=VERBOSE)
      timeStartDate = check_date_format(sStartDate)
   if sEndDate != None:
      my_print("Checking --end-date format: " + sEndDate, nMessageVerbosity=VERBOSE)
      timeEndDate = check_date_format(sEndDate)
   if sStartDate != None: and sEndDate != None: 
      if timeStartDate > timeEndDate:  # Check if start date is before end date
         my_print("ERROR: Start date is after end date:\n " + sStartDate + " after " + sEndDate,
                  nMessageVerbosity=NORMAL)
         exit(8)
      # Start date format: YYYY-MM / End date format: YYYY
      elif len(sStartDate) > len(sEndDate):
         #  datetime.datetime.strftime(t1, "%Y")

   return [time_RequestedDate, time_StartDate, time_EndDate]

def check_date_format(sDate):
   """
   Check if the provided string is a valid date of the format 'YYYY' or 'YYYY-MM'

   If one value is not valid, the program displays an error message and exits.
   """

   if len(sDate) == 4: # YYYY format
      try:
         timeDate = datetime.datetime.strptime(sDate, '%Y')
         my_print("Requested date is: " + sDate,  nMessageVerbosity=VERBOSE)
      except ValueError:
         my_print ("Requested date must be of format 'YYYY' or 'YYYY-MM'.", \
                   nMessageVerbosity=NORMAL)
         my_print("Provided value: '" + sDate + "'", \
                  nMessageVerbosity=NORMAL)
         exit(5)
   elif len(sDate) == 7: # YYYY-MM format
      try:
         timeDate = datetime.datetime.strptime(sDate, '%Y-%m')
         my_print("Requested date is: " + sDate,  nMessageVerbosity=VERBOSE)
      except ValueError:
         my_print ("Requested date must be of format 'YYYY' or 'YYYY-MM'.", \
                   nMessageVerbosity=NORMAL)
         my_print("Provided value: '" + sDate + "'",  nMessageVerbosity=NORMAL)
         exit(6)
   else: # Date format not allowed
      my_print ("Requested date must be of format 'YYYY' or 'YYYY-MM'.", \
                nMessageVerbosity=NORMAL)
      my_print("Provided value: '" + sDate + "'",  nMessageVerbosity=NORMAL)
      exit(7)

   return timeDate
   

def check_eccc_climate_connexion():
   """
   Check if we can connect the ECCC Climate web site. If not, there is point to continue.
   """

   my_print("Checking if ECCC Climate web site is available...", nMessageVerbosity=VERBOSE)

   try:
      urllib.request.urlopen(ECCC_WEBSITE_URL)
   except urllib.error.URLError :
      my_print ("ERROR: Climate web site not available", nMessageVerbosity=NORMAL)
      my_print ("Check your internet connexion or try to reach\n '" +\
                ECCC_WEBSITE_URL + "'\n in a web browser.", nMessageVerbosity=NORMAL)
      my_print ("Exiting.", nMessageVerbosity=NORMAL)
      sys.exit(1)

   my_print("ECCC Climate web site reached! Continuing. ", nMessageVerbosity=VERBOSE)

   
def load_station_list(sPath):
   """
   Download the latest file from the ECCC climate web site.
   """
   global dStationList, dStationAirport, dProvTerrList

   # Check if a local path is given
   if sPath is not None:
      my_print("Loading local file for station list at: " + sPath, nMessageVerbosity=VERBOSE)
      # Open file
      if os.path.exists(sPath) == False:
         my_print("ERROR: Local station path does not exist: " +sPath,\
                  nMessageVerbosity=NORMAL)
         my_print("Please fix this error or try the online version of station file.")
         my_print("Exiting")
         exit(2)
      else:
         file_list = open(sPath, 'r')
         station_list = csv.DictReader(file_list, fieldnames=COLUMN_TITLE_EN)
   else:
      try:
         my_print("Loading online station list at: " + \
                  dLang['station_list_URL'], nMessageVerbosity=VERBOSE)
         # Recipe from http://bit.ly/2hc9XMB
         webpage = urllib.request.urlopen(dLang['station_list_URL'])
         station_list = csv.DictReader(io.TextIOWrapper(webpage), \
                                       fieldnames=COLUMN_TITLE_EN)

      except urllib.error.URLError :
         my_print ("WARNING: Online CSV list of stations not available", \
                   nMessageVerbosity=NORMAL)
         my_print ("Cannot reach:\n '" +\
                    dLang['station_list_URL']+ "'\n", nMessageVerbosity=NORMAL)
         my_print ("Using the local version instead. Station list may be not up to date.",\
                   nMessageVerbosity=NORMAL)


   # Fill the dictionnaries with the station list
   # Skip the first 4 lines
   for i in range(4):
      next(station_list)
   for row in station_list:
      # EC internal station code
      nStationCode = row["Station ID"]
      dStationList[nStationCode] = row

      # If the station correspond to an airport
      sAirport = row["TC ID"]
      if len(sAirport) == 3:
         dStationAirport[sAirport] = nStationCode

      # Order by province/territory
      sProvTerr = row["Province"]
      dProvTerrList[dProvCode[sProvTerr]].append(nStationCode)

      
def fetch_requested_stations(lInput):
   """
   Fetch all the lines in the dictionnary containing all the stations and store them 
   in another dictionnary.

   Arguments:
    lInput: list of all the srings given in the input.
    return lStationRequested: list of all the station ID corresponding to the input.
   """
   lStationRequested = []

   # If "all", or any lower/uppercase variant, load everything and exit
   if "all" in lInput:
      my_print("All stations requested", nMessageVerbosity=VERBOSE)
      lStationRequested = dStationList.keys()
      return lStationRequested
      
   # If not all stations requested, build the station list
   for sElement in lInput:
      if len(sElement) == 3: # Airport code         
         if sElement in dStationAirport.keys():
            my_print("Airport code added in list: " +sElement, nMessageVerbosity=VERBOSE)
            lStationRequested.append(dStationAirport[sElement])
         else:
            my_print("Warning: requested airport code not in station list: '" + sElement +\
                     "'\nIgnoring", nMessageVerbosity=NORMAL)
      elif len(sElement) == 2:
         if sElement in lProvTerrCode: # Province or territory
            my_print("Station in province or territory added: " +sElement, \
                     nMessageVerbosity=VERBOSE)
            lStationRequested = lStationRequested + dProvTerrList[sElement]
         else:
            my_print("Warning: requested province or territory not in list: '" + sElement +\
                     "'\nOptions are:", nMessageVerbosity=NORMAL)
            my_print(lProvTerrCode, nMessageVerbosity=NORMAL)
      elif sElement.isdigit(): # Station ID
         my_print("Station code added: " +sElement, \
                  nMessageVerbosity=VERBOSE)
         lStationRequested.append(sElement)
      else: # Argument did not fit any criteria
            my_print("Warning: requested argument not valid: '" + sElement +\
                     "'\nSkipping.", nMessageVerbosity=NORMAL)
         
   return lStationRequested

def set_interval_date(lStationRequested, dObsPeriod, lDateRequested):
   """
   Check if the interval requested on command line are available for each station requested.

   INPUT
   lStationRequested: List of Station ID of requested stations.
   dObsPeriod: Dictionnary linking the hourly/daily/monthly obs period request to a boolean.
   lDateRequested: List of requested dates. In order:
     1- Specific date
     2- Start date
     3- End date
   """

   for sStation in lStationRequested:
      dStation = dStationList[sStation]
      if dObsPeriod["monthly"]: # Check for monthly values
         sFirstYear = dStation["HLY First Year"]
         sLastYear = dStation["HLY Last Year"]
         # ICI
         
#      ,"HLY Last Year","DLY First Year","DLY Last Year",\
#                "MLY First Year","MLY Last Year"

def get_canadian_weather_observations(tOptions):
   """
   Download the observation files from Environment and Climate change Canada (ECCC)
   on your local computer.
   """

   # If dates are provided, check if the string format is fine.
   lRequestedDate = check_input_dates\
                    ([tOptions.RequestedDate, tOptions.StartDate, tOptions.EndDate])
         
   
   # Check if we can contact ECCC web site
   check_eccc_climate_connexion()

   # Set language
   set_language(tOptions.Language)

   # Load the station list
   load_station_list(tOptions.LocalStationPath)

   # Fetch the requested stations
   lStationList = fetch_requested_stations(tOptions.Input)
   if len(lStationList) == 0: # If nothing fits.
      my_print ("No station found corresponding to arguments: ", \
                nMessageVerbosity=NORMAL)
      my_print (tOptions.Input, nMessageVerbosity=NORMAL)
      return

   # Check if the reqested dates are available for each station
   dObsPeriod = { "hourly"  : tOptions.Hourly,\
                  "daily"   : tOptions.Daily, \
                  "monthly" :tOptions.Monthly}
   set_interval_date(lStationList, dObsPeriod, lRequestedDate)
   

############################################################
# get_canadian_weather_observations in Command line
#
#

import argparse

def get_command_line():
   """
   Parse the command line and perform all the checks.
   """

   parser = argparse.ArgumentParser(prog='PROG', prefix_chars='-',\
                                    description="download the observation files from Environment and Climate change Canada (ECCC) on your local computer.")
   parser.add_argument("Input", metavar="Input", nargs="*", \
                     help="Station(s) for which the observations should be downloaded",\
                       action="store", type=str, default=None)
   parser.add_argument("--output-directory", "-o", dest="OutputDirectory", \
                     help="Directory where the files will be written",\
                     action="store", type=str, default=None)
   parser.add_argument("--station-file", "-S", dest="LocalStationPath", \
                     help="Use this local version located at PATH for the station list instead of the online version on the EC Climate web site.",\
                     action="store", type=str, default=None)   
   parser.add_argument("--dry-run", "-t", dest="DryRun", \
                     help="Execute the program, but do not download any file",\
                       action="store_true", default=False)
   parser.add_argument("--lang", "-l", dest="Language", metavar=("[en|fr]"), 
                       choices=["fr","en"], \
                       help="Language in which the data will be downloaded (en = English, fr = French). Default is English.",\
                       action="store", type=str, default="en")   
   parser.add_argument("--format", "-F", dest="Format", metavar=("[xml|csv]"), \
                       help="Download the files in 'csv' or 'xml' format. Default value is 'csv'.",\
                       action="store", type=str, default="xml")
   # Date stuff
   parser.add_argument("--date", "-d", dest="RequestedDate", metavar=("YYYY[-MM[-DD]]") ,\
                       help="Get the observations for this specific date only.  --start-date and  --end-date are ignored if provided. Format is YYYY[-MM[-DD]]",\
                       action="store", type=str, default=None)
   parser.add_argument("--start-date", "-e", dest="StartDate", metavar=("YYYY[-MM[-DD]]"), \
                       help="Get the observations after this date. Stops at --end-date if specified, otherwise download the observations until the last observation available. Format is YYYY[-MM[-DD]]",\
                       action="store", type=str, default=None)
   parser.add_argument("--end-date", "-f", dest="EndDate",metavar=("YYYY[-MM[-DD]]"), \
                       help="Get the observations before this date. Stops at --start-date if specified, otherwise download the observations until the first observation available. Format is YYYY[-MM[-DD]]",\
                       action="store", type=str, default=None)
   # hourly, daily, monthly
   parser.add_argument("--hourly", "-H", dest="Hourly", \
                     help="Get data values for observations taken on an hourly basis. (1 file per month)",\
                     action="store_true", default=False)
   parser.add_argument("--daily", "-D", dest="Daily", \
                     help="Get data values for observations taken once in a 24-hour period. (1 file per year)",\
                     action="store_true", default=False)
   parser.add_argument("--monthly", "-M", dest="Monthly", \
                     help="Get averages for each month, derived from daily data values (1 file for the whole period)",\
                     action="store_true", default=False)
   

   parser.add_argument("--verbose", "-v", dest="Verbosity", \
                     help="Explain what is being done", action="store_true", default=False)
   parser.add_argument("--version", "-V", dest="bVersion", \
                       help="Output version information and exit",\
                       action="store_true", default=False)               

   # Parse the args
   options = parser.parse_args()
   
   if options.bVersion:
      print ("get_canadian_weather_observations.py version: " + VERSION)
      print ("Copyright (C) 2017 Free Software Foundation, Inc.")
      print ("License GPLv3+: GNU GPL version 3 or later <http://gnu.org/licenses/gpl.html>.")
      print ("This is free software: you are free to change and redistribute it.")
      print ("There is NO WARRANTY, to the extent permitted by law.\n")
      print ("Written by Miguel Tremblay, http://ptaff.ca/miguel/")
      exit(0)
   
   # Verify it the output is a directory
   if options.OutputDirectory is not None and not os.path.isdir(options.OutputDirectory):
      print ("Error: Directory '%s' provided in '--output-directory' does not exist or is not a directory. Please provide a valid output directory. Exiting." % (options.OutputDirectory))
      exit (3)

   # Verify if at least one period of observation is requested.
   if options.Hourly is False and \
      options.Daily is False and \
      options.Monthly is False:
      print ("Error: no observation period indicated.")
      print ("Please choose for one or more of these options:")
      print ("--hourly --daily --monthly")
      exit(4)
      
      
   # Set the global verbosity
   global nGlobalVerbosity
   if options.Verbosity:
      nGlobalVerbosity = VERBOSE
   else:
      nGlobalVerbosity = NORMAL
      
   my_print("Verbosity level is set to: " + str(nGlobalVerbosity), nMessageVerbosity=VERBOSE)
   my_print("Arguments in command line are:\n " + str(sys.argv), nMessageVerbosity=VERBOSE)
   

            
   return options


if __name__ == "__main__":

   tOptions = get_command_line()
   get_canadian_weather_observations(tOptions)
