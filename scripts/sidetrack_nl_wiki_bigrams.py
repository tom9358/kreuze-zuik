import re
import csv
from collections import Counter
from datasets import load_dataset


# 1. Corpus inladen: Nederlandse Wikipedia (streaming mode!)
dataset = load_dataset(
    "wikimedia/wikipedia",
    "20231101.nl", # is veranderlijk
    split="train",
    streaming=True
)

# 2. Functie om woorden te extraheren
def tokenize(text: str) -> list[str]:
    # Tokenisatie: alleen letters en cijfers, alles naar kleine letters
    return re.findall(r"\w+", text.lower())

# 3. Counter voor bigrams
bigram_counter = Counter()

# 4. Loop over een sample van 2000 teksten
for i, sample in enumerate(dataset):
    if i >= 2000:
        break
    words = tokenize(sample["text"])
    bigrams = zip(words, words[1:]) # easily adaptable to n-grams
    bigram_counter.update(bigrams)

# 5. Resultaat opslaan als TSV
output_file: str = "bigram_frequentie_nl_wiki.tsv"
with open(output_file, "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f, delimiter="\t")
    writer.writerow(["woord_1", "woord_2", "frequentie"])
    for (w1, w2), count in bigram_counter.most_common():
        writer.writerow([w1, w2, count])

print(f"Klaar! Resultaat opgeslagen in {output_file}")
