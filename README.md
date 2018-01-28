# Job scraper project for Health Leads

Note: I am immensely grateful for and indebted to Futvin, whose webscraping code I used as the foundation for my project: https://github.com/Futvin/Web-Scraper-in-Python-with-BeautifulSoup. Many thanks!

Health Leads is a nonprofit, student-led organization that works with low-income individuals of the Baltimore community to address social determinants of health. As an Employment Specialist at Health Leads, finding relevant jobs for my clients often consumes a large portion of the time. While I created this webscraper in hopes of making the job search more efficient and comprehensive for my clients, it has been designed for individuals of any background to use. This current version scrapes job information, comprising of the job's name, location, company, and application link, and prints it out to a Word document. It also suggests other jobs related to the original search query.

Usage
--------------
Currently must compile and run .py file to perform the job search. 


Dependencies
--------------
Python 3.5: These scripts were developed against Python 3.6.

BeautifulSoup 4: You will need to install BeautifulSoup in order to run these libraries. This can be done through running "pip install beautifulsoup4" in the command line.

Python-Docx: I also made use of the Python-Docx library to write job postings into a Word document. More information can be found here: https://python-docx.readthedocs.io/en/latest/user/install.html


