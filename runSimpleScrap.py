"""This is more for figuring out the best way to parse a page.
"""

import re
import urllib.request
from bs4 import BeautifulSoup
from bs4 import UnicodeDammit


url = "http://www.indeed.com/jobs?q=python&l=94111"

with urllib.request.urlopen(url) as urldata:
    rawtext = urldata.read().decode('utf-8', 'ignore')
    #rawtext2 = UnicodeDammit(rawtext)
    soup_obj = BeautifulSoup(rawtext, 'html.parser')

    # Get job listings on this page.
    jobSearchResults = soup_obj.select(".result")
    for job in jobSearchResults:
        # Get the job details based on classes used for the elements.
        jobTitle = job.select(".jobtitle")[0].text.lstrip().rstrip()
        companyName = job.select(".company")[0].text.lstrip().rstrip()
        jobLocation = job.select(".location")[0].text.lstrip().rstrip()
        summary = job.select(".summary")[0].text.lstrip().rstrip()

        # Figured out if this ad is sponsored.
        isSponsered = ""
        sponderedSpans = job.find_all("span")
        if len(sponderedSpans) > 0:
            #print("###found sponsers")
            for span in sponderedSpans:
                spanText = span.text.lstrip().rstrip()
                #print("******** :" + spanText)
                if re.match("Sponsored", spanText) is not None:
                    isSponsered = spanText
                    #print("###########Found a sponsered item.")

        # Get the job URL.
        # Select returns a string instead of an intelligent object.
        all_job_links = job.find_all("a")
        for link in all_job_links:
            try:
                if "turnstileLink" in link['class']:
                    jobLinkURL = "http://www.indeed.com" + link['href']
                    # There can be muliples.
                    # break

            except:
                # Not all links will have a class key.
                pass

        # Print out what we are finding, if we want that much information.
        print("----------------")
        try:
            #print(job)
            #print("################")
            print(jobTitle)
            print(isSponsered)
            print(companyName)
            print(jobLocation)
            print(summary)
            print(jobLinkURL)
        except:
            print("### FAILED TO PARSE JOB.")

    print()
    print()
    # Get the next link.
    next_links = soup_obj.select(".pagination")[0].find_all('a')
    for link in next_links:
        if re.match("Next", link.text) is not None:
            print("###########Found link:" + link['href'])
