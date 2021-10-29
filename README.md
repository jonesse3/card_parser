# card_parser
## About this tool
This pipeline generates a data frame containing data extracted from images of COVID-19 Vaccine cards and similar documentation. It uses optical character recognition (OCR) to read typed text from images, then the text is searched for data of interest. Cards are assessed as valid or not valid based on whether extracted data is sufficient in quality and quantity. Issues retrieving data result in error flags and empty data entries.

## Validation Criteria
Validity of card data extraction was assessed through meeting the following requirements:
  * Achieve a fuzzy match score of at least 0.8 to one of the terms "COVID-19 Vaccination" or "COVID-19 Vaccine"
  * Meet 2 out of the 3 data criteria:
    - Has at least one dose date
    - Has manufacturer
    - Has at least one lot number

## Software Installation

You will need at least Python 3.7. 

Pytesseract

Poppler

## How to Use

`python card_parser.py -dir path/to/directory -vaccine path/to/file -config path/to/file`

Example:

`python card_parser.py -dir test_images -vaccine who_approved_vaccines.xlsx -config config.json`

## Example with test images

## Limitations:
* This tool only works for typed, English text.
* This tool does not currently handle HEIC or PDF files, but support for both file types is in progress.
* This tool was optimized for US CDC COVID-19 Vaccination cards and may not perform as well for other vaccine documentation (such as international cards or medical records).
* Only one manufacturer is selected from this tool, so it will not accurately capture documentation for vaccines with doses from different manufacturers.
* Multiple delimiters for dates are accepted but the order needs to be month, day, year to be captured by this tool.

## Future directions:
* Additional file support (PDF and HEIC) in development
