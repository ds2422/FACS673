import nltk
import os

# Set the download directory to a location where we have write permissions
nltk_data_dir = os.path.join(os.path.dirname(__file__), 'nltk_data')
os.makedirs(nltk_data_dir, exist_ok=True)

# Set the NLTK data path
nltk.data.path = [nltk_data_dir] + nltk.data.path

# Download required NLTK data
for package in ['punkt', 'stopwords', 'averaged_perceptron_tagger', 'wordnet']:
    print(f"Downloading {package}...")
    nltk.download(package, download_dir=nltk_data_dir)

print(f"\nNLTK data has been downloaded to: {nltk_data_dir}")
print("Please add this to your environment variables as NLTK_DATA if needed")