# -*- coding: utf-8 -*-
"""TS15.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1iaKzoIG784AqqtHQqgJVNdh0LU87qbMm
"""

# 📦 General Purpose
import os
import re
import string
import time
import pickle
import numpy as np
import pandas as pd
from collections import Counter

# 📊 Visualization
import matplotlib.pyplot as plt
import seaborn as sns
from wordcloud import WordCloud
from matplotlib import cm

# 🧠 Machine Learning & NLP
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from sklearn.decomposition import TruncatedSVD
from sklearn.metrics import classification_report, confusion_matrix, ConfusionMatrixDisplay
from textstat import flesch_reading_ease, gunning_fog
from nltk import FreqDist, word_tokenize, pos_tag
from nltk.corpus import stopwords
from nltk.tokenize import sent_tokenize
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import nltk
from datasets import load_dataset  # ✅ Fixed typo here
nltk.download('punkt')
nltk.download('vader_lexicon')
sns.set(style="whitegrid")
nlp = spacy.load("en_core_web_sm")

# 🧬 Deep Learning (Keras & Transformers)
from tensorflow.keras.preprocessing.text import Tokenizer as KerasTokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences
from tensorflow.keras.models import Sequential, Model, load_model
from tensorflow.keras.layers import Input, Embedding, LSTM, Dense, Dropout, Bidirectional, RepeatVector, TimeDistributed
from tensorflow.keras.optimizers import Adam
from transformers import AutoTokenizer, PegasusTokenizer, PegasusForConditionalGeneration
from sentence_transformers import SentenceTransformer, util

# 🔍 Graph-based Methods
import networkx as nx

# 🌐 Web App & Utilities
import streamlit as st
from pyngrok import ngrok

# data_loader.py

def load_cnn_dailymail_dataset(subset_percent=30):
    """
    Load a subset of the CNN/DailyMail dataset (v3.0.0).
    Returns DataFrames for train, validation, and test splits.
    """
    print(f"Loading {subset_percent}% of CNN/Daily Mail dataset...")

    dataset = load_dataset("cnn_dailymail", "3.0.0", split={
        'train': f"train[:{subset_percent}%]",
        'validation': f"validation[:{subset_percent}%]",
        'test': f"test[:{subset_percent}%]"
    })

    train_df = pd.DataFrame(dataset['train'])
    val_df = pd.DataFrame(dataset['validation'])
    test_df = pd.DataFrame(dataset['test'])

    return train_df, val_df, test_df

if __name__ == "__main__":
    train_df, val_df, test_df = load_cnn_dailymail_dataset(30)
    print("Train sample:")
    print(train_df.head())

    os.makedirs("data", exist_ok=True)
    train_df.to_csv("data/cnn_train.csv", index=False)
    val_df.to_csv("data/cnn_val.csv", index=False)
    test_df.to_csv("data/cnn_test.csv", index=False)
    print("✅ Dataset saved to /data/")

# Basic text cleaning
def clean_text(text):
    text = text.lower()
    text = re.sub(r'\[(.*?)\]', '', text)
    text = re.sub(r"\s+", " ", text)
    text = re.sub(f"[{re.escape(string.punctuation)}]", "", text)
    return text.strip()

# Preprocess text for LSTM (Keras-style tokenizer)
def preprocess_lstm(texts, num_words=10000, max_len=400):
    tokenizer = KerasTokenizer(num_words=num_words, oov_token="<OOV>")
    tokenizer.fit_on_texts(texts)
    sequences = tokenizer.texts_to_sequences(texts)
    padded = pad_sequences(sequences, maxlen=max_len, padding='post', truncating='post')
    return tokenizer, padded

# Preprocess for extractive models (sentence-tokenized)
def preprocess_extractive(text):
    sentences = sent_tokenize(text)
    cleaned_sentences = [clean_text(sent) for sent in sentences]
    return cleaned_sentences

# Preprocess for transformer models using HuggingFace tokenizers
def preprocess_transformer(texts, model_name="facebook/bart-base", max_len=512):
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    tokenized_inputs = tokenizer(
        texts,
        max_length=max_len,
        padding="max_length",
        truncation=True,
        return_tensors="pt"
    )
    return tokenizer, tokenized_inputs

# 🔧 NLP Pipeline Setup, Preprocessing & Cleaned Data Generation
sns.set(style="whitegrid")
nlp = spacy.load("en_core_web_sm")
download('punkt')
download('stopwords')
download('vader_lexicon')

stop_words = set(stopwords.words('english'))

# Load data and sample subset
# Updated path to include the 'data' subdirectory
full_df = pd.read_csv("data/cnn_train.csv").dropna() # Changed this line to include subdirectory
df = full_df.sample(n=2000, random_state=42).copy()

# Preprocess subset for LSTM and CNN inputs
df['clean_article'] = df['article'].apply(lambda x: preprocess_text(x))
df['clean_summary'] = df['highlights'].apply(lambda x: preprocess_text(x))

# Save for reuse
df.to_csv("cleaned_cnn_lstm_subset.csv", index=False)

!pip install nltk
import nltk

nltk.download('punkt_tab')
# Sample testing of the preprocessing functions
sample_texts = [
    "The quick brown fox jumps over the lazy dog.",
    "Data science is an interdisciplinary field."
]

print("Cleaned:", [clean_text(t) for t in sample_texts])
print("LSTM:", preprocess_lstm(sample_texts)[1])
print("Extractive:", preprocess_extractive(sample_texts[0]))
print("Transformer:", preprocess_transformer(sample_texts)[1].input_ids.shape)

# Load Dataset
df = pd.read_csv("data/cnn_train.csv")
df.dropna(inplace=True)
# Add Length Columns
df['article_len'] = df['article'].apply(lambda x: len(str(x).split()))
df['summary_len'] = df['highlights'].apply(lambda x: len(str(x).split()))

import spacy
sns.set(style="darkgrid", palette="pastel")
nlp = spacy.load("en_core_web_sm")

#Dataset Overview
print("Dataset shape:", df.shape)
df.head()

# Length Distributions
fig, axs = plt.subplots(1, 2, figsize=(14, 5))
sns.histplot(df['article_len'], bins=50, ax=axs[0], color='#8ECFC9')
axs[0].set_title("Article Length Distribution")
sns.histplot(df['summary_len'], bins=50, ax=axs[1], color='#FFBE7A')
axs[1].set_title("Summary Length Distribution")
plt.tight_layout()
plt.show()

# Length distribution with log scale and labeled x-axis
fig, ax1 = plt.subplots(figsize=(12, 6))
article_lengths = df['article'].apply(lambda x: len(x.split()))
highlight_lengths = df['highlights'].apply(lambda x: len(x.split()))

sns.histplot(article_lengths, bins=50, kde=True, color='#66c2a5', ax=ax1, label='Articles')
sns.histplot(highlight_lengths, bins=50, kde=True, color='#fc8d62', ax=ax1, label='Highlights')
ax1.set(xscale="log")
ax1.set_title("Word Count Distribution (Log Scale)")
ax1.set_xlabel("Log of Word Count")
ax1.set_ylabel("Frequency")
ax1.set_xticks([10, 30, 100, 300, 1000, 3000])
ax1.set_xticklabels(['10', '30', '100', '300', '1k', '3k'])
plt.legend()
plt.tight_layout()
plt.show()

# Word cloud with color mask and more contrast
def plot_advanced_wordcloud(text_series, title):
    text = ' '.join(text_series.dropna())
    wordcloud = WordCloud(width=1200, height=600,
                          max_words=150,
                          background_color='black',
                          colormap='Set2').generate(text)
    plt.figure(figsize=(14, 7))
    plt.imshow(wordcloud, interpolation='bilinear')
    plt.axis('off')
    plt.title(title, fontsize=16)
    plt.show()

plot_advanced_wordcloud(df['article'], 'Advanced Word Cloud for Articles')
plot_advanced_wordcloud(df['highlights'], 'Advanced Word Cloud for Highlights')

# Most frequent words annotated and sorted
nltk.download('stopwords') # Download stopwords if not already downloaded
stop_words = set(stopwords.words('english'))
words = word_tokenize(' '.join(df['article'].values))
words = [w.lower() for w in words if w.isalnum() and w.lower() not in stop_words]
fdist = FreqDist(words)
common = fdist.most_common(20)
words, freqs = zip(*common)

plt.figure(figsize=(12, 6))
sns.barplot(x=list(freqs), y=list(words), palette='viridis')
plt.title("Top 20 Frequent Words in Articles")
for i, v in enumerate(freqs):
    plt.text(v + 5, i, str(v), color='black', va='center')
plt.xlabel("Frequency")
plt.ylabel("Words")
plt.show()

# TF-IDF with word grouping
tfidf = TfidfVectorizer(max_features=25, stop_words='english')
X = tfidf.fit_transform(df['article'][:1000])
tfidf_scores = np.asarray(X.mean(axis=0)).flatten()
words = tfidf.get_feature_names_out()

sorted_idx = np.argsort(tfidf_scores)[::-1]
words = [words[i] for i in sorted_idx]
scores = [tfidf_scores[i] for i in sorted_idx]

plt.figure(figsize=(12, 6))
sns.barplot(x=scores, y=words, palette='crest')
plt.title("Top TF-IDF Words in Articles")
plt.xlabel("Average TF-IDF Score")
plt.ylabel("Words")
plt.tight_layout()
plt.show()

#Sentimental Analysis of Articles and Summaries
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import nltk

# Download the VADER lexicon if not already downloaded
nltk.download('vader_lexicon')

# Sentiment Analysis Function
def plot_sentiment_analysis(text_series, title, sample_size=1000):
    sid = SentimentIntensityAnalyzer()
    text_sample = text_series[:sample_size].astype(str)
    sentiments = text_sample.apply(lambda x: sid.polarity_scores(x)['compound'])
    plt.figure(figsize=(10, 5))
    sns.histplot(sentiments, bins=50, kde=True, color='skyblue')
    plt.title(title)
    plt.xlabel('Sentiment Score')
    plt.ylabel('Frequency')
    plt.show()

plot_sentiment_analysis(df['article'], 'Sentiment Analysis of Articles')
plot_sentiment_analysis(df['highlights'], 'Sentiment Analysis of Highlights')

# Named Entity Plot Function
def plot_named_entities(text_series, title, batch_size=100):
    entity_counts = Counter()
    for i in range(0, min(len(text_series), 1000), batch_size):
        text_sample = " ".join(text_series[i : i + batch_size])
        doc = nlp(text_sample)
        entity_counts.update(ent.label_ for ent in doc.ents)

    if entity_counts:
        plt.figure(figsize=(10, 5))
        sns.barplot(x=list(entity_counts.values()), y=list(entity_counts.keys()), palette='flare')
        plt.title(title)
        plt.xlabel('Frequency')
        plt.ylabel('Entity Type')
        plt.show()
    else:
        print(f"No named entities found in the provided text for {title}.")

plot_named_entities(df['article'], 'Named Entities in Articles')
plot_named_entities(df['highlights'], 'Named Entities in Highlights')

# POS Tag Plot Function
def plot_pos_tags(text_series, title, batch_size=100):
    pos_counts = Counter()
    for i in range(0, min(len(text_series), 1000), batch_size):
        text_batch = " ".join(text_series[i : i + batch_size])
        doc = nlp(text_batch)
        pos_counts.update(token.pos_ for token in doc)

    plt.figure(figsize=(10, 5))
    sns.barplot(x=list(pos_counts.values()), y=list(pos_counts.keys()), palette='crest')
    plt.title(title)
    plt.xlabel('Frequency')
    plt.ylabel('POS Tag')
    plt.show()

plot_pos_tags(df['article'], 'POS Tags in Articles')
plot_pos_tags(df['highlights'], 'POS Tags in Highlights')

# N-gram Frequency Plot Function
def plot_top_ngrams(text_series, ngram_range=(2, 2), top_n=20, title="Top N-grams"):
    vec = CountVectorizer(ngram_range=ngram_range, stop_words='english').fit(text_series)
    bag_of_words = vec.transform(text_series)
    sum_words = bag_of_words.sum(axis=0)
    words_freq = [(word, sum_words[0, idx]) for word, idx in vec.vocabulary_.items()]
    sorted_words = sorted(words_freq, key=lambda x: x[1], reverse=True)[:top_n]
    ngrams, counts = zip(*sorted_words)

    plt.figure(figsize=(12, 6))
    sns.barplot(x=list(counts), y=list(ngrams), palette="Spectral")
    plt.title(title)
    plt.xlabel("Frequency")
    plt.ylabel("N-gram")
    plt.tight_layout()
    plt.show()

# Apply for bigrams and trigrams
plot_top_ngrams(df['article'].dropna().astype(str)[:1000], ngram_range=(2, 2), title="Top Bigrams in Articles")
plot_top_ngrams(df['article'].dropna().astype(str)[:1000], ngram_range=(3, 3), title="Top Trigrams in Articles")

import re
import string
import numpy as np
import networkx as nx
from nltk.tokenize import sent_tokenize
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import TruncatedSVD

def clean_text(text):
    text = text.lower()
    text = re.sub(r'\[(.*?)\]', '', text)
    text = re.sub(r"\s+", " ", text)
    text = re.sub(f"[{re.escape(string.punctuation)}]", "", text)
    return text.strip()

def textrank_summarize(text, num_sentences=3):
    sentences = sent_tokenize(text)
    cleaned = [clean_text(sent) for sent in sentences]
    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform(cleaned)
    similarity_matrix = (tfidf_matrix * tfidf_matrix.T).toarray()
    np.fill_diagonal(similarity_matrix, 0)
    graph = nx.from_numpy_array(similarity_matrix)
    scores = nx.pagerank(graph)
    ranked_sentences = sorted(((scores[i], s) for i, s in enumerate(sentences)), reverse=True)
    return " ".join([s for _, s in ranked_sentences[:num_sentences]])

def lsa_summarize(text, num_sentences=3):
    sentences = sent_tokenize(text)
    cleaned = [clean_text(sent) for sent in sentences]
    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform(cleaned)
    svd = TruncatedSVD(n_components=1)
    scores = svd.fit_transform(tfidf_matrix)
    ranked = sorted(((score, s) for score, s in zip(scores, sentences)), reverse=True)
    return " ".join([s for _, s in ranked[:num_sentences]])

# 🧠 Train and Save LSTM Text Summarization Model
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences

# Load pre-cleaned dataset (2000 samples)
df = pd.read_csv("cleaned_cnn_lstm_subset.csv")
df['clean_summary'] = df['clean_summary'].apply(lambda x: "starttoken " + x + " endtoken")

# Parameters
VOCAB_SIZE = 10000
MAX_INPUT_LEN = 400
MAX_SUMMARY_LEN = 50

# Prepare inputs and summaries
input_texts = df['clean_article'].astype(str)
target_texts = df['clean_summary'].astype(str)

# Tokenize
input_tokenizer = Tokenizer(num_words=VOCAB_SIZE, oov_token="<OOV>")
target_tokenizer = Tokenizer(num_words=VOCAB_SIZE, oov_token="<OOV>")
input_tokenizer.fit_on_texts(input_texts)
target_tokenizer.fit_on_texts(target_texts)

input_seq = pad_sequences(input_tokenizer.texts_to_sequences(input_texts), maxlen=MAX_INPUT_LEN, padding='post')
target_seq = pad_sequences(target_tokenizer.texts_to_sequences(target_texts), maxlen=MAX_SUMMARY_LEN, padding='post')
target_seq = np.expand_dims(target_seq, -1)

# Build simple LSTM model
model = Sequential([
    Embedding(VOCAB_SIZE, 128),
    LSTM(256),
    RepeatVector(MAX_SUMMARY_LEN),
    LSTM(256, return_sequences=True),
    TimeDistributed(Dense(VOCAB_SIZE, activation='softmax'))
])

# ✅ Force model build to show summary properly
model.build(input_shape=(None, MAX_INPUT_LEN))
model.summary()

# Compile and train
model.compile(optimizer='adam', loss='sparse_categorical_crossentropy')
model.fit(input_seq, target_seq, batch_size=64, epochs=2, validation_split=0.1)

# Save model and tokenizers
model.save("lstm_summarizer_model.h5")
with open("lstm_tokenizers.pkl", "wb") as f:
    pickle.dump((input_tokenizer, target_tokenizer), f)

print("✅ Model and tokenizers saved!")

# pegasus_summarizer_inference.py
import pandas as pd
from transformers import PegasusTokenizer, PegasusForConditionalGeneration

# Load cleaned test data (subset)
df = pd.read_csv("cleaned_cnn_lstm_subset.csv").sample(100, random_state=42)
articles = df['clean_article'].tolist()

# Load pretrained PEGASUS model
tokenizer = PegasusTokenizer.from_pretrained("google/pegasus-cnn_dailymail")
model = PegasusForConditionalGeneration.from_pretrained("google/pegasus-cnn_dailymail")

# Summarization function
def summarize(text):
    inputs = tokenizer([text], return_tensors="pt", truncation=True, max_length=512)
    summary_ids = model.generate(inputs["input_ids"], max_length=64, num_beams=4, early_stopping=True)
    return tokenizer.decode(summary_ids[0], skip_special_tokens=True)

# Generate summaries
summaries = [summarize(article) for article in articles]

# Save results
df_result = df.copy()
df_result["pegasus_summary"] = summaries
df_result.to_csv("pegasus_pretrained_inference.csv", index=False)
print("✅ Inference complete. Summaries saved to 'pegasus_pretrained_inference.csv'")

#CNN Model Training
from tensorflow.keras.layers import Embedding, Conv1D, GlobalMaxPooling1D, RepeatVector, LSTM, TimeDistributed, Dense
from tensorflow.keras.callbacks import EarlyStopping

# Load cleaned dataset
df = pd.read_csv("cleaned_cnn_lstm_subset.csv")
df['clean_summary'] = df['clean_summary'].apply(lambda x: "starttoken " + x + " endtoken")

# Parameters
VOCAB_SIZE = 10000
MAX_INPUT_LEN = 400
MAX_TARGET_LEN = 50

# Tokenization
input_texts = df['clean_article'].astype(str)
target_texts = df['clean_summary'].astype(str)

input_tokenizer = Tokenizer(num_words=VOCAB_SIZE, oov_token="<OOV>")
target_tokenizer = Tokenizer(num_words=VOCAB_SIZE, oov_token="<OOV>")
input_tokenizer.fit_on_texts(input_texts)
target_tokenizer.fit_on_texts(target_texts)

input_seq = pad_sequences(input_tokenizer.texts_to_sequences(input_texts), maxlen=MAX_INPUT_LEN, padding='post')
target_seq = pad_sequences(target_tokenizer.texts_to_sequences(target_texts), maxlen=MAX_TARGET_LEN, padding='post')
target_seq = np.expand_dims(target_seq, -1)

X_train, X_val, y_train, y_val = train_test_split(input_seq, target_seq, test_size=0.1, random_state=42)

# Define the model
model = Sequential([
    Embedding(VOCAB_SIZE, 128, input_length=MAX_INPUT_LEN),
    Conv1D(128, 5, activation='relu'),
    GlobalMaxPooling1D(),
    RepeatVector(MAX_TARGET_LEN),
    LSTM(256, return_sequences=True),
    TimeDistributed(Dense(VOCAB_SIZE, activation='softmax'))
])

# ✅ Build the model before summary to get full output shapes and param counts
model.build(input_shape=(None, MAX_INPUT_LEN))

# Show the proper summary
model.summary()

# Compile and train
model.compile(optimizer='adam', loss='sparse_categorical_crossentropy')
early_stop = EarlyStopping(monitor='val_loss', patience=2, restore_best_weights=True)
model.fit(X_train, y_train, epochs=5, batch_size=64, validation_data=(X_val, y_val), callbacks=[early_stop])

#CNN Summary Generation Function

from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.sequence import pad_sequences
import pickle

# Load model & tokenizer
model = load_model("cnn_summarizer_model.h5")
with open("cnn_tokenizers.pkl", "rb") as f:
    input_tokenizer, target_tokenizer = pickle.load(f)

index_to_word = {i: w for w, i in target_tokenizer.word_index.items()}

# Summary generation function
def cnn_generate_summary(input_text):
    sequence = input_tokenizer.texts_to_sequences([input_text])
    padded = pad_sequences(sequence, maxlen=400, padding='post')
    prediction = model.predict(padded)[0]
    predicted_ids = prediction.argmax(axis=1)
    words = [index_to_word.get(i, '') for i in predicted_ids]
    summary = []
    for word in words:
        if word == 'endtoken': break
        if word and word != 'starttoken': summary.append(word)
    return ' '.join(summary)

#Full Model Comparison Function
from extractive_models import textrank_summarize, lsa_summarize
from lstm_model import generate_summary as lstm_summary
from transformer_utils import predict_transformer_summary

def compare_summaries(article_text):
    return {
        "TextRank": textrank_summarize(article_text),
        "LSA": lsa_summarize(article_text),
        "LSTM": lstm_summary(article_text),
        "Transformer": predict_transformer_summary(article_text),
        "CNN": cnn_generate_summary(article_text)
    }

#ROUGE Evaluation + Ranking
from rouge_score import rouge_scorer

def evaluate_summaries(summary_dict, reference_summary):
    scorer = rouge_scorer.RougeScorer(['rouge1', 'rouge2', 'rougeL'], use_stemmer=True)
    scores = {}
    for model_name, summary in summary_dict.items():
        result = scorer.score(reference_summary, summary)
        scores[model_name] = {
            'ROUGE-1': result['rouge1'].fmeasure,
            'ROUGE-2': result['rouge2'].fmeasure,
            'ROUGE-L': result['rougeL'].fmeasure
        }
    return scores

def rank_models(rouge_scores):
    ranked = []
    for model, scores in rouge_scores.items():
        avg = sum(scores.values()) / len(scores)
        ranked.append((model, avg))
    ranked.sort(key=lambda x: x[1], reverse=True)
    return ranked

#Plotting + Example Execution

import matplotlib.pyplot as plt
import pandas as pd

def plot_rouge_scores(rouge_scores):
    df = pd.DataFrame(rouge_scores).T
    df.plot(kind='bar', figsize=(10, 6))
    plt.title("ROUGE Scores by Model")
    plt.ylabel("F1 Score")
    plt.xticks(rotation=45)
    plt.grid(True)
    plt.tight_layout()
    plt.show()

# Run example
df = pd.read_csv("cleaned_cnn_lstm_subset.csv")
article = df['clean_article'].iloc[0]
reference = df['clean_summary'].iloc[0]

summaries = compare_summaries(article)
rouge = evaluate_summaries(summaries, reference)
ranked = rank_models(rouge)

# Print
for model, summary in summaries.items():
    print(f"\n🧠 {model}:\n{summary}\n{'-'*80}")

print("\n📊 ROUGE Scores:")
for model, score in rouge.items():
    print(f"{model}: {score}")

print("\n🏆 Ranked Models:")
for i, (model, score) in enumerate(ranked, 1):
    print(f"{i}. {model} - Avg ROUGE: {score:.4f}")

plot_rouge_scores(rouge)