"""
Text processing utility module for CivicPulse AI.
Handles text normalization, contraction expansion, stopword filtering,
keyword extraction, and location entity detection.
"""

import re
import string
from typing import List, Set, Tuple


# Contractions dictionary for standardization
CONTRACTIONS = {
    "ain't": "is not", "aren't": "are not", "can't": "cannot", "could've": "could have",
    "couldn't": "could not", "didn't": "did not", "doesn't": "does not", "don't": "do not",
    "hadn't": "had not", "hasn't": "has not", "haven't": "have not", "he'd": "he would",
    "he'll": "he will", "he's": "he is", "how'd": "how did", "how'll": "how will",
    "how's": "how is", "i'd": "i would", "i'll": "i will", "i'm": "i am", "i've": "i have",
    "isn't": "is not", "it'd": "it would", "it'll": "it will", "it's": "it is",
    "let's": "let us", "ma'am": "madam", "mightn't": "might not", "mustn't": "must not",
    "shan't": "shall not", "she'd": "she would", "she'll": "she will", "she's": "she is",
    "shouldn't": "should not", "that's": "that is", "there's": "there is", "they'd": "they would",
    "they'll": "they will", "they're": "they are", "they've": "they have", "wasn't": "was not",
    "we'd": "we would", "we'll": "we will", "we're": "we are", "we've": "we have",
    "weren't": "were not", "what's": "what is", "where's": "where is", "who's": "who is",
    "won't": "will not", "wouldn't": "would not", "you'd": "you would", "you'll": "you will",
    "you're": "you are", "you've": "you have"
}

# Domain-aware stopwords (keeps critical intent modifiers like 'not', 'no', 'off')
COMMON_STOPWORDS: Set[str] = {
    "a", "about", "above", "after", "again", "against", "all", "am", "an", "and",
    "any", "are", "as", "at", "be", "because", "been", "before", "being", "below",
    "between", "both", "but", "by", "could", "did", "do", "does", "doing", "down",
    "during", "each", "few", "for", "from", "further", "had", "has", "have",
    "having", "he", "her", "here", "hers", "herself", "him", "himself", "his",
    "how", "i", "if", "in", "into", "is", "it", "its", "itself", "just", "me",
    "more", "most", "my", "myself", "of", "off", "on", "once", "only", "or",
    "other", "ought", "our", "ours", "ourselves", "out", "over", "own", "same",
    "she", "should", "so", "some", "such", "than", "that", "the", "their",
    "theirs", "them", "themselves", "then", "there", "these", "they", "this",
    "those", "through", "to", "too", "under", "until", "up", "very", "was",
    "we", "were", "what", "when", "where", "which", "while", "who", "whom",
    "why", "with", "would", "you", "your", "yours", "yourself", "yourselves",
    "please", "kindly", "sir", "madam", "respected", "urgent", "regards",
    "thanks", "thank", "hello", "hi", "issue", "problem", "complaint"
}


def expand_contractions(text: str) -> str:
    """Expands standard English contractions."""
    pattern = re.compile(r'\b(' + '|'.join(re.escape(key) for key in CONTRACTIONS.keys()) + r')\b', re.IGNORECASE)
    def replace(match):
        token = match.group(0).lower()
        return CONTRACTIONS.get(token, token)
    return pattern.sub(replace, text)


def clean_text(text: str) -> str:
    """
    Cleans and standardizes raw text:
    - Expands contractions
    - Converts to lowercase
    - Normalizes punctuation and excessive whitespace
    """
    if not text or not isinstance(text, str):
        return ""
    
    # Expand contractions
    text = expand_contractions(text)
    
    # Lowercase
    text = text.lower()
    
    # Remove HTML tags if present
    text = re.sub(r'<.*?>', ' ', text)
    
    # Replace newlines and tabs with space
    text = re.sub(r'[\r\n\t]+', ' ', text)
    
    # Remove non-alphanumeric characters except basic punctuation
    text = re.sub(r'[^a-zA-Z0-9\s.,!?\-_/]', ' ', text)
    
    # Normalize multiple whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    
    return text


def tokenize(text: str, remove_stopwords: bool = True) -> List[str]:
    """
    Tokenizes cleaned text into a list of meaningful word tokens.
    """
    cleaned = clean_text(text)
    # Remove punctuation
    cleaned_no_punct = cleaned.translate(str.maketrans("", "", string.punctuation))
    words = cleaned_no_punct.split()
    
    if remove_stopwords:
        tokens = [w for w in words if w not in COMMON_STOPWORDS and len(w) > 1]
    else:
        tokens = [w for w in words if len(w) > 1]
        
    return tokens


def extract_keywords(text: str, max_keywords: int = 6) -> List[str]:
    """
    Extracts high-signal keywords and 2-gram phrases from the complaint text.
    """
    tokens = tokenize(text, remove_stopwords=True)
    if not tokens:
        return []

    # Count frequencies of unigrams
    freqs: dict[str, int] = {}
    for t in tokens:
        freqs[t] = freqs.get(t, 0) + 1

    # Extract bigrams
    bigrams = []
    for i in range(len(tokens) - 1):
        bigrams.append(f"{tokens[i]} {tokens[i+1]}")
    
    for b in bigrams:
        freqs[b] = freqs.get(b, 0) + 2  # Boost bigrams slightly

    # Sort by frequency and score
    sorted_keywords = sorted(freqs.items(), key=lambda item: (item[1], len(item[0])), reverse=True)
    return [kw for kw, _ in sorted_keywords[:max_keywords]]


def extract_location_hint(text: str) -> str:
    """
    Heuristically extracts potential location names, room numbers, or lab blocks from text.
    E.g. 'EEE Lab 2', 'Room 304', 'Block B', 'Floor 3', 'Library', 'Hostel Mess'.
    """
    patterns = [
        r'\b([A-Z]{2,5}\s+(?:Lab|Block|Building|Hall|Room|Dept|Department)\s*(?:[0-9A-Za-z\-]+)?)\b',
        r'\b((?:Lab|Room|Block|Floor|Hall|Wing|Cabin|Desk)\s+[0-9A-Za-z\-]+)\b',
        r'\b((?:Library|Canteen|Cafeteria|Auditorium|Gymnasium|Hostel|Mess|Parking|Ground|Restroom|Washroom)(?:\s+[0-9A-Za-z\-]+)?)\b',
        r'\b([A-Za-z]+\s+Block(?:\s+[0-9A-Za-z\-]+)?)\b'
    ]

    for p in patterns:
        match = re.search(p, text, re.IGNORECASE)
        if match:
            return match.group(0).strip()
            
    return ""
