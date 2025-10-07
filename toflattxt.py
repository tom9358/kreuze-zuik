import json
import re

# Load JSON file
with open("sentences_kreuze.json", "r", encoding="utf-8") as f:
    data = json.load(f)

all_text = []

# Flatten the JSON and clean text
for key, texts in data.items():
    for text in texts:
        # Replace '|' with line breaks, then normalize all line breaks to spaces
        text = text.replace("|", "\n")
        text = text.replace("\n", " ")
        text = re.sub(r"\.{4,}", "...", text)
        text = re.sub(r"^\d+\s+([A-Z])", r"\1", text)
        text = re.sub(r"\s+\d+$", "", text)
        text = re.sub(r"\s+", " ", text).strip()
        all_text.append(text)

# Remove lines that have less than 2 words containing letters
def count_words_with_letters(line):
    return sum(1 for w in line.split() if re.search(r"[A-Za-z]", w))

# Merge lines if previous line does not end in a period and next line starts with a capital
merged_text = []
i = 0
while i < len(all_text):
    current = all_text[i]
    while (i + 1 < len(all_text) and 
           not current.endswith('.') and 
           re.match(r"^[A-Z]", all_text[i + 1])):
        # Merge with next line
        current += " " + all_text[i + 1]
        i += 1
    merged_text.append(current)
    i += 1

filtered_text = [line for line in merged_text if count_words_with_letters(line) > 1]

# Deduplicate
seen = set()
unique_text = []
for t in filtered_text:
    if t not in seen:
        unique_text.append(t)
        seen.add(t)

# Join everything into one big string for GPT-2 fine-tuning
final_text = "\n".join(unique_text)

# Save to a text file
with open("cleaned_text.txt", "w", encoding="utf-8") as f:
    f.write(final_text)

print(f"Done! {len(unique_text)} unique lines saved to cleaned_text.txt")
