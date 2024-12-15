from flask import Flask, jsonify, render_template, request
import os
import re
from collections import Counter, defaultdict

app = Flask(__name__)

# Folder where the text files are located
TEXT_FOLDER = os.path.dirname(os.path.abspath(__file__))  # Same directory as app.py
def find_examples_with_word_per_document(search_pattern, max_example_lines=40):
    word_pattern = re.compile(rf'\b{search_pattern}\b', re.IGNORECASE)
    results = defaultdict(lambda: {"lines": [], "count": 0})
    total_count = 0
    total_lines_processed = 0  # New counter for total lines processed

    for filename in os.listdir(TEXT_FOLDER):
        if filename.endswith('.txt') and total_lines_processed < max_example_lines:
            file_path = os.path.join(TEXT_FOLDER, filename)
            with open(file_path, 'r', encoding='utf-8') as file:
                for line in file:
                    if total_lines_processed >= max_example_lines:
                        break
                    if word_pattern.search(line):
                        results[filename]["lines"].append(line.strip())
                        results[filename]["count"] += 1
                        total_count += 1
                        total_lines_processed += 1  # Increment global-er counter
    return results, total_count

def most_common_form_finder_per_document(search_pattern, max_example_lines=40):
    word_pattern = re.compile(rf'\b{search_pattern}\b', re.IGNORECASE)
    document_match_counter = defaultdict(Counter)
    
    # Iterate over all .txt files in the folder
    for filename in os.listdir(TEXT_FOLDER):
        if filename.endswith('.txt'):  # Process only .txt files
            file_path = os.path.join(TEXT_FOLDER, filename)
            with open(file_path, 'r', encoding='utf-8') as file:
                processed_lines = 0
                for line in file:
                    if processed_lines >= max_example_lines:
                        break
                    
                    matches = word_pattern.findall(line)
                    if matches:
                        document_match_counter[filename].update(matches)
                        processed_lines += 1
    
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
