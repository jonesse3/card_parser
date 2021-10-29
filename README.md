# card_parser

## Description of the tool:

This tool generates a .csv containing data extracted from images of COVID-19 Vaccine cards and similar documentation. It uses optical character recognition (OCR) to read typed text from images, then the text is searched for [data of interest](##-Description-of-CSV-output-file). Cards are assessed as valid or not valid based on [criteria](##-Validation-Criteria) for whether extracted data is sufficient in quality and quantity. Issues retrieving data result in [error flags](##-Description-of-CSV-output-file) and empty data entries. This tool only works for typed, English text and has several other [limitations](##-Limitations). Several of these are currently [being addressed](##-Future directions). 

## Validation Criteria

A card is considered valid if it meets the following:

1. Contains the phrase "COVID-19 Vaccination Record" or "COVID-19 Vaccine" **AND**
2. Has at least 2 out of the 3 criteria:
   * Has at least one dose date (dates are expected to be in month day year format)
   * Has a manufacturer
   * Has at least one lot number

## Software Installation

You will need at least Python 3.7 and the packages listed in *requirements.txt*.

To install the packages using *requirements.txt*, run the following command:

`pip install -r requirements.txt`

In addition, you will also need to install poppler for converting PDFs to images and pytesseract for object character recognition (OCR). 

The following instructions are for installing poppler and pytesseract on a Windows computer.

**Pytesseract**

Go to https://github.com/UB-Mannheim/tesseract/wiki and download *tesseract-ocr-w64-setup-v5.0.0-alpha.20210811.exe*. 
Double-click the .exe file and follow the instructions to install the software.

**Poppler**

Go to https://github.com/oschwartz10612/poppler-windows/releases/ and download and unzip *Release-21.10.0-0.zip*.

Next, download the code for this tool using the following command:

`git clone https://github.com/lisa-mml/card_parser.git`

Once pytesseract and poppler are installed, change the paths to pytesseract and poppler to the paths on your computer in the *config.json* file.

## How to Use

`python card_parser.py -dir path/to/directory -vaccine path/to/file -config path/to/file`

Example:

`python card_parser.py -dir test_images -vaccine who_approved_vaccines.xlsx -config config.json`

Parameters:

 * *dir*: directory containing vaccine card images
 * *vaccine*: EXCEL file containing WHO approved vaccines
 * *config*: JSON file containing full paths to Poppler and Pytesseract

## Description of CSV output file

| Variable  | Data type | Description
| ----------| ----------| -----------|
| filename  | string  | name of file |
| hhs_id  | string | individual's ID number |
| has_covid_words | string | *yes*  or *no*; Does card have the phrase "COVID-19 Vaccination Record" or "COVID-19 Vaccine"? |
| vax_dates | list of strings | any date from 2020 and 2021 |
| manufacturer | string | vaccine manufacturer (i.e. *Pfizer*) |
| lot_numbers | list of strings | lot number | 
| flags | string | message related to processing of the file (i.e. *File could not be read*) |
| has_at_least_one_lot_number | integer | 1 if yes, 0 if no |
| has_manufacturer | integer | 1 if yes, 0 if no |
| has_at_least_one_date | integer | 1 if yes, 0 if no |
| number_valid_checks | integer | 0 to 3; sum of the values of the previous 3 variables |
| valid | integer | 1 if yes, 0 if no; card has "yes" for has_covid_words and at least 2 out of the 3 criteria met |

## Example with test images

We have provided the following images in the *test_images* folder for testing the tool. 

![Image 1](/test_images/255555_vaccine_card.PNG)

PHOTOGRAPH: CARLOS AVILA GONZALEZ/SAN FRANCISCO CHRONICLE/GETTY IMAGES

![Image 2](/test_images/24444_vaccine_card.jpg)

PHOTOGRAPH: MELISSA PHILLIP/HOUSTON CHRONICLE

An example of the CSV output is provided for the above two images: *example_vaccine_data.csv*

## Limitations:
* This tool only works for typed, English text.
* This tool does not currently handle HEIC or PDF files, but support for both file types is in progress.
* Card orientation may be a problem. We did not include a step to check the orientation of the card before extracting the text, though this is something that can be added.
* This tool was optimized for US CDC COVID-19 Vaccination cards and may not perform as well for other vaccine documentation (such as international cards or medical records).
* Only one manufacturer is selected from this tool, so it will not accurately capture documentation for vaccines with doses from different manufacturers.
* Multiple delimiters for dates are accepted but the order needs to be month, day, year to be captured by this tool.

## Future directions:
* Additional file support (PDF and HEIC) in development.
* Card orientation verification and improvement is in development.
* The main limitation of this tool is that it performs poorly on extracting text from handwritten images. Utilizing services such as Google's Google Cloud Vision API, Microsoft's Azure Computer Vision API, and Amazon's Textract and Rekognition will improve the performance of this tool on handwritten images.
