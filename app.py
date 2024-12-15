from flask import Flask, jsonify, render_template, request
import os
import re
import json
from collections import Counter, defaultdict

app = Flask(__name__)

JSON_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'aggregated_text_kreuze.json')

with open(JSON_FILE, 'r', encoding='utf-8') as file:
        AGGREGATED_DATA = json.load(file)

def split_into_sentences(text, max_length=99):
    """
    Splits text into sentences by detecting sentence-ending punctuation with regex.
    Also splits long chunks.
    """
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

def process_pages(search_pattern, max_example_lines):
    """
    Processes pages to find examples and count matches.
    """
    word_pattern = re.compile(rf'\b{search_pattern}\b', re.IGNORECASE)
    results = defaultdict(lambda: {"lines": [], "count": 0})
    document_match_counter = defaultdict(Counter)

    total_sentences_processed = 0  # Counter for sentences

    for filename, pages in AGGREGATED_DATA.items():
        for page_content in pages:
            if total_sentences_processed >= max_example_lines:
                break
            sentences = split_into_sentences(page_content)
            for sentence in sentences:
                if total_sentences_processed >= max_example_lines:
                    break

                if word_pattern.search(sentence):
                    results[filename]["lines"].append(sentence)
                    results[filename]["count"] += 1
                    total_sentences_processed += 1
                matches = word_pattern.findall(sentence)
                if matches:
                    document_match_counter[filename].update(matches)

    return results, document_match_counter

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/process', methods=['POST'])
def process():
    search_pattern = request.form['search_pattern']
    max_lines = int(request.form['max_lines'])

    examples, match_counts = process_pages(search_pattern, max_lines)

    # Prepare a JSON structure for separate display
    hits_per_file = {filename: data['count'] for filename, data in examples.items()}
    example_lines = {filename: data['lines'] for filename, data in examples.items()}
    match_counts = {doc: dict(counter.most_common()) for doc, counter in match_counts.items()}

    return jsonify({'hits_per_file': hits_per_file, 'examples': example_lines, 'counts': match_counts})

if __name__ == '__main__':
    app.run(debug=True)
