import csv
from utils import Donor

file_path = "dataset.tsv"
def read_tsv(file_path=file_path, delimiter='\t', quotechar=None):
    """
    Reads data from a TSV (Tab Separated Values) file and returns a list of lists,
    where each inner list represents a row in the TSV file.

    Args:
        file_path (str): The path to the TSV file.
        delimiter (str, optional): The delimiter used in the TSV file. Defaults to '\t'.
        quotechar (str, optional): The quote character used in the TSV file. Defaults to None.

    Returns:
        list: A list of lists representing the parsed TSV data, or None if an error occurs.
    """
    try:
        with open(file_path, 'r', newline='', encoding='utf-8') as tsvfile:
            reader = csv.reader(tsvfile, delimiter=delimiter, quotechar=quotechar)
            data = list(reader)
            return data
    except FileNotFoundError:
        print(f"Error: File not found at {file_path}")
        return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

def read_donors():
    parsed_data = read_tsv()

    attributes = parsed_data[0] # First line
    donors = []

    for id, row in enumerate(parsed_data):
        if row is attributes:
            continue

        donor = Donor(id, attributes, row)
        donors.append(donor)

    return (attributes, donors)
