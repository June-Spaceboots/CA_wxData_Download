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
Description: Download the observation files from Environment and 
 Climate change Canada (ECCC) on your local computer.

Notes: 

Author: Miguel Tremblay (http://ptaff.ca/miguel/)
Date: July 25th 2017
"""

import sys
import os
import glob
import datetime
import urllib
import io
import csv
import urllib.request
import cgi
from multiprocessing import Pool


# From dateutil package: https://pypi.python.org/pypi/python-dateutil
from dateutil import rrule
# From progress https://pypi.python.org/pypi/progress
from progress.bar import Bar

VERSION = "0.3"
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
STATION_LIST_FR = ECCC_FTP_URL + "Répertoire%20des%20stations%20FR.csv"

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
      my_print("Checking --date format '" + sRequestedDate +"'", nMessageVerbosity=VERBOSE)
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

   # Start/end date specified
   if sStartDate != None:
      my_print("Checking --start-date format: " + sStartDate, nMessageVerbosity=VERBOSE)
      timeStartDate = check_date_format(sStartDate)
   if sEndDate != None:
      my_print("Checking --end-date format: " + sEndDate, nMessageVerbosity=VERBOSE)
      timeEndDate = check_date_format(sEndDate)
   if sStartDate != None and sEndDate != None: 
      if timeStartDate > timeEndDate:  # Check if start date is before end date
         my_print("ERROR: Start date is after end date:\n " + sStartDate + " after " + sEndDate,
                  nMessageVerbosity=NORMAL)
         exit(8)
      # Start date format: YYYY-MM / End date format: YYYY
      elif len(sStartDate) > len(sEndDate):
         my_print("Start date is in format 'YYYY-MM' while End date is 'YYYY': '"+ \
                  sStartDate + "' vs '" + sEndDate + "'", nMessageVerbosity=NORMAL)
         my_print("Changing End date to end in December ---> " + \
                  sEndDate + "-12 ", nMessageVerbosity=NORMAL)
         sEndDate = sEndDate + "-12"
         timeEndDate = check_date_format(sEndDate)
      # End date format: YYYY-MM / Start date format: YYYY
      elif len(sEndDate) > len(sStartDate):
         my_print("End date is in format 'YYYY-MM' while Start date is 'YYYY': '"+ \
                  sEndDate + "' vs '" + sStartDate + "'", nMessageVerbosity=NORMAL)
         my_print("Changing Start date to start in January ---> " + \
                  sStartDate + "-01 ", nMessageVerbosity=NORMAL)
         sStartDate = sStartDate + "-01"
         timeStartDate = check_date_format(sStartDate)

   return [timeRequestedDate, timeStartDate, timeEndDate]


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
         my_print("This may take a while...", nMessageVerbosity=VERBOSE)         
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
      if len(sElement) == 3 and sElement.isalpha(): # Airport code         
         if sElement in dStationAirport.keys():
            my_print("Airport code added in list: " +sElement + " (" + \
                     dStationAirport[sElement] + ")", nMessageVerbosity=VERBOSE)
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
                     "' Skipping.", nMessageVerbosity=NORMAL)
         
   return lStationRequested

def check_specific_date(sStation, timeDate, timeFirstYear, timeLastYear, sPeriod=None):
   """
   When a specific date is given, check if it falls between the intervals. 
   Return True if it is in the interval, False otherwise.
   """

   if timeDate < timeFirstYear: # Requested before the station starts recording
      my_print("Station " +sStation + ":\n\t" + sPeriod +" values: requested year" + \
               " is before the station started to record values", nMessageVerbosity=NORMAL)
      my_print("\tRequested year: " + timeDate.strftime('%Y'), \
               nMessageVerbosity=NORMAL)
      my_print("\tStarting year for this station: " + timeFirstYear.strftime('%Y') + ". Skipping",\
               nMessageVerbosity=NORMAL)
      return False
   elif timeDate > timeLastYear: # Requested after the station ends recording
      my_print("Station " +sStation + ":\n\t" + sPeriod +" values: requested year" + \
               " is after the station started to record values", nMessageVerbosity=NORMAL)
      my_print("\tRequested year: " + timeDate.strftime('%Y'), \
               nMessageVerbosity=NORMAL)
      my_print("\tLast year for this station: " + timeLastYear.strftime('%Y') + ". Skipping",\
               nMessageVerbosity=NORMAL)
      return False
   else:
      my_print("Station " + sStation + ":\n\trequested date for " +sPeriod + " data is valid. ", \
               nMessageVerbosity=VERBOSE)
      return True

   
def check_start_date(sStation, timeStartDate, timeEndDate, timeFirstYear,\
                     timeLastYear, sLastYear, sPeriod=None):
   """
   When a specific starting date is given, check if it falls between the intervals. 
   Return the interval in a list if it falls between valid dates,  None otherwise.
   """
   
   if timeStartDate > timeLastYear: # start date is after the last year of recording
      my_print("Station " + sStation + ":\n\t" +sPeriod +" values: requested year(s)" + \
               " is after the station started to record values", nMessageVerbosity=NORMAL)
      my_print("\tRequested year: " + timeStartDate.strftime('%Y-'), \
               nMessageVerbosity=NORMAL)
      my_print("\tLast year for this station: " + timeLastYear.strftime('%Y') + ". Skipping",\
               nMessageVerbosity=NORMAL)
      return None
   elif timeEndDate == None : # No ending date, covers the whole period after valid start date
      sStartYearRequested = datetime.datetime.strftime(timeStartDate, "%Y-%m")
      my_print("Station " + sStation + ":", nMessageVerbosity=VERBOSE)
      if timeStartDate < timeFirstYear:
         sFirstYear = datetime.datetime.strftime(timeFirstYear, "%Y-%m")
         my_print("\tRequested start date before first year for this station. Changing " +\
               sStartYearRequested +" with " +sFirstYear, nMessageVerbosity=VERBOSE)
         sStartYearRequested = datetime.datetime.strftime(timeFirstYear, "%Y-%m")
      my_print("\tgetting " +sPeriod + " values for period: [" +\
               sStartYearRequested + "," + sLastYear + "]" , nMessageVerbosity=VERBOSE)
      return [sStartYearRequested, sLastYear]
   elif timeEndDate < timeFirstYear: # Requested period is before observations started
      my_print("Station " + sStation + ":\n\t" +sPeriod + " values: requested year" + \
               " is before the station started to record values", nMessageVerbosity=NORMAL)
      my_print("\tLast year requested: " + timeEndDate.strftime('%Y'), \
               nMessageVerbosity=NORMAL)
      my_print("\tStarting year for this station: " + timeFirstYear.strftime('%Y') + ". Skipping",\
               nMessageVerbosity=NORMAL)
      return None
   else: # Period is covered
      sStartYearRequested = datetime.datetime.strftime(timeStartDate, "%Y-%m")
      sEndYearRequested = datetime.datetime.strftime(timeEndDate, "%Y-%m")
      my_print("Station " + sStation + ":\n\tgetting " +sPeriod +" values for period: [" +\
               sStartYearRequested + "," + sEndYearRequested + "]" , nMessageVerbosity=VERBOSE)
      return [sStartYearRequested, sEndYearRequested]

   
def check_end_date(sStation, timeStartDate, timeEndDate, timeFirstYear,\
                     timeLastYear, sFirstYear, sPeriod=None):
   """
   When a specific ending date is given, check if it falls between the intervals. 
   Return the interval in a list if it falls between valid dates,  None otherwise.
   """
   
   if timeEndDate < timeFirstYear: # Requested period is before observations started
      my_print("Station " + sStation + ":\n\t" +sPeriod + " values: requested year(s)" + \
               " is before the station started to record values", nMessageVerbosity=NORMAL)
      my_print("\tLast year requested: " + timeEndDate.strftime('%Y'), \
               nMessageVerbosity=NORMAL)
      my_print("\tStarting year for this station: " + timeFirstYear.strftime('%Y'),\
               nMessageVerbosity=NORMAL)
      my_print("\tSkipping", nMessageVerbosity=NORMAL)
      return None
   elif timeStartDate == None:
      if timeEndDate >  timeLastYear: # end-date is after last year
         sEndYearRequested = datetime.datetime.strftime(timeLastYear, "%Y-%m")
         my_print("Station " + sStation + ":\n\tLast year after the valid station period. " + \
                     "Using the last year for station instead of requested date")
         my_print("\tgetting " +sPeriod +" values for period: [" +\
                     sFirstYear + "," + sEndYearRequested + "]" , nMessageVerbosity=VERBOSE)
         return [sFirstYear, sEndYearRequested]
      else:
         sEndYearRequested = datetime.datetime.strftime(timeEndDate, "%Y-%m")
         my_print("Station " + sStation + ":\n\tgetting " +sPeriod +" values for period: [" +\
                  sFirstYear + "," + sEndYearRequested + "]" , nMessageVerbosity=VERBOSE)
         return [sFirstYear, sEndYearRequested]
   
def check_monthly(sStation, lDateRequested, sFirstYear, sLastYear):
   """
   INPUT
   sStation: Station ID for logging purpose
   lDateRequested: List of requested dates in strptime format. In order:
     1- Specific date
     2- Start date
     3- End date
   sFirstYear: String in format YYYY for the first year of recording of the station
   sEndYear: String in format YYYY for the last year of recording of the station
   
   OUTPUT
   Return True if the requested year is valid, False otherwise.
   """
   
   [timeDate, timeStartDate, timeEndDate] = lDateRequested
   
   # Check if the station records monthly value (one file per station covers the whole period)
   if len(sFirstYear) == 0: 
      my_print("Station " + sStation + " does not have monthly value. Skipping.",
               nMessageVerbosity=NORMAL)
      return None

   timeFirstYear = datetime.datetime.strptime(sFirstYear, '%Y')
   timeLastYear = datetime.datetime.strptime(sLastYear, '%Y')

   # If no date provided, download the data
   if timeDate == None and timeStartDate == None and timeEndDate == None :
      my_print("Station " + sStation + ": getting monthly values ", nMessageVerbosity=VERBOSE)
      return True
         
   # If a specific date is required
   if timeDate != None:
      bInterval = check_specific_date(sStation, timeDate, \
                                      timeFirstYear, timeLastYear, sPeriod="monthly")
      return bInterval
   # If the start date is specified
   elif timeStartDate != None:
      lInterval = check_start_date(sStation, timeStartDate, timeEndDate, \
                                   timeFirstYear, timeLastYear, sLastYear, sPeriod="monthly")
      
   # If only the end date is specified
   else:
      lInterval = check_end_date(sStation, timeStartDate, timeEndDate, \
                                   timeFirstYear, timeLastYear, sFirstYear, sPeriod="monthly")

   if lInterval != None:
      return True
   else:
      return None
      
def check_daily(sStation, lDateRequested, sFirstYear, sLastYear):
   """
   INPUT
   sStation: Station ID for logging purpose
   lDateRequested: List of requested dates in strptime format. In order:
     1- Specific date
     2- Start date
     3- End date
   sFirstYear: String in format YYYY for the first year of recording of the station
   sEndYear: String in format YYYY for the last year of recording of the station
   
   OUTPUT
   Return the interval to download [YYYY, YYYY]. Since there is only one file per year, only the
   years are needed to identify the download period.
   """

   [timeDate, timeStartDate, timeEndDate] = lDateRequested
   
   # Check if the station records daily value (one file per station covers the whole period)
   if len(sFirstYear) == 0: 
      my_print("Station " + sStation + " does not have daily value.\n\tSkipping.",
               nMessageVerbosity=NORMAL)
      return None

   # If no date provided, download the data for the whole period
   if timeDate == None and timeStartDate == None and timeEndDate == None :
      my_print("\tgetting daily values for the whole period: ["\
               +sFirstYear +"," +sLastYear  +"]", nMessageVerbosity=VERBOSE)
      return [sFirstYear, sLastYear]

   timeFirstYear = datetime.datetime.strptime(sFirstYear, '%Y')
   timeLastYear = datetime.datetime.strptime(sLastYear, '%Y')

   # If a specific date is required
   if timeDate != None:
      bInterval = check_specific_date(sStation, timeDate, \
                                      timeFirstYear, timeLastYear, sPeriod="daily")
      if bInterval :
         sRequestedYear = datetime.datetime.strftime(timeDate, "%Y")
         my_print("\tgetting daily values for period: [" +\
                   sRequestedYear + "," + sRequestedYear + "]" , nMessageVerbosity=VERBOSE)
         lInterval = [sRequestedYear, sRequestedYear]
      else:
         return None

   # If the start date is specified
   elif timeStartDate != None:
      lInterval = check_start_date(sStation, timeStartDate, timeEndDate, \
                                   timeFirstYear, timeLastYear, sLastYear, sPeriod="daily")
   
   # If only the end date is specified
   else:
      lInterval = check_end_date(sStation, timeStartDate, timeEndDate, \
                                 timeFirstYear, timeLastYear, sFirstYear, sPeriod="daily")

   return lInterval

def check_hourly(sStation, lDateRequested, sFirstYear, sLastYear):
   """
   INPUT
   sStation: Station ID for logging purpose
   lDateRequested: List of requested dates in strptime format. In order:
     1- Specific date
     2- Start date
     3- End date
   sFirstYear: String in format YYYY for the first year  of recording of the station
   sEndYear: String in format YYYY for the last year of recording of the station
   
   OUTPUT
   Return the interval to download [YYYY-MM, YYYY-MM]. Since there is only one file per month, 
   only the months are needed to identify the download period.
   """

   [timeDate, timeStartDate, timeEndDate] = lDateRequested

   # Check if the station records hourly value (one file per station covers the whole period)
   if len(sFirstYear) == 0: 
      my_print("Station " + sStation + " does not have hourly value.\n\tSkipping.",
               nMessageVerbosity=NORMAL)
      return None
   # Since there is no information for starting/ending month, assumed January for start and
   # December for the last year.
   else:
      sFirstYear = sFirstYear + "-01"
      sLastYear = sLastYear + "-12"
      
   # If no date provided, download the data for the whole period
   if timeDate == None and timeStartDate == None and timeEndDate == None :
      my_print("\tgetting hourly values for the whole period: ["\
               +sFirstYear +"," +sLastYear  +"]", nMessageVerbosity=VERBOSE)
      return [sFirstYear, sLastYear]

   timeFirstYear = datetime.datetime.strptime(sFirstYear, '%Y-%m')
   timeLastYear = datetime.datetime.strptime(sLastYear, '%Y-%m')

   # If a specific date is required
   if timeDate != None:
      bInterval = check_specific_date(sStation, timeDate, \
                                      timeFirstYear, timeLastYear, sPeriod="hourly")
      if bInterval:
         sRequestedYearMonth = datetime.datetime.strftime(timeDate, "%Y-%m")
         my_print("\tgetting hourly values for period: [" +\
                   sRequestedYearMonth + "," + sRequestedYearMonth + "]" ,\
                  nMessageVerbosity=VERBOSE)
         return [sRequestedYearMonth, sRequestedYearMonth]
      else:
         return None

   # If the start date is specified
   elif timeStartDate != None:
      lInterval = check_start_date(sStation, timeStartDate, timeEndDate, \
                                 timeFirstYear, timeLastYear, sLastYear, sPeriod="hourly")

   # If only the end date is specified
   else:
      lInterval = check_end_date(sStation, timeStartDate, timeEndDate, \
                                 timeFirstYear, timeLastYear, sFirstYear, sPeriod="hourly")

   return lInterval
  
def set_interval_date(lStationRequested, dObsPeriod, lDateRequested):
   """
   Check if the interval requested on command line are available for each station requested.

   INPUT
   lStationRequested: List of Station ID of requested stations.
   dObsPeriod: Dictionnary linking the hourly/daily/monthly obs period request to a boolean.
   lDateRequested: List of requested dates in strptime format. In order:
     1- Specific date
     2- Start date
     3- End date

   OUTPUT
   dStationStartEndDates: dictionnary with station ID as key. Each station is linked to a 
   dictionnary with 3 keys: "monthly" "daily" "hourly"
   "monthly" only needs a boolean, since one file covers the whole period. You download the file, or you don't.
   "daily" is a list of years [YYYY, YYYY]
   "hourly" is a list of year and month [YYYY-MM, YYYY-MM]

   
 
   """
   dStationStartEndDates = {}

   for sStation in lStationRequested:
      dStation = dStationList[sStation]

      # Initialisation of the start/end date dictionnary
      dStationStartEndDates[sStation] = { "monthly" : False , \
                                          "daily" :  None , \
                                          "hourly" :  None }
                                          
      if dObsPeriod["monthly"]: # Check for monthly values
         sFirstYear = dStation["MLY First Year"]
         sLastYear = dStation["MLY Last Year"]

         dStationStartEndDates[sStation]["monthly"] = \
                                                      check_monthly(sStation, lDateRequested, sFirstYear, sLastYear)

      if dObsPeriod["daily"]: # Check for daily values
         sFirstYear = dStation["DLY First Year"]
         sLastYear = dStation["DLY Last Year"]

         dStationStartEndDates[sStation]["daily"] = \
                                                      check_daily(sStation, lDateRequested, sFirstYear, sLastYear)
         
      if dObsPeriod["hourly"]: # Check for hourly values
         sFirstYear = dStation["HLY First Year"]
         sLastYear = dStation["HLY Last Year"]

         dStationStartEndDates[sStation]["hourly"] = \
                                                      check_hourly(sStation, lDateRequested, sFirstYear, sLastYear)

      # Remove item from the dictionnaries if there is no valid interval
      if dStationStartEndDates[sStation]["monthly"] == False and \
         dStationStartEndDates[sStation]["daily"] == None and \
         dStationStartEndDates[sStation]["hourly"] == None:
         my_print("\tStation does not have any valid date period.",\
                  nMessageVerbosity=VERBOSE)
         del dStationStartEndDates[sStation]
         
   return dStationStartEndDates

def create_url(dStationDates, sDirectory, bNoTree, sLang, sFormat, bNoClobber):
   """
   INPUT
   dStationDates: dictionnary containing the station number as the key, and a dictionnary as the value.
     The dictionnary contains the start/end dates for monthly/daily/hourly request.
   sDirectory: string for the local path where the files should be saved. In case it is not given, the path where the file
     is executed is chosen. 
   sLang: English or French
   sFormat: CSV or XML

   OUTPUT
   lUrlPath : a list of lists. The contained lists are [URL, localpath] for every file to download.
   """

   my_print("Creating the path for the files to download", nMessageVerbosity=VERBOSE)
   
   # If output directory is not given, use the default
   if sDirectory == None:
      sDirectory = os.path.dirname(os.path.realpath(__file__))

   # Check if the directory can be written by the user
   if not os.access(sDirectory, os.W_OK):
      my_print("ERROR: you do not have permission to write on the output directory:\n\t" +sDirectory +\
               "\nPlease change the permission or change the output directory", nMessageVerbosity=NORMAL)
      return

   lUrlPath = []
   for sStation in dStationDates.keys():
      sDirectoryStation = sDirectory + "/" +sStation
      # Check monthly
      if dStationDates[sStation]["monthly"] == True:
         if bNoTree:
            sDirectoryStationMonth = sDirectory
         else:
            sDirectoryStationMonth = sDirectoryStation + "/monthly"

         sPathWildCard = sDirectoryStationMonth + "/" + sLang + "*-monthly-??????-??????." + sFormat
         if bNoClobber and glob.glob(sPathWildCard) :
            my_print("File already exists:\n\t" + sPathWildCard + "\n\tSkipping",\
                     nMessageVerbosity=NORMAL)
         else:
            sMonthlyURL = get_monthly_url(sStation, sLang, sFormat)
            lUrlPath.append([sMonthlyURL,sDirectoryStationMonth])

      # Check daily
      if dStationDates[sStation]["daily"] != None:
         if bNoTree:
            sDirectoryStationDay = sDirectory
         else:
            sDirectoryStationDay = sDirectoryStation + "/daily"

         lStartEnd = dStationDates[sStation]["daily"]
         lDailyURL = get_daily_url(sStation, sLang, sFormat, lStartEnd, \
                                   sDirectoryStationDay, bNoClobber)
         for sDailyURL in lDailyURL:           
            lUrlPath.append([sDailyURL,sDirectoryStationDay])

      # Check hourly
      if dStationDates[sStation]["hourly"] != None:
         if bNoTree:
            sDirectoryStationHour = sDirectory
         else:
            sDirectoryStationHour = sDirectoryStation + "/hourly"
         lStartEnd = dStationDates[sStation]["hourly"]
         lHourlyURL = get_hourly_url(sStation, sLang, sFormat, lStartEnd, \
                                     sDirectoryStationHour, bNoClobber)
         for sHourlyURL in lHourlyURL:           
            lUrlPath.append([sHourlyURL,sDirectoryStationHour])

   my_print("Number of files to download: " + str(len(lUrlPath)), \
            nMessageVerbosity=VERBOSE)
   return lUrlPath

def  get_monthly_url(sStation, sLang, sFormat):
   """
   INPUT
   sStation: station ID
   sLang: language in which to dowload the data
   sFormat: CSV or XML:

   OUTPUT
   sURL: URL to download the monthly data
   """

   if sLang == "en":
      sURL = "http://climate.weather.gc.ca/climate_data/bulk_data_e.html?format=" +\
             sFormat + "&stationID=" +sStation +"&timeframe=3&submit=Download+Data"
   elif sLang == "fr":
      sURL = "http://climat.meteo.gc.ca/climate_data/bulk_data_f.html?format=" +\
             sFormat + "&stationID=" +sStation +"&timeframe=3&submit=++T%C3%A9l%C3%A9charger+%0D%0Ades+donn%C3%A9es"

   return sURL

def  get_daily_url(sStation, sLang, sFormat, lStartEndTime, sDirectory, bNoClobber):
   """
   INPUT
   sStation: station ID
   sLang: language in which to dowload the data
   sFormat: CSV or XML:
   lStartEndTime: list containing the string for start and end for the period

   OUTPUT
   lURL: URLs to download the daily data for the period
   """

   
   if sLang == "en":
      sStartURL = "http://climate.weather.gc.ca/climate_data/bulk_data_e.html?format=" +\
             sFormat + "&stationID=" +sStation +"&Year="
      sEndURL = "&timeframe=2&submit=Download+Data"
   elif sLang == "fr":
      sStartURL = "http://climat.meteo.gc.ca/climate_data/bulk_data_f.html?format=" +\
             sFormat + "&stationID=" +sStation +"&Year"
      sEndURL = "&timeframe=2&submit=++T%C3%A9l%C3%A9charger+%0D%0Ades+donn%C3%A9es"

   lUrl = []
   [sStart, sEnd] = lStartEndTime
   for nYear in range(int(sStart[0:4]),int(sEnd[0:4])+1):
      sYear = str(nYear)
      sPathWildCard = sDirectory + "/" + sLang + "*-daily-0101" + sYear +\
                      "-1231" + sYear + "." + sFormat
      if bNoClobber and glob.glob(sPathWildCard) :
         my_print("File already exists:\n\t" + sPathWildCard + "\n\tSkipping",\
                  nMessageVerbosity=NORMAL)
      else:
         sURL = sStartURL + sYear + sEndURL
         lUrl.append(sURL)

   return lUrl

def  get_hourly_url(sStation, sLang, sFormat, lStartEndTime, sDirectory, bNoClobber):
   """
   INPUT
   sStation: station ID
   sLang: language in which to dowload the data
   sFormat: CSV or XML:
   lStartEndTime: list containing the string for start and end for the period

   OUTPUT
   lURL: URLs to download the hourly data for the period
   """

   if sLang == "en":
      sStartURL = "http://climate.weather.gc.ca/climate_data/bulk_data_e.html?format=" +\
             sFormat + "&stationID=" +sStation +"&Year="
      sEndURL = "&timeframe=1&submit=Download+Data"
   elif sLang == "fr":
      sStartURL = "http://climat.meteo.gc.ca/climate_data/bulk_data_f.html?format=" +\
             sFormat + "&stationID=" +sStation +"&Year"
      sEndURL = "&timeframe=1&submit=++T%C3%A9l%C3%A9charger+%0D%0Ades+donn%C3%A9es"

   lUrl = []
   [sStart, sEnd] = lStartEndTime
   timeStart = datetime.datetime.strptime(sStart, "%Y-%m")
   timeEnd = datetime.datetime.strptime(sEnd, "%Y-%m")
   
   for time1 in rrule.rrule(rrule.MONTHLY, dtstart=timeStart, until=timeEnd):
      sYear = datetime.datetime.strftime(time1, "%Y")
      sMonth = datetime.datetime.strftime(time1, "%m")

      sPathWildCard = sDirectory + "/" + sLang + "*-hourly-" + sMonth + "??" +sYear +\
                      "-" + sMonth + "??" +sYear + "." + sFormat
      if bNoClobber and glob.glob(sPathWildCard) :
         my_print("File already exists:\n\t" + sPathWildCard + "\n\tSkipping",\
                  nMessageVerbosity=NORMAL)
      else:
         sURL = sStartURL + sYear + "&Month=" +sMonth + sEndURL
         lUrl.append(sURL)

   return lUrl

def download_files(lUrlAndPath, bDryRun):
   """
   INPUT:
   lUrlAndPath: a list of list containing two values: the URL to download 
    and the path where the file should be copied on the local computer.
   bDryRun: if set to True, do not download or create directory.
   """

   # Create directories
   lDirectories = [item[1] for item in lUrlAndPath]
   create_directories(lDirectories, bDryRun)
   
   # Set the progress bar
   rows, columns = os.popen('stty size', 'r').read().split()
   nWidth = int(columns) - 32
   bar = Bar('Downloading', max=len(lUrlAndPath), width=int(nWidth))

   for lList in lUrlAndPath:
      [sURL, sDirectory] = lList
      if not bDryRun:
         # Download the file
         httpResponse = urllib.request.urlopen(sURL)
         # Extract the provided filename
         _,params = cgi.parse_header(httpResponse.headers.get('Content-Disposition', ''))
         sFilename = params['filename']
         bar.next()
         my_print("Downloading file:\n\t" + sFilename, nMessageVerbosity=VERBOSE)
         my_print("and saving on local directory:\n\t" + sDirectory, \
                  nMessageVerbosity=VERBOSE)
         sPath = sDirectory + "/" + sFilename
         fichier = open(sPath,  "wb")
         fichier.write(httpResponse.read())
         fichier.close()
      else:
         my_print("--dry-run mode: file not downloaded:\n\t" + sURL, \
                  nMessageVerbosity=NORMAL)
            
            
   bar.finish()

      
def create_directories(lDirectories, bDryRun):
      """
      Check if directories exists in the list lDirectories. If not, create it, unless we are in 
      --dry-run mode.
      """

      lDirectoryCreated =[]
      
      for sDirectory in lDirectories:
         # Check if the directory has not been created and does not exists
         if sDirectory not in lDirectoryCreated and \
            not os.path.isdir(sDirectory):
            my_print("Directory does not exists \n\t" + sDirectory, nMessageVerbosity=NORMAL)
            if bDryRun:
               my_print("\t--dry-run mode: directory is not created", nMessageVerbosity=NORMAL)
            else:
               my_print("\tCreating directory", nMessageVerbosity=NORMAL)
               os.makedirs(sDirectory)
            lDirectoryCreated.append(sDirectory)
      
def get_canadian_weather_observations(tOptions):
   """
   Download the observation files from Environment and Climate change Canada (ECCC)
   on your local computer.
   """

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
   elif tOptions.Information: # print the lines of the station dictionnary and exits
      for sStation in lStationList:
         my_print("----", nMessageVerbosity=NORMAL)
         my_print ("Station ID: " + sStation, nMessageVerbosity=NORMAL )
         row = dStationList[sStation]
         for sItem in row:
            my_print (sItem + ":" + row[sItem], nMessageVerbosity=NORMAL)
      return

   # If dates are provided, check if the string format is fine.
   lRequestedDate = check_input_dates\
                    ([tOptions.RequestedDate, tOptions.StartDate, tOptions.EndDate])

   # Check if we can contact ECCC web site
   check_eccc_climate_connexion()

   # Check if the requested dates are available for each station
   dObsPeriod = { "hourly"  : tOptions.Hourly,\
                  "daily"   : tOptions.Daily, \
                  "monthly" :tOptions.Monthly}  
   dStationStartEndDates = set_interval_date(lStationList, dObsPeriod, lRequestedDate)

   if len(dStationStartEndDates.keys()) == 0: # If nothing fits.
      my_print ("No station found corresponding to date arguments. " + \
                "Please check the input stations or the date arguments.", \
                nMessageVerbosity=NORMAL)
      return

   # Create the URL for all the files requested
   lUrlPath = create_url(dStationStartEndDates, tOptions.OutputDirectory, \
                         tOptions.NoTree, tOptions.Language, tOptions.Format, tOptions.NoClobber)
   
   download_files(lUrlPath, tOptions.DryRun)

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
                     help="Directory where the files will be downloaded, in their corresponding sub-directory or not (see --no-tree option). Default value is where the script get_canadian_weather_observations.py is located.",\
                     action="store", type=str, default=None)
   parser.add_argument("--no-tree", "-n", dest="NoTree", \
                       help="Do not create directories, download all the files in the output directory.",\
                       action="store_true", default=False)
   parser.add_argument("--no-clobber", "-N", dest="NoClobber", \
                     help=" Do not overwrite an existing file",\
                     action="store_true", default=False)

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
   
   parser.add_argument("--info", "-I", dest="Information", \
                     help="Get and print the information (lat, lon, code, start/end date, etc.) for the selected station(s) and exit.",\
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
      options.Monthly is False and \
      options.Information is False:
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
