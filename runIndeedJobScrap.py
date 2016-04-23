"""
This is a simple java script which uses the BeautifulSoup4 libraries
to scrap out some job listings from the indeed website.  In this web
scrap script, my aim was to create something in one file for easy
execution and delivery.

This script will load up the starting indeed page, grab all of the
jobs listed, then go to the next page of results and do the same.
Results will be written to an output file as SQL insert statements.
"""


import argparse
import re
import queue
import urllib.request
import threading
import traceback
from concurrent.futures import ThreadPoolExecutor
from bs4 import BeautifulSoup


###########
# Globals
###########
# Many of these can be overridden on the command line.
# These are made as globals for those that don't like command line args.

# The output verbosity
verbosity = 0

# Files that we are using for input and output
output_file = "lists_output.tsv"
input_file = "url_list.txt"

# The number of concurrent scrap threads that we will use
workers = 3

# This is for adding an ID to the scraper threads to help identify them.
next_threadid = 0
threadid_lock = threading.Lock()
list_of_futures = queue.Queue()

# Thread Mananger
tpe = None


def main():
    global verbosity, input_file, output_file

    # Initialize our environment
    parse_args()
    output_data = queue.Queue()

    # Get the initial urls to process.
    url_list = load_input_file(input_file)

    # Create the thread pool for scraping urls.
    initialize_threadpool()

    # Add urls to the scrap queue
    for next_url in url_list:
        add_to_threadpool(next_url, output_data)

    # Start looking for data to process and write to our output file.
    process_page_data(output_data, output_file)


def load_input_file(infile):
    global verbosity

    if verbosity > 2:
        print("Loading data from file " + infile)

    url_list = []
    with open(infile, 'r') as fileinput:
        for line in fileinput:
            line = line.rstrip()
            # Make sure this is a line with a potential URL.
            httploc = re.search('http', line)
            if httploc is not None:
                if verbosity > 1:
                    print("Using URL: " + line)
                url_list.append(line)

    # Add some better output for verbose mode.
    if verbosity > 0:
        print()

    return url_list


def initialize_threadpool():
    global verbosity, tpe, workers

    if verbosity > 2:
        print("Starting initialize_threadpool")

    try:
        if verbosity > 0:
            print(">Creating ThreadPoolExecutor with " + str(workers) + " workers.")

        tpe = ThreadPoolExecutor(max_workers=workers)

    except Exception as e:
        print(e)

    # For some readability
    if verbosity > 0:
        print()

    #return tpe


def add_to_threadpool(next_url, output_data):
    global verbosity
    if verbosity > 2:
        print("Starting add_to_threadpool.")

    assert tpe is not None, "ThreadPoolExecutor must be defined."

    if verbosity > 0:
        print("Submitting url to be scraped: " + next_url)

    list_of_futures.put(tpe.submit(scrap_url, next_url, output_data))


# Here we will scrap the data, and only look for
# new urls to add to the scrap list.
def scrap_url(url, output_data):
    global verbosity
    myid = str(get_next_id())

    if verbosity > 2:
        print("ID:" + myid + "  Starting new scrap_url thread.")

    with urllib.request.urlopen(url) as urldata:
        rawtext = urldata.read()
        soupObj = BeautifulSoup(rawtext, 'html.parser')

        # Look up the link to the next page and add that to our queue.
        try:
            next_links = soupObj.select(".pagination")[0].find_all('a')
            for link in next_links:
                if re.match("Next", link.text) is not None:
                    next_link_url = "http://www.indeed.com" + link['href']
                    if verbosity > 1:
                        print()
                        print("ID:" + myid + "  Adding next link:" + next_link_url)
                        print()
                    add_to_threadpool(next_link_url, output_data)
        except:
            # This could fail if there are no links in the text returned.
            pass

        if verbosity > 1:
            print("ID:" + myid + "  Adding page data from queue.")

        output_data.put(soupObj)


def get_next_id():
    global next_threadid
    global threadid_lock
    global verbosity

    threadid_lock.acquire()
    next_threadid += 1
    myid = next_threadid
    threadid_lock.release()

    return myid


# This will process incoming.
def process_page_data(output_data, outfile):
    global verbosity
    if verbosity > 2:
        print("Starting process_page_data")

    with open(outfile, 'w+') as fout:
        while True:
            try:
                # By using the timeout, we are adding some sleep to this thread.
                next_page_obj = output_data.get(timeout=2)
                text_output = process_indeed_page_data(next_page_obj)
                if verbosity > 0:
                    print("Writing data to output file.")
                fout.write(text_output)
            except:
                if verbosity > 0:
                    print("No data in queue.  Verify that threads are still running.")

                # If we failed, then see if there are any processes
                # still running.  This could be part of the loop, but
                # putting it here will ensure that we are trying to clear
                # out the data queue first.
                if not are_threads_still_running():
                    break


def are_threads_still_running():
    global verbosity, list_of_futures
    tmp_future = None

    if verbosity > 2:
        print("Start are_threads_still_running")

    # We will check until we find a future which is still running.
    # Then put it back, and return the result.
    while not list_of_futures.empty():
        tmp_future = None
        try:
            tmp_future = list_of_futures.get(timeout=5)
        except:
            # The queue was busy, come back later.
            break

        # Print out any exceptions, if the thread is done.
        if tmp_future.done():
            tmp_exceptions = tmp_future.exception()
            if tmp_exceptions is not None:
                # Do this funny trick to print out the stack trace from the thread.
                try:
                    raise tmp_exceptions
                except Exception:
                    print()
                    print("TREAD EXCEPTION: " + traceback.format_exc())
                    print()

        # If the thread is not done, then just put it back onto the stack
        else:
            list_of_futures.put(tmp_future)
            break

    # If we still have futures in the queue,
    # then we still have running threads.
    return not list_of_futures.empty()


def process_indeed_page_data(soup_obj):
    global verbosity
    if verbosity > 2:
        print("Starting process_indeed_page_data")

    data_to_write = ""

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
            for span in sponderedSpans:
                spanText = span.text.lstrip().rstrip()
                if re.match("Sponsored", spanText) is not None:
                    isSponsered = spanText
                    if verbosity > 2:
                        print("####### Found a sponsered item.")

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
        if verbosity > 2:
            print("----------------")
            # Sometimes this fails because of encoding.  Don't quit because of that.
            try:
                if verbosity > 3:
                    print(job)
                    print("################")
                print(jobTitle)
                print(companyName)
                print(jobLocation)
                print(summary)
                print(isSponsered)
                print(jobLinkURL)
            except:
                print("Failed to print all job information.")

        # Now add the data to the output string.
        data_to_write += convert_to_tsv_format(jobTitle, isSponsered,
                                companyName, jobLocation, summary, jobLinkURL)

    return data_to_write


# Covert data to tab separated values, since commas are common.
def convert_to_tsv_format(*data):
    global verbosity
    csv_text = ""

    # If there is data passed in, collate it into the csv format.
    if len(data) > 0:
        for datum in data:
            csv_text += "\t" + str(datum)

        # The loop above will add a ',' to the start of the line.  Remove it.
        csv_text = csv_text[1:]

    # else:
    # if there was no data passed in, we will just return an empty string.

    # Add a carrage return to the end of the line.
    csv_text += "\n"

    if verbosity > 3:
        try:
            print("Data: " + csv_text)
        except:
            print("Failed to print data for job.")

    return csv_text


def parse_args():
    global verbosity, output_file, input_file, workers

    parser = argparse.ArgumentParser(
        description="Scraps jobs from the indeed.com website.")

    parser.add_argument('-i', '--infile',
        help="List of URLs separated by new lines.",
        default=input_file)

    parser.add_argument('-o', '--outfile',
        help="Place to store the results of the scrap.",
        default=output_file)

    parser.add_argument('-w', '--workers',
        help="The number of threads to use for finding jobs.",
        type=int, default=workers)

    parser.add_argument('-v', '--verbose',
        help="Verbosity.  More v's more verbose.",
        action='count', default=verbosity)

    # Parse the command line arguments to see what we got.
    args = parser.parse_args()

    # Update the global values.  The args default to the global values.
    # So if nothing is passed in, then go back to their original values.
    verbosity = args.verbose
    input_file = args.infile
    output_file = args.outfile
    workers = args.workers

    if verbosity > 0:
        print()
        print("Verbosity level set to: " + str(verbosity))
        print("Input file set to: " + input_file)
        print("Output file set to: " + output_file)
        print("Number of workers: " + str(workers))
        print()

    #TODO put more error checking here for other values.  Right now I trust the user.
    if workers < 1:
        raise ValueError('Number of Workers must be greater that 0!')


if __name__ == "__main__":
    # execute only if run as a script
    main()
