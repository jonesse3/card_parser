# card_parser



## Validation Criteria

## Software Installation

You will need at least Python 3.7. 

Pytesseract

Poppler

## How to Use

`python card_parser.py -dir path/to/directory -vaccine path/to/file -config path/to/file`

Example:

`python card_parser.py -dir test_images -vaccine who_approved_vaccines.xlsx -config config.json`

## Example with test images

## Limitations and Future Work

The main limitation of this tool is that it performs poorly on extracting text from handwritten images.   

As of now, this tool does not handle HEIC files. Further work is needed to convert HEIC to JPEG. 
