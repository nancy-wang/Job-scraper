#A web scraper to do job searches for Health Leads clients 
#This code was adapted from https://github.com/Futvin/Web-Scraper-in-Python-with-BeautifulSoup/blob/master/runSimpleScrap.py
import re
import urllib.request
from bs4 import BeautifulSoup


def crawler_func(url):
	with urllib.request.urlopen(url) as urldata:
		rawtext = urldata.read().decode('utf-8', 'ignore')
		soup = BeautifulSoup(rawtext, 'html.parser')

	jobListings = soup.select(".result")
	for job in jobListings:
		#Get job details
		jobTitle= job.select(".jobtitle")[0].text.lstrip().rstrip()
		companyName = job.select(".company")[0].text.lstrip().rstrip()
		jobLocation = job.select(".location")[0].text.lstrip().rstrip()

   #get job URL
		all_jobs = job.find_all("a")
		for link in all_jobs:
   			try:
   				if "turnstileLink" in link['class']:
   					jobURL = "https://www.indeed.com" + link['href']
   			except:
   				pass
		print("-----")
		try:
   			print(jobTitle)
   			print(companyName)
   			print(jobLocation)
   			print(jobURL)
		except:
   			print("Couldn't get info for this job - sorry!")

		print("\n\n")
	next_link = soup.select(".pagination")[0].find_all('a')
	for link in next_link:
   		if re.match("Next", link.text) is not None:
   			print("End of job search")

def menu():
	print("Hey fellow Employment Specialist! Welcome to the job scraper!")
	zip = input("Please input the zipcode of the job you are looking for.\nIf you don't know what zipcode you're looking for, enter 'N/A' and the default location will be set to Baltimore\n")
	if (zip == "N/A"):
		zip = 21218
	job = input("Please input the type of job you're seeking.\nIf your input is more than one word, please separate spaces with + symbols, e.g. 'night+jobs'\n")
	url = "https://www.indeed.com/jobs?q=" + str(job) + "&l=" + str(zip)
	print(url)
	crawler_func(url)

menu()

