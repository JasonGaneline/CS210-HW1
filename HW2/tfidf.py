"""
tfidf.py
Problem 1 - Text Processing and TF-IDF
"""

import re
import math
import sys
from collections import Counter
from pathlib import Path

def read_stopwords(path="stopwords.txt"):
    sw = set()
    try:
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                w = line.strip().lower()
                if w:
                    sw.add(w)
    except FileNotFoundError:
        # if file missing, return empty set
        return set()
    return sw

def remove_urls(text):
    return re.sub(r"https?://\S+", "", text)

def remove_nonword_chars(text):
    if not text:
        return text

    #Remove all remaining non-word characters (including apostrophes, hyphens, asterisks, etc.)
    text = re.sub(r"[^\w\s]", "", text)

    #Collapse multiple spaces
    text = re.sub(r"\s+", " ", text)

    return text.strip()




def collapse_whitespace(text):
    return re.sub(r"\s+", " ", text).strip()

def clean_text(text):
    text = remove_urls(text)
    text = remove_nonword_chars(text)
    text = text.lower()
    text = collapse_whitespace(text)
    return text

def remove_stopwords_from_text(text, stopwords):
    if not text:
        return text
    words = text.split()
    filtered = [w for w in words if w not in stopwords]
    return " ".join(filtered)

def stem_token(token):
    # Some exceptions for 'ing' ending
    ing_exceptions = {"sing", "fling", "cling", "bring", "thing", "sling"}

    # Aggressively stem 'ing' if word is longer than 4 and not in exceptions
    if token.endswith("ing") and token not in ing_exceptions and len(token) > 4:
        return token[:-3]  
        
    # Stem 'ly' endings if longer than 3
    if token.endswith("ly") and len(token) > 3:
        return token[:-2]

    # Stem 'ment' endings if longer than 5
    if token.endswith("ment") and len(token) > 5:
        return token[:-4]

    return token

def stem_text(text):
    if not text:
        return text
    words = text.split()
    stemmed = [stem_token(w) for w in words]
    # collapse again in case stemming produced empty strings or extra spaces
    return " ".join([w for w in stemmed if w]).strip()

# -----------------------
# TF-IDF computation
# -----------------------

def compute_tf(word_list):
    total = len(word_list)
    if total == 0:
        return {}
    counts = Counter(word_list)
    return {w: counts[w] / total for w in counts}

def compute_idf(all_docs_wordlists):
    N = len(all_docs_wordlists)
    idf = {}
    # collect unique words across corpus
    all_words = set()
    for wl in all_docs_wordlists:
        all_words.update(wl)
    for w in all_words:
        doc_count = sum(1 for wl in all_docs_wordlists if w in wl)
        if doc_count == 0:
            continue
        idf[w] = math.log(N / doc_count) + 1.0
    return idf

def compute_tfidf_for_doc(tf_dict, idf_dict):
    """
    tf_dict: {word: tf}
    idf_dict: {word: idf}
    returns dict {word: rounded_tfidf}
    """
    tfidf = {}
    for w, tf_val in tf_dict.items():
        idf_val = idf_dict.get(w, math.log(len(idf_dict) + 1) + 1.0)  # fallback just in case
        score = tf_val * idf_val
        # round to 2 decimals as spec requires
        score_rounded = round(score + 1e-12, 2)  # tiny epsilon to reduce floating error
        tfidf[w] = score_rounded
    return tfidf

def top_n_by_tfidf(tfidf_dict, n=5):
    """
    Sort by:
      1) descending TF-IDF score
      2) alphabetical order of word for ties
    Use rounded scores for tie-breaking.
    Returns list of (word, score) tuples.
    """
    items = list(tfidf_dict.items())
    # Sorting key: (-score, word)
    items.sort(key=lambda kv: (-kv[1], kv[0]))
    return items[:n]

# -----------------------
# File I/O and orchestration
# -----------------------

def write_preproc_file(orig_filename, content):
    out_name = f"preproc_{orig_filename}"
    with open(out_name, "w", encoding="utf-8") as f:
        f.write(content + ("\n" if content and not content.endswith("\n") else ""))
    return out_name

def write_tfidf_file(orig_filename, top_list):
    out_name = f"tfidf_{orig_filename}"
    # top_list is list of (word, score) tuples; write Python-like repr
    with open(out_name, "w", encoding="utf-8") as f:
        f.write(repr(top_list) + "\n")
    return out_name

def process_documents(doc_filenames, stopwords):
    preproc_wordlists = []
    for fname in doc_filenames:
        if not fname:
            continue
        p = Path(fname)
        if not p.exists():
            # If file doesn't exist, create empty preproc file and record empty doc
            write_preproc_file(fname, "")
            preproc_wordlists.append([])
            continue
        text = p.read_text(encoding="utf-8")
        cleaned = clean_text(text)
        no_stop = remove_stopwords_from_text(cleaned, stopwords)
        stemmed = stem_text(no_stop)
        # final ensure: only lowercase words separated by single space
        final = collapse_whitespace(stemmed.lower())
        write_preproc_file(fname, final)
        words = final.split() if final else []
        preproc_wordlists.append(words)
    return preproc_wordlists

def read_tfidf_doclist(path="tfidf_docs.txt"):
    try:
        with open(path, "r", encoding="utf-8") as f:
            lines = [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        print(f"Error: {path} not found. Please create {path} with one document filename per line.", file=sys.stderr)
        sys.exit(1)
    return lines

def main():
    # Read list of docs and stopwords
    doc_filenames = read_tfidf_doclist("tfidf_docs.txt")
    stopwords = read_stopwords("stopwords.txt")

    # Preprocess and write preproc_ files
    preproc_wordlists = process_documents(doc_filenames, stopwords)

    # Compute IDF across all preprocessed docs
    idf = compute_idf(preproc_wordlists)

    # For each document compute TF, TF-IDF and write tfidf_ file with top 5
    for fname, words in zip(doc_filenames, preproc_wordlists):
        tf = compute_tf(words)
        tfidf = compute_tfidf_for_doc(tf, idf)
        top5 = top_n_by_tfidf(tfidf, 5)
        
        write_tfidf_file(fname, top5)

if __name__ == "__main__":
    main()
