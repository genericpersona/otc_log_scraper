otc_log_scraper
===============

#bitcoin-otc log scraper

This script is used to scrape the public logs for freenode's #bitcoin-otc
channel.  It takes a range of dates and times for each of the days, grabs the
logs for those days and outputs their contents.

This script requires Python 2.7 and several 3-rd party libraries:

    -- BeautifulSoup4 for HTML scraping
    -- dateutil for parsing strings containing dates
                and converting them into datetime objects
    -- requests for speaking HTTP
