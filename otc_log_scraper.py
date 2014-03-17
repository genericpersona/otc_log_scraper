#!/usr/bin/env python2
# -*- encoding: utf-8 -*-

# bitcoin-otc Log Scraper
# Copyright (C) 2014 by genericpersona
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

# Imports
import argparse
from datetime import datetime
from datetime import timedelta
from pprint import pprint
import sys

# All 3-rd party library imports
# Requires:
#   BeautifulSoup4 (for HTML parsing)
#   dateutil       (for date parsing and manipulation)
#   requests       (for HTTP logic)
from bs4 import BeautifulSoup
from dateutil.parser import parse
from dateutil.relativedelta import relativedelta
import requests

# Constants
log_url = 'http://bitcoinstats.com/irc/bitcoin-otc/logs/{year}/{month}/{day}'

def get_logs(date, time_start='00:00', time_end='23:59'):
    '''
    Grabs the #bitcoin-otc logs from a particular date 
    and from a particular range of hours and minutes
    as specified by time_start and time_end.

    This function only grabs logs for a single day.

    Return a list of 3-tuples where:
        (timestamp (%Y/%m/%d %H:%M), nick, message)
    '''
    # Parse the date
    date = parse(date)
    year, month, day = date.strftime('%Y/%m/%d').split('/')

    # Get the HTML for the log
    r = requests.get(log_url.format(year=year, month=month, day=day))
    soup = BeautifulSoup(r.text)

    # All messages are a separate table
    tables = soup.find_all('tr')

    # Save the log for the day broken down
    # into individual lines as 3-tuples 
    # such that:
    #
    #   (timestamp, nick, message)
    lines = []
    for table in tables:
        rows = table.find_all('td')
        timestamp = rows[0].find_all('a')[-1].string

        # Make sure the timestamp is within the desired range
        ts_dt = datetime.strptime(timestamp, '%H:%M')
        if not ((ts_dt >= datetime.strptime(time_start, '%H:%M')) and \
                            (ts_dt <= datetime.strptime(time_end, '%H:%M'))):
            continue

        nick = rows[1].string

        message = rows[2].string

        if not message is None:
            lines.append(('/'.join((year, month, day)) + ' ' + timestamp, 
                                                            nick, message))

    return lines

def parse_args():
    # Build a parser
    description = 'Scrape the logs for freenode\'s #bitcoin-otc' + \
                  ' from a particular time period.'
    parser = argparse.ArgumentParser( description=description
                                    , formatter_class=\
                                        argparse.RawTextHelpFormatter
                                    )

    # Create arguments
    parser.add_argument( '-d'
                       , '--days'
                       , help='Number of days back to look at logs'
                       , type=int
                       , default=0
                       )
    parser.add_argument( '-w'
                       , '--weeks'
                       , help='Number of weeks back to look at logs'
                       , type=int
                       , default=0
                       )
    parser.add_argument( '-m'
                       , '--months'
                       , help='Number of months back to look at logs'
                       , type=int
                       , default=0
                       )
    parser.add_argument( '-y'
                       , '--years'
                       , help='Number of years back to look at logs'
                       , type=int
                       , default=0
                       )

    parser.add_argument( '--date'
                       , help='Specify a particular date to look up\n' + \
                              'Defaults to today'
                       , default=datetime.utcnow()
                       )
    parser.add_argument( '--date-from'
                       , help='Specify a start date to look at logs' + \
                              '\nMust be used with --date-to'
                       )
    parser.add_argument( '--date-to'
                       , help='Specify a ending date to look at logs' + \
                              '\nMust be used with --date-from'
                       )
    parser.add_argument( '--hour-from'
                       , help='Specify a start hour to look at logs\n' + \
                              'Defaults to 0'
                       , default='00'
                       , choices=range(24)
                       , metavar='HOUR-FROM'
                       )
    parser.add_argument( '--hour-to'
                       , help='Specify an ending hour to look at logs\n' + \
                              'Defaults to 23'
                       , default='23'
                       , choices=range(24)
                       , metavar='HOUR-TO'
                       )
    parser.add_argument( '--minute-from'
                       , help='Specify a start hour to look at logs\n' + \
                              'Defaults to 0'
                       , default='00'
                       , choices=range(60)
                       , metavar='MINUTE-FROM'
                       )
    parser.add_argument( '--minute-to'
                       , help='Specify an ending minute to look at logs\n' + \
                              'Defaults to 59'
                       , default='59'
                       , choices=range(60)
                       , metavar='MINUTE-TO'
                       )

    parser.add_argument( '-o'
                       , '--output'
                       , type=argparse.FileType('w')
                       , default=sys.stdout
                       , help='Output file to write log entries to\n' + \
                              'Defaults to stdout'
                       )

    return parser.parse_args()

def daterange(start_date, end_date):
    '''
    Iterator that returns subsequent
    datetime objects within particular
    range of dates.

    Yield one day at a time.

    Code taken from:
        http://ow.ly/uE2M4
    '''
    if start_date == end_date:
        yield start_date
    else:
        for n in range(int((end_date - start_date).days)):
            yield start_date + timedelta(n)
    
#------------------------------------------------#
#                                                #
#                  MAIN                          #
#                                                #
#------------------------------------------------#
if __name__ == '__main__':
    # Parse the command line arguments
    args = parse_args() 

    # Save the arguments appropriately
    # and do some error checking
    if not (args.date_to and args.date_from) and \
        not (args.date_to is None and args.date_from is None):
        quit('[Error]: Cannot have --date-to without --date-from')
    elif (args.date_from and args.date_to):
        # Build datetime objects
        df = parse(args.date_from)
        dt = parse(args.date_to)

        if df > dt:
            quit('[Error]: --date-to cannot be before --date-to')

        if df > datetime.utcnow():
            quit('[Error]: --date-from cannot be before today')
        elif dt > datetime.utcnow():
            quit('[Error]: --date-to cannot be before today')

    # Check if args.date was passed in
    if type(args.date) == str:
        date = datetime.strptime(args.date, '%Y/%m/%d') 
    else:
        date = args.date

    # Make sure the date is set correctly
    if date > datetime.utcnow(): 
        quit('[Error]: Cannot have a date past today')

    # Figure out how to call the get_logs function
    start_date = date if not args.date_from else df
    end_date = date if not args.date_to else dt
    start_time = '{}:{}'.format(args.hour_from, args.minute_from)
    end_time = '{}:{}'.format(args.hour_to, args.minute_to)

    start_date = start_date + \
            relativedelta(years=-args.years, months=-args.months,
                                    weeks=-args.weeks, days=-args.days)

    # Get the logs for the range specified
    logs = []
    for day in daterange(start_date, end_date):
        days = day.strftime('%Y/%m/%d')
        logs.extend(get_logs(days, start_time, end_time))

    # Finally, write logs to specified output file
    longest_nick = max(map(len, map(lambda x: x[1], logs)))
    args.output.write((''.join(map(lambda x: \
                            '{} {:<{}} | {}'.format(x[0].encode('utf-8'), 
                    x[1].encode('utf-8'), longest_nick, x[2].encode('utf-8')),
                                logs))))
