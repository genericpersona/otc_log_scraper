otc_log_scraper
===============

#bitcoin-otc log scraper

This script is used to scrape the public logs for freenode's #bitcoin-otc
channel.  It takes a range of dates and times for each of the days, grabs the
logs for those days and outputs their contents.

Caveat: All dates and times given to the script MUST be in UTC.

This script requires Python 2.7 and several 3rd party libraries:

    -- BeautifulSoup4   (for HTML scraping)
    -- dateutil         (for parsing strings containing dates
                        and converting them into datetime objects)
    -- requests         (for speaking HTTP)

Some example uses:

    To get the logs for today:

        ./otc_log_scraper.py

    To get the logs for today saved to a file named today_otc_logs:

        ./otc_log_scraper.py -o today_otc_logs

        or

        ./otc_log_scraper.py --output today_otc_logs

    To get the logs for the past two weeks:

        ./otc_log_scraper.py -w 2

        or

        ./otc_log_scraper.py --weeks 2

    To get the logs from yesterday to today during 0800 - 1700:

        ./otc_log_scraper.py --hours-from 8 --hours-to 17

