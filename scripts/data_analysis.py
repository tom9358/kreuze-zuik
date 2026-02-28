#About the json and the old txt files:

import os
import json
import re
import unicodedata

JSON_FILE = 'sentences_kreuze.json'

def count_unique_words(JSON_FILE: str = 'sentences_kreuze.json'):
    with open(JSON_FILE, 'r', encoding='utf-8') as file:
        data = json.load(file)

    word_set = set()
    for pages in data.values():
        for page in pages:
            page = page.replace('-\n', '').replace('\n', ' ').replace("d'", 'de ').lower()
            page = unicodedata.normalize("NFKC", page)
            words = re.findall(r'\b\w+\b', page)
            word_set.update(words)

    print(f"Unique words: {len(word_set)}")

count_unique_words()
count_unique_words("aggregated_text_kreuze.json")

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
TXT_DIR = os.path.abspath(os.path.join(CURRENT_DIR, '..'))

def normalize(text):
    return text.replace('-\n', '').replace('\n', ' ').replace("d'", 'de ').lower()

def extract_words(text):
    return re.findall(r'\b\w+\b', text)

def count_unique_words():
    word_set = set()

    txt_contents = []
    for fname in os.listdir(TXT_DIR):
        if fname.endswith('.txt'):
            path = os.path.join(TXT_DIR, fname)
            with open(path, 'r', encoding='utf-8') as f:
                txt_contents.append(f.read())

    if txt_contents:
        combined_txt = ' '.join(txt_contents)
        normalized_txt = normalize(combined_txt)
        words = extract_words(normalized_txt)
        word_set.update(words)

    print(f"Unique words in TXT files: {len(word_set)}")

count_unique_words()

###############

# Data analysis of the new data:

OUTPUT_WORDLIST = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'kreuze_freq_wordlist.txt')
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
from collections import Counter
import string

sns.set_theme(style="whitegrid")

def load_wordlist(path):
    words = []
    freqs = []
    with open(path, 'r', encoding='utf-8') as f:
        for line in f:
            word, freq = line.strip().split('\t')
            words.append(word)
            freqs.append(int(freq))
    return words, freqs


def plot_top_words(words, freqs, top_n=50):
    plt.figure(figsize=(12, 6))
    plt.bar(words[:top_n], freqs[:top_n])
    plt.xticks(rotation=90)
    plt.title(f'Top {top_n} Word Frequencies')
    plt.xlabel('Words')
    plt.ylabel('Frequency')
    plt.tight_layout()
    plt.show()


def plot_zipf(freqs):
    ranks = np.arange(1, len(freqs) + 1)
    plt.figure(figsize=(8, 6))
    plt.loglog(ranks, freqs, marker='.')
    plt.title("Zipf's Law: Frequency ~ 1 / Rank")
    plt.xlabel('Rank (log)')
    plt.ylabel('Frequency (log)')
    plt.tight_layout()
    plt.show()


def print_basic_stats(words, freqs):
    total_tokens = sum(freqs)
    unique_words = len(words)
    avg_freq = total_tokens / unique_words
    print(f'Total tokens: {total_tokens:,}')
    print(f'Unique words (types): {unique_words:,}')
    print(f'Average frequency per word: {avg_freq:.2f}')
    print(f'Most frequent word: "{words[0]}" ({freqs[0]} occurrences)')


def plot_coverage_curve(freqs, steps=[100, 500, 1000, 5000, 10000, 20000]):
    total = sum(freqs)
    cumulative = np.cumsum(freqs)
    coverage = [cumulative[n-1] / total for n in steps if n <= len(freqs)]
    plt.figure(figsize=(8, 6))
    plt.plot(steps[:len(coverage)], coverage, marker='o')
    plt.title('Coverage Curve')
    plt.xlabel('Top N Words')
    plt.ylabel('Cumulative Coverage (Proportion)')
    plt.ylim(0, 1)
    plt.tight_layout()
    plt.show()


def plot_word_length_distribution(words):
    lengths = [len(word) for word in words]
    length_counts = Counter(lengths)
    lengths_sorted = sorted(length_counts.items())
    x, y = zip(*lengths_sorted)
    plt.figure(figsize=(8, 6))
    plt.bar(x, y)
    plt.title('Word Length Distribution')
    plt.xlabel('Word Length')
    plt.ylabel('Number of Words')
    plt.tight_layout()
    plt.show()


def plot_frequency_histogram(freqs, max_bins=50):
    plt.figure(figsize=(8, 6))
    plt.hist(freqs, bins=max_bins, log=True)
    plt.title('Histogram of Word Frequencies')
    plt.xlabel('Frequency')
    plt.ylabel('Number of Words (log scale)')
    plt.tight_layout()
    plt.show()

def plot_char_frequencies(words):
    char_counts = Counter()
    for word in words:
        for char in word:
            char_counts[char] += 1

    # Sort characters by frequency for plotting
    sorted_chars = sorted(char_counts.items(), key=lambda item: item[1], reverse=True)
    chars, freqs = zip(*sorted_chars)

    # Plot 1: All characters
    plt.figure(figsize=(15, 7))
    plt.bar(chars, freqs)
    plt.title('Character Frequency Distribution (All Characters)')
    plt.xlabel('Characters')
    plt.ylabel('Frequency')
    plt.yscale('log')
    plt.tight_layout()
    plt.show()

    # Plot 2: Non-Latin alphabet characters
    non_latin_chars_counts = Counter()
    latin_alphabet = set(string.ascii_letters)
    for char, freq in char_counts.items():
        if char not in latin_alphabet:
            non_latin_chars_counts[char] = freq

    if non_latin_chars_counts: # Only plot if there are non-Latin characters
        sorted_non_latin = sorted(non_latin_chars_counts.items(), key=lambda item: item[1], reverse=True)
        non_latin_chars, non_latin_freqs = zip(*sorted_non_latin)

        plt.figure(figsize=(15, 7))
        plt.bar(non_latin_chars, non_latin_freqs)
        plt.title('Character Frequency Distribution (Non-Latin Alphabet Characters)')
        plt.xlabel('Characters')
        plt.ylabel('Frequency')
        plt.yscale('log')
        plt.tight_layout()
        plt.show()
        for char in non_latin_chars: print(char, end='')
    else:
        print("No non-Latin alphabet characters found to plot.")

def plot_frequency_cutoff_ranks(freqs):
    """
    Plots the rank (line number) against the frequency,
    showing only the last occurrence of each unique frequency value.
    This illustrates for a given frequency Y, how many words (rank X)
    have at least that frequency.
    """
    if not freqs:
        print("No frequencies to plot for cutoff ranks.")
        return

    ranks_to_plot = []
    freqs_to_plot = []
    seen_frequencies = set()

    # Iterate from the end to find the last occurrence of each frequency
    for i in range(len(freqs) - 1, -1, -1):
        current_freq = freqs[i]
        if current_freq not in seen_frequencies:
            ranks_to_plot.append(i + 1) # i+1 because ranks are 1-based
            freqs_to_plot.append(current_freq)
            seen_frequencies.add(current_freq)

    # Sort the collected points by rank for proper plotting order
    sorted_points = sorted(list(zip(ranks_to_plot, freqs_to_plot)))
    
    ranks, freqs_at_ranks = zip(*sorted_points) if sorted_points else ([], [])

    for i in sorted_points[::-1][:25]:
        print(i[0],"words have at least",i[1],"occurrences")
    plt.figure(figsize=(10, 7))
    plt.plot(freqs_at_ranks, ranks, marker='+', linestyle='-')
    plt.title('Rank vs. Frequency Cutoff')
    plt.ylabel('Rank (Number of words with at least this frequency)')
    plt.xlabel('Minimum Frequency')
    plt.xscale('log') # Use log scale for ranks as they can vary widely
    plt.yscale('log') # Use log scale for frequencies as they can vary widely
    plt.grid(True, which="both", ls="-", alpha=0.2)
    plt.tight_layout()
    # plt.show()

def full_analysis(path):
    words, freqs = load_wordlist(path)
    # print_basic_stats(words, freqs)
    # plot_top_words(words, freqs)
    # plot_zipf(freqs)
    # plot_coverage_curve(freqs)
    # plot_word_length_distribution(words)
    # plot_frequency_histogram(freqs)
    plot_frequency_cutoff_ranks(freqs) #kind of like a simplified Zipf plot
    # plot_char_frequencies(words)

full_analysis(OUTPUT_WORDLIST)
