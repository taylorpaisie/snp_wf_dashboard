import base64
import io
import pandas as pd
from Bio import Phylo

def decode_uploaded_file(contents):
    """Decodes a base64-encoded file uploaded to Dash."""
    content_type, content_string = contents.split(',')
    decoded = base64.b64decode(content_string).decode("utf-8")
    return decoded

def save_uploaded_tree(contents, filename="uploaded_tree.tree"):
    """Decodes and saves a Newick tree file."""
    decoded_tree = decode_uploaded_file(contents)
    with open(filename, "w") as f:
        f.write(decoded_tree)
    return filename

def save_uploaded_metadata(contents, filename="uploaded_metadata.tsv"):
    """Decodes and saves a metadata file."""
    decoded_metadata = decode_uploaded_file(contents)
    with open(filename, "w") as f:
        f.write(decoded_metadata)
    return filename

def load_tree(file_path):
    """Loads a phylogenetic tree from a Newick file."""
    return Phylo.read(file_path, 'newick')

def load_metadata(file_path):
    """Loads a metadata file into a Pandas DataFrame."""
    return pd.read_csv(file_path, sep='\t')
