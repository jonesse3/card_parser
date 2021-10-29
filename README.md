# card_parser

The purpose of this tool is to extract text from vaccine cards and generate a CSV file containing relevant information from the card. 

## Validation Criteria

A card is considered valid if it meets the following:

1. Contains the phrase "COVID-19 Vaccination" AND
2. Has at least 2 out of the 3 criteria:
 * Has at least one dose date
 * Has a manufacturer
 * Has at least one lot number

## Software Installation

You will need at least Python 3.7 to use this tool. 

Pytesseract

Poppler

## How to Use

`python card_parser.py -dir path/to/directory -vaccine path/to/file -config path/to/file`

Example:

`python card_parser.py -dir test_images -vaccine who_approved_vaccines.xlsx -config config.json`

Parameters:

-dir: directory containing vaccine card images
-vaccine: CSV file containing WHO approved vaccines
-config: JSON file containing full paths to Poppler and Pytesseract

## Example with test images

## Limitations and Future Work

The main limitation of this tool is that it performs poorly on extracting text from handwritten images.   

As of now, this tool does not handle HEIC files. Further work is needed to convert HEIC to JPEG. 
