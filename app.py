from flask import Flask, jsonify, render_template, request
import os
import re
import json
from collections import Counter, defaultdict
from difflib import get_close_matches
import random
import math

app = Flask(__name__)

JSON_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'sentences_kreuze.json')
with open(JSON_FILE, 'r', encoding='utf-8') as file:
    AGGREGATED_DATA = json.load(file)

WORDLIST = []
WORD_FREQUENCIES = []
WORD_STATS        = []
_log_values       = []


with open("kreuze_freq_wordlist.txt", 'r', encoding='utf-8') as file:
    for line in file:
        word, freq_str   = line.strip().split('\t')
        freq             = int(freq_str)
        log_f            = math.log10(freq)              # log‑freq (basis 10)
        WORDLIST.append(word)
        WORD_FREQUENCIES.append((word,freq))
        WORDLIST.append(word)
        WORD_STATS.append({'word': word, 'freq': freq, 'log': log_f})
        _log_values.append(log_f)

# normalize log‑frequencies -> 0 (= rare) ... 100 (= most frequent)
_min_log, _max_log = min(_log_values), max(_log_values)
for d in WORD_STATS:
    d['norm'] = 100 * (d['log'] - _min_log) / (_max_log - _min_log)

# optional sorting, nice for debugging
WORD_STATS.sort(key=lambda d: d['norm'])

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

def sample_random_words(center, bandwidth, num_samples, min_len, max_len):
    """
    Samples random words based on rarity, length, and number of samples.
    """
    lo = max(0, center - bandwidth / 2)
    hi = min(100, center + bandwidth / 2)

    pool = [
        d for d in WORD_STATS
        if lo <= d['norm'] <= hi and min_len <= len(d['word']) <= max_len
    ]
    if not pool:
        return []

    chosen = random.sample(pool, min(num_samples, len(pool)))
    return [{'word': d['word'], 'freq': d['freq']} for d in chosen]


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/random_word')
def random_word_page():
    return render_template('random_word.html')

@app.route('/get_random_words', methods=['POST'])
def get_random_words():
    data         = request.json
    center       = float(data['rarity_center'])
    bandwidth    = float(data['bandwidth'])
    num_samples  = int(data['num_samples'])
    min_length   = int(data['minLength'])
    max_length   = int(data['maxLength'])
    sampled      = sample_random_words(center, bandwidth,
                                       num_samples, min_length, max_length)

    return jsonify({'words': sampled})

@app.route('/process', methods=['POST'])
def process():
    search_pattern = request.form['search_pattern']
    max_lines = int(request.form['max_lines'])

    examples, match_counts = find_example_sentences(search_pattern, max_lines)

    if not any(examples.values()):
        # No matches found; suggest closest words
        suggestions = get_close_matches(search_pattern, WORDLIST, n=7)
        return jsonify({'suggestions': suggestions})

    # Prepare a JSON structure for separate display
    hits_per_file = {filename: data['count'] for filename, data in examples.items()}
    example_lines = {filename: data['lines'] for filename, data in examples.items()}
    match_counts = {doc: dict(counter.most_common()) for doc, counter in match_counts.items()}

    return jsonify({'hits_per_file': hits_per_file, 'examples': example_lines, 'counts': match_counts})

if __name__ == '__main__':
    app.run(debug=True)
