#A web scraper to do job searches for Health Leads clients 
#This code was adapted from https://github.com/Futvin/Web-Scraper-in-Python-with-BeautifulSoup/blob/master/runSimpleScrap.py
import re
import urllib.request
from bs4 import BeautifulSoup
from docx import Document

document = Document()
document.add_heading('Job Listings', 0)

def crawler_func(url):

	#file = open("job_listings.txt", "w")

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
   			
   			document.add_paragraph(jobTitle)
   			document.add_paragraph(companyName)
   			document.add_paragraph(jobLocation)
   			document.add_paragraph(jobURL)
   			#file.write(jobTitle)
   			#file.write("\n")
   			#file.write(companyName)
   			#file.write("\n")
   			#file.write(jobLocation)
   			#file.write("\n")
   			#file.write(jobURL)
   			#file.write("\n")
   			#file.write("\n")
		except:
   			pass
		document.save('job_listings.docx')
		print("\n\n")
	#hard coding a way to only read two pages worth of data, LOL
	#if (count <= 1):
	#	try:
	#		page = 10
	#		url = url + "&start=" + str(page)
	#		print(url)
	#		count+=1
	#		crawler_func(url, count)
			
	#	except:
	#		exit()
	#next_link = soup.select(".pagination")[0].find_all('a')
	#page = 0
	#for link in next_link:
   		#if re.match("Next", link.text) is not None:
   			#print(link)
   			#page+= 10
   			#url = url + "&start=" + str(page)
   			#print(url)
   			#crawler_func(url)
   			#print("hi")
   		#else:
   		#	exit()

def menu():
	print("Hey fellow Employment Specialist! Welcome to the job scraper!")
	zipcode = input("Please input the zipcode of the job you are looking for.\nIf you don't know what zipcode you're looking for, enter 'N/A' and the default location will be set to Baltimore\n")
	if (zipcode == "N/A"):
		zipcode = 21218
	job = input("Please input the type of job you're seeking.\nIf your input is more than one word, please separate spaces with + symbols, e.g. 'night+jobs'\n")
	radius = input("Please input how far you can travel.\n If no preference, input 25.\n")
	sortdate = input("Type 'y' if you'd like to sort by date.\n")
	if (sortdate=='y'):
		url = "https://www.indeed.com/jobs?q=" + str(job) + "&l=" + str(zipcode) + "&radius=" + str(radius) + "&sort=date"
	else: 
		url = "https://www.indeed.com/jobs?q=" + str(job) + "&l=" + str(zipcode) + "&radius="
	#count = 1
	print("Thanks! Starting search now...")
	print(url)
	crawler_func(url)

menu()

