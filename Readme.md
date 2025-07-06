# Gujarati AI Duplicate Checker App

This is an AI-powered Flask web application that detects semantically similar or duplicate sentences from uploaded `.docx` and `.pdf` documents. It uses multilingual sentence embeddings to intelligently identify meaning-based duplicates.

---

## 🚀 Features

- Upload `.docx` or `.pdf` files
- AI-powered duplicate sentence detection
- Semantic understanding using `sentence-transformers`
- Modern UI with gradient animation
- Dockerized for easy deployment

---

## 🐳 Docker Usage

### Step 1: Build the Docker image

```bash
docker build -t gujarati-ai-app .

