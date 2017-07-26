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

VERSION = "0.1"
# Verbose level:
## 1 Normal mode
## 2 Full debug
NORMAL= 1
VERBOSE= 2

nGlobalVerbosity = 1

def my_print(sMessage, nMessageVerbosity=NORMAL):
   """
   Use this method to write the message in the standart output 
   """

   if nMessageVerbosity == NORMAL:
      print (sMessage)
   elif nMessageVerbosity == VERBOSE and nGlobalVerbosity == VERBOSE:
      print (sMessage)
   
def get_canadian_weather_observations(tOptions):
   """
   Download the observation files from Environment and Climate change Canada (ECCC) on your local computer.
   """



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
   parser.add_argument("--dry-run", "-t", dest="DryRun", \
                     help="Execute the program, but do not download any file",\
                       action="store_true", default=False)
   parser.add_argument("--lang", "-l", dest="Language",  \
                     help="Language in which the data will be downloaded (en = English, fr = French). Default is English.",\
                       action="store", type=str, default="en")   
   parser.add_argument("--format", "-F", dest="Format",  \
                       help="Download the files in 'csv' or 'xml' format. Default value is 'csv'.",\
                       action="store", type=str, default="xml")
   # Date stuff
   parser.add_argument("--date", "-d", dest="DateRequested", \
                       help="Get the observations for this specific date only.  --start-date and  --end-date are ignored if provided. Format is YYYY[-MM[-DD]]",\
                       action="store", type=lambda d: datetime.strptime(d, '%Y-%m-%d'), default=None)
   parser.add_argument("--start-date", "-e", dest="StartDate", \
                       help="Get the observations after this date. Stops at --end-date if specified, otherwise download the observations until the last observation available. Format is YYYY[-MM[-DD]]",\
                       action="store", type=lambda d: datetime.strptime(d, '%Y-%m-%d'), default=None)
   parser.add_argument("--end-date", "-f", dest="EndDate", \
                       help="Get the observations before this date. Stops at --start-date if specified, otherwise download the observations until the first observation available. Format is YYYY[-MM[-DD]]",\
                       action="store", type=lambda d: datetime.strptime(d, '%Y-%m-%d'), default=None)
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
