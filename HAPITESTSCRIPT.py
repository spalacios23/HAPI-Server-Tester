#Simple Command Line Arg script for testing a random dataset&parameter given a HAPI url
import sys
import requests
import json
import urllib.request
from urllib.request import urlopen
import random
import pandas as pd
import datetime
from datetime import timedelta
import ssl
import certifi


import time

import csv


from hapiclient import hapi


from hapiplot import hapiplot

# set up special matplotlib plotting requirements

















#declaring variables and defining functions

finalLog = ['**********************************', 'RESULTS:']

exceptLog = ['**********************************', 'ERRORS:']

servers    = ['http://hapi-server.org/servers/SSCWeb/hapi',
 'https://cdaweb.gsfc.nasa.gov/hapi',
 'http://planet.physics.uiowa.edu/das/das2Server/hapi', 
 'https://iswa.gsfc.nasa.gov/IswaSystemWebApp/hapi',
 'http://lasp.colorado.edu/lisird/hapi',
 'http://hapi-server.org/servers/TestData2.0/hapi',
 'http://amda.irap.omp.eu/service/hapi', 
 'https://vires.services/hapi'
 ]

#error/success color escape codes
class tColors:
    success = '\033[92m'
    fail = '\033[91m'
    endC = '\033[0m'
    
    

#tests the server for a 200 response code
def testHTTPCode(cS):
    x = requests.get(cS) #, verify=False)
    
    if x.status_code == 200:
        print(f"{tColors.success}Server is up!{tColors.endC}")
        
    else:
        print(f"{tColors.fail}ERRROR, BAD HTTP response status code: {tColors.endC}" + "[" + str(x.status_code) + "]")
        


    







#begin testing


def hapiTest(cHS):
    
    #a way to measure process time
    start_time = time.perf_counter ()
    

    #get url from system
    """
    try:
        cHS = sys.argv[1]
        
    except:
        print("URL NOT RECEIVED")
        sys.exit("URL NOT RECEIVED, TERMINATE PROCESS")
    """
    
    #make sure url matches known list of servers
    if cHS in servers:
        print("URL MATCHES KNOWN HAPI SERVER")
            
    else:
        print("URL DOES NOT MATCH KNOWN HAPI SERVER")
        #sys.exit("URL DOES NOT MATCH KNOWN HAPI SERVER, TERMINATE PROCESS")
        
    
    
    #test HTTP code to check for 200 response
    testHTTPCode(cHS)
    
    
    #create the catalog URL
    catalogURL = cHS
    catalogURL += '/catalog'
    
    
    try:
    
        #load all available dataset ids and store them in a python list for further use
            
        serverResponse = urlopen(catalogURL)
        DataSetList = json.loads(serverResponse.read())
        refinedList = DataSetList.get('catalog') #just a note, hapi 2.0 has the 'catalog' key:value item at the top of the json, while 3.0 has it at the bottom. 
            
            #get HAPI version for later use
        hapiVer = DataSetList.get('HAPI')
            
        print(hapiVer)
            
            
            #this actually returns a python list of python dictionaries... hence the .get of the key "id"
            #down below to get its value
                
                
        idList = []
        for i in range(len(refinedList)):
            idList.append(refinedList[i].get('id')) 
                    
                    
        print(idList[0])
        print(idList[-1])
        print(len(refinedList))
        
    except Exception as e:
        
        exceptLog.append(str(e) + " occured on " + cHS + "  process: getting dataset IDs")
        
        
    #get a random dataset ID to choose time/params from the info
    
    randID = random.choice(idList)
    print(randID)
    infoURL = cHS
    #create the info URL
    infoURL += '/info?id=' + randID
    
    
    
    
    #make a list of all available parameters for said dataset (from info url) and choose a random one
    
    try:
    
        #load all available parameter ids and store them in a python list for further use
            
        serverResponse = urlopen(infoURL)
        DataSetList = json.loads(serverResponse.read())
        refinedList = DataSetList.get('parameters') #just a note, hapi 2.0 has the 'catalog' key:value item at the top of the json, while 3.0 has it at the bottom. 
        #this actually returns a python list of python dictionaries... hence the .get of the key "name"
        #down below to get the parameter name
            
            
        pList = []
        for i in range(len(refinedList)):
            pList.append(refinedList[i].get('name')) 
                
                
        print(pList[0])
        print(pList[-1])
        print(len(refinedList))
        
    except Exception as e:
       
        exceptLog.append(str(e) + " occured on " + cHS + "  process: getting parameters")
        
        
        
        
        
    #get a random parameter
    del pList[0] #gets rid of time(no need to plot time)
    randPara = random.choice(pList)
    print(randPara)
    
    #search for the startDate and stopDate within a random dataset. 
    try:
        serverResponse = urlopen(infoURL)
        infoList = json.loads(serverResponse.read())
        startDate = infoList.get('startDate')
        stopDate = infoList.get('stopDate')
        
        print(str(startDate) + '\n' +  str(stopDate))
        
        #convert the ISO 8061 strings to python datetime objects for later random date generation
        #with a special case for different servers that use microseconds and special case for DAS2 and HapiTestServer as they have odd time formats
        
        if cHS == "http://hapi-server.org/servers/TestData2.0/hapi": #special case for Hapi test server
            startDate = datetime.datetime.strptime(startDate,'%Y-%m-%dZ')
            stopDate = datetime.datetime.strptime(stopDate,'%Y-%m-%dZ')
            
        elif cHS == "http://planet.physics.uiowa.edu/das/das2Server/hapi": #special case or Das2 server
            
            if randID == 'Cassini/Ephemeris/Saturn,60s' or randID == 'Cassini/MAG/VectorKSO': #very specific time formatting for these two datasets that has unorthodox time format compared to the rest of the server
                startDate = datetime.datetime.strptime(startDate, "%Y-%m-%dT%H:%M:%S")
                stopDate = datetime.datetime.strptime(stopDate, "%Y-%m-%d")
                
            
                
                
            else:
                startDate = datetime.datetime.strptime(startDate, "%Y-%m-%dT%H:%M:%S")
                stopDate = datetime.datetime.strptime(stopDate, "%Y-%m-%dT%H:%M")
            
        
        elif len(startDate) > 20: #special case for microseconds, checks the length of the ISO time string
            
            startDate = datetime.datetime.strptime(startDate, "%Y-%m-%dT%H:%M:%S.%fZ")
            stopDate = datetime.datetime.strptime(stopDate, "%Y-%m-%dT%H:%M:%S.%fZ")
            
        
            
        else: #case for no microseconds
            startDate = datetime.datetime.strptime(startDate, "%Y-%m-%dT%H:%M:%SZ")
            stopDate = datetime.datetime.strptime(stopDate, "%Y-%m-%dT%H:%M:%SZ")
            
        
        #generate a test "start date" 15 mins before the dataset stopdate, to check if the latest data is all good/parseable (therefore the rest of the data should be ok.) well, maybe...
        k = 15
        testDate = stopDate - timedelta(minutes = k)
    
        print(str(startDate) + '\n' +  str(testDate))
    
    except Exception as e:
        
        exceptLog.append(str(e) + " occured on " + cHS + " process:  getting timestamps")
        
        
    #using the start and stop date, select a random start and stop date within the timeframe for use in sampling (pd dataframe)
    
    
    
        
        
    
        
        
    
        
    
    
    
    
    
    #convert testDate(this is our start date for testing purposes) to ISO Format string(do the same for stopDate(Also a datetime object))
    testStartDate = testDate.isoformat() + 'Z'
    
    testStopDate = stopDate.isoformat() + 'Z'
    
    print(testStartDate)
    print(testStopDate)
    
    
    #create the final random link- with a special case for 2.0 vs 3.0- & only to get CSVs!
    dataEmpty = True #boolean for getting new urls until data has populated 
    testInterval = 60
    increaser = 4
    try:
        
        while dataEmpty:
                    
            if hapiVer == '3.0':
                        
                    
                finalURL = cHS + '/data?id=' + randID + '&parameters=' + randPara + '&start=' + testStartDate + '&stop=' + testStopDate + '&format=csv' #'&include=header'
                    
                print(finalURL)
                        
            if hapiVer == '2.0' or hapiVer == '1.1':
                finalURL = cHS + '/data?id=' + randID + '&parameters=' + randPara + '&time.min=' + testStartDate + '&time.max=' + testStopDate + '&format=csv' #'&include=header'
                    
                print(finalURL)
            
            #load csv file from finalURL
            try:
                
                csvResponse = pd.read_csv(finalURL) #turns it into a pandas dataframe
            except:
                
                csvResponse = []
                
                csvResponse = pd.DataFrame(csvResponse) #makes into an empty dataframe to prevent errors
                

            
            dataRows = csvResponse.shape[0] #this returns the # of rows in the dataframe
            
            
            if dataRows < 2: #2 to avoid tick issue???
                
                print(f"{tColors.fail}No data found... increasing time range{tColors.endC}")
                
                #1 second delay between requests- to not overwhelm servers
                time.sleep(1)
                
                
                testDate = stopDate - timedelta(minutes = testInterval)
                
                testStartDate = testDate.isoformat() + 'Z'
                
                
                
                if testInterval == 3840: #64 hours in mins, if it reaches this point go straight to collecting a years worth of data
                    increaser = 300
                
                #increase the time range by 4x each time, until data is found, if not the exception will catch an out of bounds HAPI error, most likely meaning empty data. 15 mins, 1 hr, 4hr, 16hr, 64hr
                testInterval *= increaser
                
                
                
                
                
            else:
                print(f"{tColors.success}Found Data! On to the plot!{tColors.endC}")
                dataEmpty = False
                
                   
    except Exception as e:
        exceptLog.append(str(e) + " occured on " + finalURL + " process:  loading CSV. Likely empty dataset")
        print(str(e))
    
        
    
        
    
    
    
    #With the random link, check to see if the resulting CSV is parseable! 
    #and if the metadata allows for a good plot using Hapiplot!
    #try:
        
    try:
            
        
            
    
        server     = cHS
        dataset    = randID
        parameters = randPara
        start      = testStartDate
        stop       = testStopDate
        opts       = {'logging': True, 'usecache': True}
            
        data, meta = hapi(server, dataset, parameters, start, stop, **opts)
            
            
        popts = {'useimagecache': False, 'logging': True, 'returnimage': True}
            
        hapiplot(data, meta, **popts)
        # Plot parameter 
            
            
            
        end_time = time.perf_counter ()
            
        finalLog.append(cHS + ' plotted successfully.')
        print(f"{tColors.success}Success!!!!!{tColors.endC}" + " Time: " + str(round((end_time - start_time), 3)) + " seconds") 
            #sys.exit(0)

    except Exception as e:
       
        exceptLog.append(str(e) + " occured on " + finalURL + " process:  plotting data")
        
        
        
        
        print(f"{tColors.fail}HAPI failed to plot on {tColors.endC}" + str(cHS))
        finalLog.append(cHS + '--ERROR')
  


#final notes: some sites have UTC Zulu as :XXX, some have it as .XXX
#also hapi 2.0 uses time.min and time.max to stream data...




"""
  #  http://hapi-server.org/servers/SSCWeb/hapi Yes
   # http://datashop.elasticbeanstalk.com/hapi - SERVER DOWN
   # https://cdaweb.gsfc.nasa.gov/hapi - YES-%100
    #http://planet.physics.uiowa.edu/das/das2Server/hapi No... Dates(.) yet to make a 1.1 url adapter has its own weird outdated time structure. Some datasets work for plotting but not all
   ##https://iswa.gsfc.nasa.gov/IswaSystemWebApp/hapi Yes
   #http://lasp.colorado.edu/lisird/hapi Yes
    #http://hapi-server.org/servers/TestData2.0/hapi NO... Dates (.) #also has its own dates that are a tad too short... unimportant as it is a test site
    http://amda.irap.omp.eu/service/hapi YES- %100 Lol i think I shut it down by lots of tests
    https://vires.services/hapi YES- 100% lets go accomodated for both time types 
"""



    
def main():
    
    test_start_time = time.perf_counter ()
    
    for z in servers:
        hapiTest(z)
    
    for o in finalLog:
        
        print(o)
        
    
    
    test_end_time = time.perf_counter ()
    
    print("Total Test Time: " + str(round((test_end_time - test_start_time), 3)) + " seconds")
    
    #print all exceptions that occured for debugging purposes:
    
    for j in exceptLog:
        print(j)
main()
    
    

#das2 has the data on dataset info ID page?? Works 50% of the time??????

#Just realized.. Das2 streams some of its data from a deprecated server: http://mapsview.engin.umich.edu/
#DAS2 is a mess.. wrap in try errors

#SSC web is plottable 99% of the time... 


    

"""
ERRORS/ISSUES SO FAR:
    1. Some parameter data are strings... like vectorstr on HAPITEST2
    2. Certain parameters have no data for the current 15 minute time sample- implement a dynamic way around this- DONE
    3. Certain servers have non-standard data organization
    4. some servers have no data for the last 8 hours of listed date.. but as soon as you get to its start you are met with LOTS of data- some servers measure by milliseconds, others daily. lol

missing datasets on iswa: RBSP_B_RBSPICE_part_P1M



"""
    
    







    




