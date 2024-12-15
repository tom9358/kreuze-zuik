# from PyPDF2 import PdfReader
# import os

# def extract_text_from_pdfs():
#     for filename in os.listdir():
#         if filename.endswith('.pdf'):
#             txt_filename = filename.replace('.pdf', '.txt')
#             try:
#                 with open(txt_filename, 'w', encoding='utf-8') as txt_file:
#                     reader = PdfReader(filename)
#                     for page in reader.pages:
#                         txt_file.write(page.extract_text() + '\n')
#                 print(f"Done with {filename}")
#             except Exception as e:
#                 print(f"Error reading {filename}: {e}")

# # Run the extraction
# extract_text_from_pdfs()
# print("Extraction complete.")

# import os
# import fitz  # PyMuPDF

# def extract_text_from_pdfs():
#     # Loop through all PDF files in the current directory
#     for filename in os.listdir():
#         if filename.endswith('.pdf'):
#             txt_filename = filename.replace('.pdf', '.txt')
#             try:
#                 # Open the PDF file with PyMuPDF
#                 doc = fitz.open(filename)
                
#                 # Open the corresponding text file for writing
#                 with open(txt_filename, 'w', encoding='utf-8') as txt_file:
#                     # Loop through each page of the PDF
#                     for page_num in range(doc.page_count):
#                         page = doc.load_page(page_num)
#                         # Extract the text in block format (better for preserving structure)
#                         blocks = page.get_text("blocks")
                        
#                         # Write the text from each block to the text file
#                         for block in blocks:
#                             txt_file.write(block[4].strip() + '\n')  # block[4] is the text of the block
#                         print(f"{filename}\t{blocks[0][4][:80]}")
                        
#                     # print(f"Done with {filename}")
            
#             except Exception as e:
#                 print(f"Error reading {filename}: {e}")

# # Run the extraction
# extract_text_from_pdfs()
# print("Extraction complete.")

# import os
# import json
# from pdfminer.high_level import extract_text

# def aggregate_text_to_json(output_file):
#     """
#     Aggregates text from all PDFs in a folder into a JSON file.
#     The JSON structure maps each PDF filename to a list of page contents.
#     """
#     aggregated_data = {}
    
#     for filename in os.listdir():
#         if filename.endswith('.pdf'):
#             try:
#                 # Use pdfminer.six to extract text page by page
#                 text = extract_text(filename)
#                 pages = text.split('\f')  # '\f' is the page delimiter
#                 aggregated_data[filename] = [page.strip() for page in pages if page.strip()]
#                 print(f"Successfully processed {filename}")
#             except Exception as e:
#                 print(f"Error reading {filename}: {e}")
    
#     # Save aggregated data to JSON
#     with open(output_file, 'w', encoding='utf-8') as output:
#         json.dump(aggregated_data, output, ensure_ascii=False, indent=4)

# # Example usage
# output_file = "aggregated_text_kreuze.json"  # Output JSON file
# aggregate_text_to_json(output_file)

import os
import json
from pdfminer.high_level import extract_text # forget PyPDF2 or PyMuPDF / fitz,
from pdfminer.pdfpage import PDFPage # pdfminer.six is where it's at!!

def aggregate_text_to_json(output_file):
    """
    Aggregates text from PDFs into a JSON structure:
    {
        "file.pdf": [
            {"page_number": 1, "content": "Page 1 text"},
            {"page_number": 2, "content": "Page 2 text"}
        ]
    }
    """
    aggregated_data = {}

    for filename in os.listdir():
        if filename.endswith('.pdf'):
            try:
                # Initialize JSON entry for this file
                aggregated_data[filename] = []
                
                # Page-specific extraction
                with open(filename, 'rb') as pdf_file:
                    for page_number, page in enumerate(PDFPage.get_pages(pdf_file), start=1):

                        text = extract_text(filename, page_numbers=[page_number - 1])
                        if text.strip():  # Add non-empty pages
                            aggregated_data[filename].append({
                                "page_number": page_number,
                                "content": text.strip()
                            })

                print(f"Processed {filename} successfully.")
            except Exception as e:
                print(f"Error processing {filename}: {e}")

    # Save the JSON structure
    with open(output_file, 'w', encoding='utf-8') as output:
        json.dump(aggregated_data, output, ensure_ascii=False, indent=4)

# Example usage
output_file = "aggregated_text.json"
aggregate_text_to_json(output_file)
