from flask import Flask, jsonify, render_template, request
import os
import re
import json
from collections import Counter, defaultdict

app = Flask(__name__)

JSON_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'aggregated_text_kreuze.json')

def load_aggregated_data():
    """Load the JSON file containing aggregated text data."""
    if os.path.exists(JSON_FILE):
        with open(JSON_FILE, 'r', encoding='utf-8') as file:
            return json.load(file)
    return {}

def find_examples_with_word_per_document(search_pattern, max_example_lines=40):
    """Find examples of a search pattern in the aggregated data."""
    word_pattern = re.compile(rf'\b{search_pattern}\b', re.IGNORECASE)
    aggregated_data = load_aggregated_data()

    results = defaultdict(lambda: {"lines": [], "count": 0})
    total_count = 0
    total_lines_processed = 0

    for filename, pages in aggregated_data.items():
        for page_content in pages:
            if total_lines_processed >= max_example_lines:
                break
            lines = page_content.split('\n')
            for line in lines:
                if total_lines_processed >= max_example_lines:
                    break
                if word_pattern.search(line):
                    results[filename]["lines"].append(line.strip())
                    results[filename]["count"] += 1
                    total_count += 1
                    total_lines_processed += 1
    return results, total_count

def most_common_form_finder_per_document(search_pattern, max_example_lines=40):
    """Find the most common forms of the search pattern in the aggregated data."""
    word_pattern = re.compile(rf'\b{search_pattern}\b', re.IGNORECASE)
    aggregated_data = load_aggregated_data()

    document_match_counter = defaultdict(Counter)
    total_lines_processed = 0

    for filename, pages in aggregated_data.items():
        for page_content in pages:
            if total_lines_processed >= max_example_lines:
                break
            lines = page_content.split('\n')
            for line in lines:
                if total_lines_processed >= max_example_lines:
                    break
                matches = word_pattern.findall(line)
                if matches:
                    document_match_counter[filename].update(matches)
                    total_lines_processed += 1
    return {doc: dict(counter.most_common()) for doc, counter in document_match_counter.items()}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/process', methods=['POST'])
def process():
    search_pattern = request.form['search_pattern']
    max_lines = int(request.form['max_lines'])

    examples, total_count = find_examples_with_word_per_document(search_pattern, max_lines)
    match_counts = most_common_form_finder_per_document(search_pattern, max_lines)

    # Prepare a JSON structure for separate display
    hits_per_file = {filename: data['count'] for filename, data in examples.items()}
    example_lines = {filename: data['lines'] for filename, data in examples.items()}

    return jsonify({'hits_per_file': hits_per_file, 'examples': example_lines, 'counts': match_counts})

if __name__ == '__main__':
    app.run(debug=True)