import re
import os
from collections import Counter, defaultdict

def find_examples_with_word_per_document(search_pattern, max_example_lines=40):
    word_pattern = re.compile(rf'\b{search_pattern}\b', re.IGNORECASE)
    results = defaultdict(lambda: {"lines": [], "count": 0})
    
    for filename in os.listdir():
        if filename.endswith('.txt'):  # Process only text files
            with open(filename, 'r', encoding='utf-8') as file:
                line_count = 0
                for line in file:
                    if line_count >= max_example_lines:
                        break
                    if word_pattern.search(line):
                        results[filename]["lines"].append(line.strip())
                        results[filename]["count"] += 1
                        line_count += 1
    
    return results

def most_common_form_finder_per_document(search_pattern, max_example_lines=40):
    word_pattern = re.compile(rf'\b{search_pattern}\b', re.IGNORECASE)
    document_match_counter = defaultdict(Counter)
    
    for filename in os.listdir():
        if filename.endswith('.txt'):  # Process only text files
            with open(filename, 'r', encoding='utf-8') as file:
                processed_lines = 0
                for line in file:
                    if processed_lines >= max_example_lines:
                        break
                    
                    matches = word_pattern.findall(line)
                    if matches:
                        document_match_counter[filename].update(matches)
                        processed_lines += 1
    
    return {doc: dict(counter.most_common()) for doc, counter in document_match_counter.items()}

# Example usage
search_pattern = r"schier"
max_lines = 50

# Find examples per document
examples_per_document = find_examples_with_word_per_document(search_pattern, max_lines)
print("Examples per document:")
for doc, data in examples_per_document.items():
    print(f"\n{doc}: {data['count']} matches")
    for example in data['lines']:
        print(f"  - {example}")

# Find match counts per document
match_counts_per_document = most_common_form_finder_per_document(search_pattern, max_lines)
print("\nMatch counts per document:")
for doc, counts in match_counts_per_document.items():
    print(f"\n{doc}:")
    for word, count in counts.items():
        print(f"  {word}: {count}")
