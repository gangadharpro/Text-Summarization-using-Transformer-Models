# 🧠 Text Summarization Using Transformer Models

This project explores and compares multiple text summarization techniques — from traditional extractive methods to advanced transformer-based models — using the **CNN/DailyMail dataset**. It also includes a **Streamlit web app** for real-time summarization.

---

## 📌 Project Overview

- **Goal**: Evaluate and compare summarization models for long-form news articles.
- **Dataset**: CNN/DailyMail news articles with human-written highlights.
- **Models Used**:
  - CNN-based Extractive Summarizer (TF-IDF + KMeans)
  - LSTM-Based Abstractive Summarizer (Base and Attention+GloVe)
  - Transformer-Based Summarizers (BART, T5)
- **Evaluation**: ROUGE Scores (ROUGE-1, ROUGE-2, ROUGE-L)

---

## 🚀 How to Run the Project

### 1. Clone the Repository
```bash
git clone https://github.com/gangadharpro/Text-Summarization-using-Transformer-Models.git
cd Text-Summarization-using-Transformer-Models
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Run Streamlit App
```bash
streamlit run app.py
```

---

## 📊 ROUGE Score Summary

| Model                        | ROUGE-1 | ROUGE-2 | ROUGE-L |
|-----------------------------|---------|---------|---------|
| CNN Extractive              | ~0.15   | ~0.06   | ~0.11   |
| LSTM Base                   | 0.000   | 0.000   | 0.000   |
| LSTM Enhanced (GloVe+Attn)  | 0.000   | 0.000   | 0.000   |
| BART                        | **0.27**| **0.10**| **0.18**|
| T5                          | 0.25    | 0.09    | 0.17    |

---

## 📂 Project Structure

```
📦 text-summarization-project/
├── app.py
├── organized_project_notebook.ipynb
├── data_loader.py
├── preprocessing.py
├── cnn_extractive.py
├── lstm_base.py
├── lstm_enhanced.py
├── transformer_models.py
├── evaluation.py
├── requirements.txt
└── README.md
```

---

## 🔗 Useful Links

- Dataset: [CNN/DailyMail on Hugging Face](https://huggingface.co/datasets/cnn_dailymail)
- BART Model: `facebook/bart-large-cnn`
- T5 Model: `t5-small`

---

## 📜 License

This project uses open-source datasets and pre-trained models. Please cite original sources where applicable.

