from flask import Flask, jsonify, render_template, request
import os
import re
import json
from collections import Counter, defaultdict
from difflib import get_close_matches

app = Flask(__name__)

JSON_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'sentences_kreuze.json')
with open(JSON_FILE, 'r', encoding='utf-8') as file:
        AGGREGATED_DATA = json.load(file)

with open("kreuze_freq_wordlist.txt", 'r', encoding='utf-8') as file:
    WORDLIST = [line.split('\t')[0] for line in file.readlines()]

def find_example_sentences(search_pattern, max_example_lines):
    """
    Find example sentences and count matches.
    """
    word_pattern = re.compile(rf'\b{search_pattern}\b', re.IGNORECASE)
    results = defaultdict(lambda: {"lines": [], "count": 0})
    document_match_counter = defaultdict(Counter)

    total_sentences_processed = 0

    for filename, sentences in AGGREGATED_DATA.items():
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

    examples, match_counts = find_example_sentences(search_pattern, max_lines)

    # Prepare a JSON structure for separate display
    hits_per_file = {filename: data['count'] for filename, data in examples.items()}
    example_lines = {filename: data['lines'] for filename, data in examples.items()}
    match_counts = {doc: dict(counter.most_common()) for doc, counter in match_counts.items()}

    return jsonify({'hits_per_file': hits_per_file, 'examples': example_lines, 'counts': match_counts})

if __name__ == '__main__':
    app.run(debug=True)
