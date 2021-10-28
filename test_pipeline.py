#############
# This notebook tests functions and pipelines from pipeline_draft script with card images in a local directory. 
# Prerequisities: Python 3, required packages and executables (see documentation)  
# Throughout: replace  'your_filepath' with the actual file path needed for your device.
#############

#############
#read in packages
#############
from PIL import Image
import pytesseract
pytesseract.pytesseract.tesseract_cmd = r'your_filepath\tesseract\tesseract.exe'

import cv2
from matplotlib import pyplot as plt
get_ipython().run_line_magic('matplotlib', 'inline')
import pdfplumber

#import packages for data extraction
import numpy as np
import pandas as pd
import argparse
import sys
import re
import os
from fuzzywuzzy import fuzz, process


#############
#set functions and other pieces
#############

#check if filepath exists and return valid filepath
def check_path(filepath):
    if os.path.exists(filepath):
        return filepath
    else:
        print("{} does not exist.".format(filepath))
        sys.exit()


#search for dates with regular expressions 
#for now, pieces of this typed into pipeline, but could use separate function instead if needed
def short_dates(card_text):
    dates=[]
    found=re.findall('(\d+[-\/|]\d+[-\/|]\d+)',card_text)
    dates.append(found)
    return(dates)
#this date format catches 00/00/00, 00-00-00, 00|00|00, mixed delimiters, four digit years, different m/d/y orders


# make function to extract manufacturer with the highest fuzzy matched score
# args: img_text = text string from image
#       manuf_list = list of manufacturers (previously read in from .xlsx)
def get_manufact(img_text,manuf_list):
    # create dictionary to hold scores
    scores = dict()

    # try different fuzzy matching scorers and save to scores dictionary
    token_set_ratio = process.extractOne(img_text, manuf_list, scorer = fuzz.token_set_ratio)
    scores["token_set_ratio"] = {}
    scores["token_set_ratio"]["name"] = token_set_ratio[0]
    scores["token_set_ratio"]["score"] = token_set_ratio[1]

    default_ratio = process.extractOne(img_text, manuf_list)
    scores["default_ratio"] = {}
    scores["default_ratio"]["name"] = default_ratio[0]
    scores["default_ratio"]["score"] = default_ratio[1]

    partial_ratio = process.extractOne(img_text, manuf_list, scorer = fuzz.partial_ratio)
    scores["partial_ratio"] = {}
    scores["partial_ratio"]["name"] = partial_ratio[0]
    scores["partial_ratio"]["score"] = partial_ratio[1]

    #print(scores)    
    # get max score
    max_score = max([val.get("score") for val in scores.values()])
    #print(max_score)
    if max_score >= 80:
        # add manufacturer to list
        manufacturer=[val.get("name") for val in scores.values() if val.get("score") == max_score][0]
    else:
        # add N/A to list
        manufacturer=""
    return(manufacturer)


#set up fuzzymatching for covid words
# args: img_text text from image file
#       cov_words_list list of key words for covid vaccine verification
def get_covwords(img_text,cov_words_list):
    # create dictionary to hold scores
    scores = dict()

    # try different fuzzy matching scorers and save to scores dictionary
    token_set_ratio = process.extractOne(img_text, cov_words_list, scorer = fuzz.token_set_ratio)
    scores["token_set_ratio"] = {}
    scores["token_set_ratio"]["name"] = token_set_ratio[0]
    scores["token_set_ratio"]["score"] = token_set_ratio[1]

    default_ratio = process.extractOne(img_text, cov_words_list)
    scores["default_ratio"] = {}
    scores["default_ratio"]["name"] = default_ratio[0]
    scores["default_ratio"]["score"] = default_ratio[1]

    partial_ratio = process.extractOne(img_text, cov_words_list, scorer = fuzz.partial_ratio)
    scores["partial_ratio"] = {}
    scores["partial_ratio"]["name"] = partial_ratio[0]
    scores["partial_ratio"]["score"] = partial_ratio[1]

    #print(scores)    
    # get max score
    max_score = max([val.get("score") for val in scores.values()])
    #print(max_score)
    if max_score >= 80:
        # assume card contains covid vaccine info
        cov_words=True
    else:
        # add N/A to list
        cov_words=False
    return(cov_words)



#############
# Establish pipeline that makes output dataframe with image file names + extracted contents.
# args: imagepath = path for folder containing image files
#       manuf_list = list of manufacturers from vaccine list spreadsheet
#############
def df_from_imgs(imagepath,manuf_list,cov_words_list):
    total_files = 0 # number of files in folder
    total_valid = 0 
    
    if os.path.isdir(imagepath):
        filenames=[] #list for image file names
        ids=[] #list for hhs ids
        covid_words=[] #list for covid vax words present
        manufacturer=[] #list for manufacturers
        lots=[] #list for lot numbers
        dates=[] #list for dates
        flags=[] #list for flags
       
            #loop through each file and do stuff
        for file in os.listdir(imagepath):
            total_files += 1
            
            #add file names and ids for all files, regardless of if we can pull data
            filenames.append(file)
            ids.append(file.split('_',1)[0]) #change based on actual delim
            
            try:
                img=cv2.imread(os.path.join(imagepath,file))
                text=pytesseract.image_to_string(img)

            except: 
                covid_words.append("no")
                dates.append([])
                flags.append("file_could_not_be_read")
                manufacturer.append([])
                lots.append([])

            else:
                #print(text)
              #check if text contains key words for covid vax validity
                vaxwords=get_covwords(text,cov_words_list)

                if vaxwords:
                    covid_words.append("yes")
                    total_valid +=1

                    #extract manufacturer text using function made earlier
                    #matches text manufacturer to list of approved vaccines
                    manufacturer.append(get_manufact(text,manuf_list))

                    #extract dates using regex
                    found_dates=re.findall('(\d+\s*[\-\/\|\\\]\s*\d+\s*[\-\/\|\\\]\s*\d+)',text)
                    dates.append(found_dates)
                    
                    #leave flags blank
                    flags.append("")
                    
                    #extract lot numbers
                    found_lots=re.findall('((Lot|ER|EW)+\s*[#:]*\s*[A-Z0-9]{4,})',text)
                    lots.append(found_lots)
                    
                else:
                    covid_words.append("no")
                    
                    #add empty strings and flags since data not read
                    dates.append([])
                    manufacturer.append([])
                    lots.append([])
                    flags.append("covid_vax_phrase_not_found")
                
    else:
        print("Not valid directory.")
        sys.exit()
    print("Number of files in directory: {}". format(total_files))
    print("Number of files with at least a valid card: {}". format(total_valid))
    
    # create a zipped list of tuples from above lists
    data = list(zip(filenames, ids, covid_words, dates, manufacturer, lots, flags))

    # convert to dataframe
    df = pd.DataFrame(data, columns = ["filename","hhs_id","covid_words","vax_dates","manufacturer", "lot_numbers","flags"])

    return df  

#############
# make/read in lists to check against
############

# read in file and get list of vaccines
# this list can be downloaded from github
vax_list = pd.read_excel("your_filepath/who_approved_vaccines.xlsx")["vaccines"].tolist()

#create list for covid vaccine words
covid_words=["COVID-19 Vaccination","COVID-19 Vaccine"]

#############
# Execute pipeline on folder of images.
# reminder: "images" is the name of the folder containing images
#            vax_list has the list of vaccines approved by WHO and imported from the spreadsheet
#            covid_words are the key words for covid vaccination made earlier in the script
#############
df_from_imgs("images",vax_list,covid_words)
