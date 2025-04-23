# Text-Summarization-using-Transformer-Models
This project compares Transformer-based, CNN-based extractive, and LSTM-based abstractive models for long-form text summarization. It evaluates accuracy, readability, and coherence using the CNN/Daily Mail dataset, aiming to determine if Transformers outperform traditional models. 

# 🧠 Text Summarization Using Transformer Models

This project explores and compares multiple text summarization techniques — from traditional extractive methods to advanced transformer-based models — using the **CNN/DailyMail dataset**. It also includes a **Streamlit web app** to interact with summarization models in real-time.

---

## 📌 Project Overview

- 🔍 **Goal**: Evaluate which model best balances accuracy and efficiency for long-form text summarization.
- 🧪 **Models Implemented**:
  - CNN-based Extractive Summarization (TF-IDF + KMeans)
  - LSTM Abstractive Summarization (Base + Enhanced with Attention & GloVe)
  - Transformer-Based Abstractive Summarizers (BART & T5)
- 📊 **Evaluation Metric**: ROUGE (ROUGE-1, ROUGE-2, ROUGE-L)
- 🌐 **Live Demo**: Streamlit app for input article → model-wise summary comparison

---

## 📂 Project Structure

```bash
├── data_loader.py               # Dataset reading and subsampling
├── preprocessing.py            # Text cleaning, tokenization, EDA
├── cnn_extractive.py           # TF-IDF + KMeans based summarizer
├── lstm_base.py                # Basic LSTM seq2seq summarizer
├── lstm_enhanced.py           # LSTM with attention and GloVe
├── transformer_models.py       # BART and T5 summarizers using Hugging Face
├── evaluation.py               # ROUGE metrics + visualizations
├── app.py                      # Streamlit app
├── requirements.txt            # Python dependencies
└── organized_project_notebook.ipynb  # All code in one structured notebook
