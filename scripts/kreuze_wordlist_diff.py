def get_words_from_file(filename):
    """Reads a tab-separated wordlist and returns a set of words."""
    words = set()
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            for line in f:
                parts = line.lower().strip().split('\t')
                if parts:
                    words.add(parts[0])
    except FileNotFoundError:
        print(f"Error: File '{filename}' not found.")
    return words

def main():
    new_wordlist_file = 'kreuze_freq_wordlist.txt'
    old_wordlist_file = 'kreuze_freq_wordlist_old.txt'

    # Get words from both files
    words_in_new = get_words_from_file(new_wordlist_file)
    words_in_old = get_words_from_file(old_wordlist_file)

    # Find words present in the old list but not in the new list
    words_only_in_old = words_in_old - words_in_new

    if words_only_in_old:
        print(f"Words present in '{old_wordlist_file}' but not in '{new_wordlist_file}':")
        for word in list(words_only_in_old)[:900]: # Sort for consistent output
            print(word)
    else:
        print("No words found in the old list that are not in the new list.")

if __name__ == "__main__":
    main()