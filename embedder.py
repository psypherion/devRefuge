import os
import numpy as np
from sentence_transformers import SentenceTransformer

class SentenceTransformerTextEmbedder:
    """
    A class to handle embedding of tokenized text files using Sentence Transformers model.
    """
    def __init__(self, model_name: str = 'all-MiniLM-L6-v2'):
        """
        Initializes the SentenceTransformerTextEmbedder with a specified model.
        
        Args:
            model_name (str): The name of the Sentence Transformer model to use for embedding.
        """
        self.model_name = model_name
        self.model = SentenceTransformer(self.model_name)

    def read_tokenized_text(self, filepath: str):
        """
        Reads a tokenized text file and returns its content as a list of sentences.
        
        Args:
            filepath (str): Path to the tokenized text file.
        
        Returns:
            List[str]: List of tokenized sentences.
        """
        with open(filepath, 'r') as file:
            return [line.strip() for line in file.readlines() if line.strip()]

    def embed_texts(self, texts):
        """
        Embeds a list of sentences using the Sentence Transformer model.
        
        Args:
            texts (List[str]): List of sentences to embed.
        
        Returns:
            np.ndarray: An array of sentence embeddings.
        """
        # Get embeddings for the sentences
        embeddings = self.model.encode(texts)
        return embeddings

    def process_directory(self, input_dir: str, output_dir: str):
        """
        Processes all tokenized text files in a directory, embedding their content and saving results.
        
        Args:
            input_dir (str): Directory containing tokenized text files.
            output_dir (str): Directory to save the embedding files.
        """
        os.makedirs(output_dir, exist_ok=True)
        
        for filename in os.listdir(input_dir):
            if filename.endswith('.txt'):
                filepath = os.path.join(input_dir, filename)
                print(f"Processing {filename}...")

                # Read and embed text
                tokenized_text = self.read_tokenized_text(filepath)
                embeddings = self.embed_texts(tokenized_text)

                # Save embeddings to .npy file
                output_path = os.path.join(output_dir, filename.replace('.txt', '_embeddings.npy'))
                np.save(output_path, embeddings)
                print(f"Embeddings saved to {output_path}")

# Example usage:
embedder = SentenceTransformerTextEmbedder()
embedder.process_directory(input_dir='chunks/python', output_dir='embeddings/python')
