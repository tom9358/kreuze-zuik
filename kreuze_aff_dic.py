# Define the file paths

input_file_path = 'kreuze_freq_wordlist.txt' #D:\Kreuze-app\kreuze-zuik\kreuze_freq_wordlist.txt
output_file_path = 'gos_NL.dic'

# Initialize an empty list to hold the words
words = []

# Open and read the input file with UTF-8 encoding
with open(input_file_path, 'r', encoding='utf-8') as file:
    for line in file:
        # Split each line by tab to separate the word and its frequency
        word, frequency = line.strip().split('\t')
        words.append(word)

# Sort the list of words
# words = sorted(words)

# Open the output file and write the words to it
with open(output_file_path, 'w', encoding='utf-8') as file:
    # Write the total number of words as the first line (required by Hunspell)
    file.write(f'{len(words)}\n')
    for word in words:
        file.write(f'{word}\n')

print(f'Dictionary file {output_file_path} created successfully!')
