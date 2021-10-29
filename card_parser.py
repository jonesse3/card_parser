"""
Purpose: This script reads in a directory of vaccine cards, extracts text from each card, and generates a csv file containing relevant information from the card. Based on the information pulled, a card is considered valid if it meets certain criteria.
"""
#############
# Packages
#############
from PIL import Image
import pytesseract
from pdf2image import convert_from_path
from io import BytesIO
import json
import cv2
import pdfplumber
import numpy as np
import pandas as pd
import argparse
import sys
import re
import os
import warnings
from dateutil.parser import parse
from datetime import datetime
from fuzzywuzzy import fuzz, process

warnings.filterwarnings("ignore")
#############
# Functions
#############

#check if filepath exists and return valid filepath
def check_path(filepath):
    """
    Check if filepath exists.

    Args: filepath (string) - path to file

    Returns: filepath
    """
    if os.path.exists(filepath):
        return filepath
    else:
        print("{} does not exist.".format(filepath))
        sys.exit()

def clean_dates(date_list):
    """
    Clean dates and convert to same format.

    Args: date_list (list) - list of possible dates

    Returns: new_date_list (list)
    """
    new_date_list  = []
    for i in range(len(date_list)):
        # replace any characters that can't be parsed
        date_txt = re.sub('[|]', '/', date_list[i])
        # remove extra spaces
        date_txt = re.sub(r' [/-] ', '/', date_txt)
        try:
            # parse text to get date
            new_date = parse(date_txt)
            final_date = new_date.date().strftime("%m/%d/%Y")
            new_date_list.append(final_date)
        except:
            pass
    return new_date_list

def get_best_score(img_text, word_list, score=80):
    """
    Get term with highest fuzzy matched score.

    Args: img_text (string) - text extracted from image
          word_list (list) - list of words for matching
          score (int) - minimum threshold for matching score

    Returns: best_word (string)
    """
    # create dictionary to hold scores
    scores = dict()

    # try different fuzzy matching scorers and save to scores dictionary
    token_set_ratio = process.extractOne(img_text, word_list, scorer = fuzz.token_set_ratio)
    scores["token_set_ratio"] = {}
    scores["token_set_ratio"]["name"] = token_set_ratio[0]
    scores["token_set_ratio"]["score"] = token_set_ratio[1]

    default_ratio = process.extractOne(img_text, word_list)
    scores["default_ratio"] = {}
    scores["default_ratio"]["name"] = default_ratio[0]
    scores["default_ratio"]["score"] = default_ratio[1]

    partial_ratio = process.extractOne(img_text, word_list, scorer = fuzz.partial_ratio)
    scores["partial_ratio"] = {}
    scores["partial_ratio"]["name"] = partial_ratio[0]
    scores["partial_ratio"]["score"] = partial_ratio[1]

    # get max score
    max_score = max([val.get("score") for val in scores.values()])
    #print(max_score)
    if max_score >= score:
        # add manufacturer to list
        best_word = [val.get("name") for val in scores.values() if val.get("score") == max_score][0]
    else:
        # add empty string
        best_word = ""
    return best_word

#############
# Main program
#############
def main(args):

    # read in arguments
    img_folder = check_path(args.dir)
    vax_file = check_path(args.vaccine)
    config_file = check_path(args.config)

    error = False

    try:
        # read in json file
        with open(config_file) as f:
            data = json.load(f)
        # path to poppler
        path_to_poppler = data["poppler_path"]
        # path to pytesseract
        path_to_pytesseract = data["pytesseract_path"]
    except:
        print("JSON file is not in correct format.")
        sys.exit(1)

    pytesseract.pytesseract.tesseract_cmd = path_to_pytesseract

    # create list for covid vaccine words
    cov_words_list = ["COVID-19 Vaccination Record","COVID-19 Vaccine"]

    # read in vaccine file and get list of vaccines
    vaccine_list = pd.read_excel(vax_file)["vaccine_key_terms"].tolist()

    # create a dictionary from the vaccine file
    vaccine_dict = pd.read_excel(vax_file).set_index("vaccine_key_terms").to_dict()

    # get start time
    start = datetime.now()

    total_files = 0 # number of files in folder
    total_valid = 0

    if os.path.isdir(img_folder):
        filenames = [] # list for image file names
        ids = [] # list for ids
        covid_words = [] # list for tracking if covid vax words are present
        manufacturer = [] # list for manufacturers
        lots = [] # list for lot numbers
        dates = [] # list for dates
        flags = [] # list for flags

        i = 0 # track number of files
        #loop through each file
        for file in os.listdir(img_folder):
            total_files += 1
            i += 1
            if i%10 == 0:
                print("{} files processed.".format(i))

            # add file names and ids for all files
            filenames.append(file)
            # id at the start of file name
            ids.append(file.split("_",1)[0])

            try:
                if file.lower().endswith("pdf"):
                    with pdfplumber.open(os.path.join(img_folder,file)) as pdf:
                        first_page = pdf.pages[0]
                        text = first_page.extract_text()
                else:
                    try:
                        text = pytesseract.image_to_string(Image.open(os.path.join(img_folder,file)))
                    except TesseractNotFoundError:
                        error = True
                        print("Path to pytesseract not recognized.")
                        break
                    except:
                        pass
            except:
                covid_words.append("no")
                dates.append([])
                flags.append("File could not be read")
                manufacturer.append("")
                lots.append([])
            else:
                # check if text contains key words for COVID vaccine
                if text:
                    vaxwords = get_best_score(text, cov_words_list, score=80)

                # if text doesn't contain key words, convert PDF to image
                if not text or not vaxwords and file.lower().endswith("pdf"):
                    try:
                        # store pdf with convert_from_path function
                        pdf_img = convert_from_path(os.path.join(img_folder,file), poppler_path = path_to_poppler)
                    except:
                        error = True
                        print("Path to poppler not recognized.")
                        break
                    else:
                        with BytesIO() as f:
                            pdf_img[0].save(f, format="jpeg") # get first page
                            f.seek(0)
                            try:
                                text = pytesseract.image_to_string(Image.open(f))
                            except TesseractNotFoundError:
                                error = True
                                print("Path to pytesseract not recognized.")
                                break
                        vaxwords = get_best_score(text, cov_words_list, score=80)

                if vaxwords:
                    covid_words.append("yes")

                    # extract manufacturer using best score from list of approved vaccines
                    manufacturer.append(get_best_score(text, vaccine_list, score=80))

                    # extract dates using regex
                    found_dates = re.findall('(?<=\s)(\d+\s*[-\/|]\s*\d+\s*[-\/|]\s*\d*2[0|1]|[0-9]*\s*(?:Jan(?:uary)?|Feb(?:ruary)?|Mar(?:ch)?|Apr(?:il)?|May|Jun(?:e)?|Jul(?:y)?|Aug(?:ust)?|Sep(?:tember)?|Sept|Oct(?:ober)?|Nov(?:ember)?|Dec(?:ember)?).+20*[^0|1]2*[0|1])', text)

                    # clean dates
                    dates.append(clean_dates(found_dates))

                    # leave flags blank
                    flags.append("")

                    # extract lot numbers
                    found_lots = re.findall('([0-9]{3}[A-Z][0-9]{2}[A-Z]|E[A-Z][0-9]{4}|A[0-9]{5})', text)
                    lots.append(found_lots)
                else:
                    covid_words.append("no")
                    dates.append([])
                    manufacturer.append("")
                    lots.append([])
                    flags.append("COVID-19 Vaccination Record phrase not found")
    else:
        print("Not valid directory.")
        sys.exit(1)
    if error:
        sys.exit(1)

    # create a zipped list of tuples from above lists
    card_data = list(zip(filenames, ids, covid_words, dates, manufacturer, lots, flags))

    # convert to dataframe
    df = pd.DataFrame(card_data, columns = ["filename","hhs_id","has_covid_words","vax_dates","manufacturer", "lot_numbers","flags"])

    # add columns
    df["has_at_least_one_lot_number"] = df["lot_numbers"].apply(lambda x: 1 if len(x) > 0 else 0)
    df["has_manufacturer"] = df["manufacturer"].apply(lambda x: 0 if not x else 1)
    df = df.replace({"manufacturer": vaccine_dict})
    df["has_at_least_one_date"] = df["vax_dates"].apply(lambda x: 1 if len(x) > 0 else 0)
    df["number_valid_checks"] = df["has_manufacturer"] + df["has_at_least_one_date"] + df["has_at_least_one_lot_number"]
    df["valid"] = np.where((df["has_covid_words"] == "yes") & (df["number_valid_checks"] >= 2), 1, 0)

    total_valid = df["valid"].sum()
    print("Number of files in directory: {}". format(total_files))
    print("Number of files with at least a valid card: {}". format(total_valid))

    # get time it took to run program
    print("Finished in {}".format(datetime.now()-start))

    # save file
    name_of_file = "vaccine_data.csv"
    df.to_csv(os.path.join(img_folder, name_of_file), index = False)

if __name__ == "__main__":

    # create arguments
    p = argparse.ArgumentParser(description=__doc__, prog = "card_parser.py",
        usage = "%(prog)s -dir <path/to/directory> -config <path/to/file> -vaccine <path/to/file>", add_help = True)

    p.add_argument("-dir", help = "directory containing vaccine cards", required = True)
    p.add_argument("-config", help = "json file containing full paths to pytesseract and poppler", required = True)
    p.add_argument("-vaccine", help = "csv file containing WHO approved vaccines", required = True)

    # parse arguments
    args = p.parse_args()
    # run program with arguments
    main(args)
