import os
import re
from typing import List

class TextTokenizer:
    """
    A class to read, tokenize, and save text chunks from files.
    """

    def __init__(self, max_tokens: int = 512):
        """
        Initializes the TextTokenizer with the maximum number of tokens per chunk.

        Args:
            max_tokens (int): The maximum number of tokens per chunk.
        """
        self.max_tokens = max_tokens

    def read_text_file(self, filepath: str) -> str:
        """
        Reads the content of a text file.

        Args:
            filepath (str): Path to the text file.

        Returns:
            str: The content of the text file.
        """
        with open(filepath, 'r', encoding='utf-8') as file:
            return file.read()

    def tokenize_text(self, text: str) -> List[str]:
        """
        Tokenizes text into chunks with a maximum number of tokens.

        Args:
            text (str): The input text to tokenize.

        Returns:
            List[str]: A list of tokenized text chunks.
        """
        # Split the text into sentences
        sentences = re.split(r'(?<=[.!?]) +', text)

        chunks = []
        current_chunk = []
        current_length = 0

        for sentence in sentences:
            sentence_length = len(sentence.split())
            if current_length + sentence_length <= self.max_tokens:
                current_chunk.append(sentence)
                current_length += sentence_length
            else:
                # Save the current chunk and start a new one
                chunks.append(' '.join(current_chunk))
                current_chunk = [sentence]
                current_length = sentence_length

        # Add the last chunk if not empty
        if current_chunk:
            chunks.append(' '.join(current_chunk))

        return chunks

    def tokenize_files_in_directory(self, input_dir: str, output_dir: str) -> None:
        """
        Tokenizes all text files in a directory and saves the chunks to new files.

        Args:
            input_dir (str): Directory containing the input text files.
            output_dir (str): Directory to save the tokenized output files.
        """
        os.makedirs(output_dir, exist_ok=True)

        for filename in os.listdir(input_dir):
            if filename.endswith('.txt'):
                filepath = os.path.join(input_dir, filename)
                text = self.read_text_file(filepath)
                chunks = self.tokenize_text(text)

                # Save each chunk to separate files
                for i, chunk in enumerate(chunks):
                    output_filepath = os.path.join(output_dir, f"{filename[:-4]}_chunk_{i+1}.txt")
                    with open(output_filepath, 'w', encoding='utf-8') as out_file:
                        out_file.write(chunk)
                print(f"Tokenized and saved chunks for {filename}")

# Example usage
if __name__ == "__main__":
    input_directory = 'db/python'
    output_directory = 'chunks/python'
    tokenizer = TextTokenizer(max_tokens=512)
    tokenizer.tokenize_files_in_directory(input_directory, output_directory)
