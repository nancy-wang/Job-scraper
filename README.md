# Web-Scraper-in-Python-with-BeautifulSoup
This is a web scraper/crawler which grabs all of the current jobs from indeed, based on search urls.  This will 'click' on the Next button until there are no more jobs to grab.  This utilizes the BeautifulSoup4 3rd party package.

Usage
--------------
The url_list which is including searches for various jobs in the financial district of San Francisco.  In most cases, there are 100 pages for this script to crawl through, collecting data.  The script will not print anything to standard out, unless some level of verbosity is defined.

`.\runIndeedJobScrap.py -v`

I included an additional file which will scrap one page, and print the results.  This file is for development purposes.

`.\runSimpleScrap.py`


Dependances
--------------
Python 3.5: These scripts were developed against Python 3.5.

BeautifulSoup 4: You will need to install BeautifulSoup in order to run these libraries.
  Here is a link to the specific version that I used for this project:
  https://www.crummy.com/software/BeautifulSoup/bs4/download/4.4/beautifulsoup4-4.4.1.tar.gz


