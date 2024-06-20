import os
import json
import re
from collections import Counter
import unicodedata

def remove_diacritics(text):
    normalized_text = unicodedata.normalize('NFKD', text)
    return ''.join(c for c in normalized_text if not unicodedata.combining(c))

def merge_and_count_words(root_dir):
    try:
        for subdir, dirs, files in os.walk(root_dir):
            word_count = Counter()
            dir_name = os.path.basename(subdir)
            merged_file = os.path.join(subdir, f'{dir_name}_allPositions.txt')
            word_count_file = os.path.join(subdir, f'{dir_name}_word_count.json')

            with open(merged_file, 'w', encoding='utf-8') as outfile:
                for file in files:
                    if file.endswith('.txt'):
                        file_path = os.path.join(subdir, file)
                        with open(file_path, 'r', encoding='utf-8') as infile:
                            for line in infile:
                                line_without_diacritics = remove_diacritics(line)
                                outfile.write(line_without_diacritics)
                                words = re.findall(r'\b[a-zA-Z]{2,}\b', line_without_diacritics.lower())
                                word_count.update(words)
                            outfile.write("\n\n")
            save_to_json(word_count, word_count_file)

    except Exception as e:
        print(f"An error occurred: {e}")

def save_to_json(data, output_file):
    try:
        sorted_data = dict(sorted(data.items(), key=lambda item: item[1], reverse=True))
        with open(output_file, 'w', encoding='utf-8') as file:
            json.dump(sorted_data, file, ensure_ascii=False, indent=4)
    except Exception as e:
        print(f"An error occurred while writing to {output_file}: {e}")

def main():
    root_directory = 'ScrappedPositions'
    merge_and_count_words(root_directory)

if __name__ == "__main__":
    main()