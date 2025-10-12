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

WORDLIST_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'kreuze_freq_wordlist.txt')
with open(WORDLIST_PATH, 'r', encoding='utf-8') as file:
    for line in file:
        word, freq_str   = line.strip().split('\t')
        freq             = int(freq_str)
        log_f            = math.log10(freq)
        WORDLIST.append(word)
        WORD_FREQUENCIES.append((word,freq))
        WORD_STATS.append({'word': word, 'freq': freq, 'log': log_f})
        _log_values.append(log_f)

# normalize log‑frequencies -> 0 (= rare) ... 100 (= most frequent)
_min_log, _max_log = min(_log_values), max(_log_values)
scale = 100 / (_max_log - _min_log)

for d in WORD_STATS:
    d['norm'] = (d['log'] - _min_log) * scale

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
    re_finditer = word_pattern.finditer
    form_counts = Counter()

    for filename, sentences in AGGREGATED_DATA.items():
        doc_counter = document_match_counter[filename]
        res_entry = results[filename]
        for sentence in sentences:
            if total_sentences_processed >= max_example_lines:
                break

            iters = re_finditer(sentence)
            first_match = next(iters, None)
            if first_match is None:
                continue
            matches = [first_match[0]] + [m[0] for m in iters]

            res_entry["lines"].append(sentence)
            res_entry["count"] += 1
            total_sentences_processed += 1

            doc_counter.update(matches)
            form_counts.update(matches)
    results = {k: v for k, v in results.items() if v["count"] > 0}
    return results, document_match_counter, form_counts

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

    examples, match_counts, form_counts = find_example_sentences(search_pattern, max_lines)

    if not any(examples.values()):
        # No matches found; suggest closest words
        suggestions = get_close_matches(search_pattern, WORDLIST, n=7)
        return jsonify({'suggestions': suggestions})

    # Prepare a JSON structure for separate display
    hits_per_file = {filename: data['count'] for filename, data in examples.items()}
    example_lines = {filename: data['lines'] for filename, data in examples.items()}
    match_counts = {doc: dict(counter.most_common()) for doc, counter in match_counts.items()}

    total_hits = sum(hits_per_file.values())

    return jsonify({
        'hits_per_file': hits_per_file,
        'examples': example_lines,
        'counts': match_counts,
        'form_counts': dict(form_counts),
        'total_hits': total_hits
    })

if __name__ == '__main__':
    app.run(debug=False)
