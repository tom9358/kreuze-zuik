import os
import json
from pdfminer.high_level import extract_text

def aggregate_text_to_json(output_file):
    """
    Aggregates text from all PDFs in a folder into a JSON file.
    The JSON structure maps each PDF filename to a list of page contents.
    """
    aggregated_data = {}
    
    for filename in os.listdir():
        if filename.endswith('.pdf'):
            try:
                # Use pdfminer.six to extract text page by page
                text = extract_text(filename)
                pages = text.split('\f')  # '\f' is the page delimiter
                aggregated_data[filename] = [page.strip() for page in pages if page.strip()]
                print(f"Successfully processed {filename}")
            except Exception as e:
                print(f"Error reading {filename}: {e}")
    
    # Save aggregated data to JSON
    with open(output_file, 'w', encoding='utf-8') as output:
        json.dump(aggregated_data, output, ensure_ascii=False, indent=0)

# Example usage
output_file = "aggregated_text_kreuze.json"  # Output JSON file
# aggregate_text_to_json(output_file)

# # if we want to keep page numbers:
# import os
# import json
# from pdfminer.high_level import extract_text # forget PyPDF2 or PyMuPDF / fitz,
# from pdfminer.pdfpage import PDFPage # pdfminer.six is where it's at!!

# def aggregate_text_to_json(output_file):
#     """
#     Aggregates text from PDFs into a JSON structure:
#     {
#         "file.pdf": [
#             {"page_number": 1, "content": "Page 1 text"},
#             {"page_number": 2, "content": "Page 2 text"}
#         ]
#     }
#     """
#     aggregated_data = {}

#     for filename in os.listdir():
#         if filename.endswith('.pdf'):
#             try:
#                 # Initialize JSON entry for this file
#                 aggregated_data[filename] = []
                
#                 # Page-specific extraction
#                 with open(filename, 'rb') as pdf_file:
#                     for page_number, page in enumerate(PDFPage.get_pages(pdf_file), start=1):

#                         text = extract_text(filename, page_numbers=[page_number - 1])
#                         if text.strip():  # Add non-empty pages
#                             aggregated_data[filename].append({
#                                 "page_number": page_number,
#                                 "content": text.strip()
#                             })

#                 print(f"Processed {filename} successfully.")
#             except Exception as e:
#                 print(f"Error processing {filename}: {e}")

#     # Save the JSON structure
#     with open(output_file, 'w', encoding='utf-8') as output:
#         json.dump(aggregated_data, output, ensure_ascii=False, indent=0)

# # Example usage
# output_file = "aggregated_text.json"
# aggregate_text_to_json(output_file)


# Now some code to further preprocess the aggregated text into sentences.
import os
import re
import json
from collections import defaultdict

JSON_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'aggregated_text_kreuze.json')
PREPROCESSED_DATA = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'sentences_kreuze.json')

def split_into_sentences(text, max_length=99) -> list:
    """
    Splits text into sentences by detecting sentence-ending punctuation with regex.
    Also splits long chunks.
    """
    # Remove hyphenation
    text = re.sub(r'-\n', '',text)

    # Regex for standard sentence delimiters
    sentence_endings = re.compile(r'(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<![A-Z]\.)(?<=\.|\?|\!)\s')
    raw_sentences = sentence_endings.split(text)
    
    sentences = []
    for sentence in raw_sentences:
        sentence = sentence.strip()
        if len(sentence) > max_length:
            # Split long "sentences" further on capital letters after spaces
            long_sentence_split = re.split(r'(?<=\s)(?=[A-Z])', sentence)
            for sub_sentence in long_sentence_split:
                if sub_sentence.strip():
                    sentences.append(sub_sentence.strip())
        else:
            if sentence:
                sentences.append(sentence)
    
    return sentences

def preprocess_aggregated_data():
    """
    Preprocess the aggregated text by splitting into sentences and saving to a new file.
    """
    with open(JSON_FILE, 'r', encoding='utf-8') as file:
        aggregated_data = json.load(file)

    preprocessed_data = defaultdict(list)

    for filename, pages in aggregated_data.items():
        print(f'preprocessing {filename}')
        for page_content in pages:
            sentences = split_into_sentences(page_content)
            preprocessed_data[filename].extend(sentences)
    
    # Save preprocessed data
    with open(PREPROCESSED_DATA, 'w', encoding='utf-8') as file:
        json.dump(preprocessed_data, file, ensure_ascii=False, indent=0)
    print(f"Preprocessed data saved to {PREPROCESSED_DATA}")

# Preprocess and save
# preprocess_aggregated_data()

# Now we can use the preprocessed sentences to create a wordlist with frequency data.

import os
import json
from collections import Counter, defaultdict
from tokenizers.pre_tokenizers import Whitespace, Punctuation
from tokenizers.pre_tokenizers import Sequence

# Define the file paths
PREPROCESSED_DATA = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'sentences_kreuze.json')
OUTPUT_WORDLIST = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'kreuze_freq_wordlist.txt')

pre_tokenizer = Sequence([Whitespace(), Punctuation()])

def tokenize(sentence: str) -> list[str]:
    return [tok[0] for tok in pre_tokenizer.pre_tokenize_str(sentence)]

def pass_check(word: str, count: int) -> bool: # seems to have a VERY good quality/complexity ratio
    if count < 3: return False
    # Let's only permit alphanumeric characters:
    if any(not char.isalpha() for char in word):
        return False
    for char in 'åõüāēōšôûîâÅÕÜĀĒŌŠÔÛÎÂíéáúñçßÍÉÁÚÑÇẞ':
        if char in word: return False
    return True

def create_wordlist_from_sentences() -> None:
    """
    Creates a wordlist with frequency data from preprocessed sentences.
    """
    word_counter = Counter()

    with open(PREPROCESSED_DATA, 'r', encoding='utf-8') as file:
        preprocessed_data = json.load(file)

    for _, sentences in preprocessed_data.items():
        for sentence in sentences:
            words = tokenize(sentence)
            word_counter.update(words)

    # Postprocess to deal with sentence starting capitalizations and other casing issues
    word_counter = postprocess(word_counter)

    # Sort words by frequency and then alphabetically
    sorted_words = sorted(word_counter.items(), key=lambda item: (-item[1], item[0]))

    # Write to output file
    with open(OUTPUT_WORDLIST, 'w', encoding='utf-8') as file:
        for word, freq in sorted_words:
            if pass_check(word, freq):
                file.write(f"{word}\t{freq}\n")
    
    print(f"Wordlist created successfully at {OUTPUT_WORDLIST}")

def postprocess(counter: Counter) -> Counter:
    """
    Merges word frequencies ignoring case, and retains the most frequent casing variant.
    In case of a tie, prefers the all-lowercase variant.
    """
    freq_dict = defaultdict(int)
    casing_variants = defaultdict(Counter)

    for word, freq in counter.items():
        lower_word = word.lower()
        freq_dict[lower_word] += freq
        casing_variants[lower_word][word] += freq

    result = Counter()
    for lower_word, total_freq in freq_dict.items():
        variants = casing_variants[lower_word]
        most_common_freq = variants.most_common(1)[0][1]

        tied_variants = [v for v, f in variants.items() if f == most_common_freq]
        best_variant = min((v for v in tied_variants if v.islower()), default=min(tied_variants))

        result[best_variant] = total_freq
    return result

# Create the wordlist
create_wordlist_from_sentences()

# Plotting some stats about the data:
import matplotlib.pyplot as plt
def plot_word_frequencies(input_file: str) -> None:
    """
    Plots the frequency of words from a given input file.
    input_file (str): Path to the input file containing words and their frequencies.
    """
    frequencies = []
    words = []

    with open(input_file, 'r', encoding='utf-8') as file:
        for line in file:
            word, freq = line.strip().split('\t')
            frequencies.append(int(freq))
            words.append(word)

    plt.figure(figsize=(12, 6))
    plt.bar(words[:50], frequencies[:50])  # Plot only the first 50 for clarity
    plt.xticks(rotation=90)
    plt.title('Word Frequencies')
    plt.xlabel('Words')
    plt.ylabel('Frequency')
    plt.tight_layout()
    plt.show()

# Data inspection
plot_word_frequencies(OUTPUT_WORDLIST)
