from flask import Flask, render_template, request, abort
from werkzeug.utils import secure_filename
from docx import Document
import fitz
import re
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

app = Flask(__name__)
model = SentenceTransformer('sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2')

def clean_gujarati_text(text):
    text = re.sub(r"[\"',।!?\\\-]", "", text)
    return text.strip()

def is_valid_line(line):
    if not line.strip():
        return False
    if re.match(r"^(Page|પાનું)\s*\d+\s*(of|/)\s*\d+", line, re.IGNORECASE):
        return False
    if re.sub(r"\s+", "", line).isalnum() is False and re.sub(r"\s+", "", line) == "":
        return False
    return True

def split_gujarati_questions(text):
    split_lines = re.split(r"(પ્રશ્ન\s*\d+[\.\:\)]|Que\.\s*\d+[\.\:\)]?)", text)
    cleaned = []
    buffer = ""
    for part in split_lines:
        if re.match(r"(પ્રશ્ન\s*\d+[\.\:\)]|Que\.\s*\d+[\.\:\)]?)", part):
            if buffer.strip():
                cleaned.append(clean_gujarati_text(buffer))
            buffer = part
        else:
            buffer += " " + part
    if buffer.strip():
        cleaned.append(clean_gujarati_text(buffer))
    return [line for line in cleaned if len(line.split()) >= 3 and is_valid_line(line)]

def extract_sentences(file, filename):
    ext = filename.rsplit('.', 1)[-1].lower()
    extracted = []

    try:
        if ext == 'docx':
            doc = Document(file)
            for p in doc.paragraphs:
                line = p.text.strip()
                if line and is_valid_line(line):
                    for question in split_gujarati_questions(line):
                        extracted.append((question, "Page ~"))
        elif ext == 'pdf':
            doc = fitz.open(stream=file.read(), filetype="pdf")
            for i, page in enumerate(doc, start=1):
                text = page.get_text()
                for line in text.split('\n'):
                    line = line.strip()
                    if line and is_valid_line(line):
                        for question in split_gujarati_questions(line):
                            extracted.append((question, f"Page {i}"))
        else:
            return None
    except Exception:
        return None

    return extracted if extracted else None

def detect_semantic_duplicates(file, filename):
    data = extract_sentences(file, filename)
    if not data:
        return None

    sentences, pages = zip(*data)
    embeddings = model.encode(sentences)
    duplicates = []
    seen = set()

    for i in range(len(sentences)):
        if i in seen:
            continue
        for j in range(i + 1, len(sentences)):
            if j in seen:
                continue
            score = cosine_similarity([embeddings[i]], [embeddings[j]])[0][0]
            if score >= 0.88:
                duplicates.append((sentences[i], pages[i], sentences[j], pages[j], round(score, 4)))
                seen.add(j)

    return duplicates

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    if 'file' not in request.files:
        abort(400, 'કોઈ ફાઇલ અપલોડ થઈ નથી')
    file = request.files['file']
    if file.filename == '':
        abort(400, 'ફાઇલ પસંદ કરો')
    filename = secure_filename(file.filename)
    file.seek(0)
    duplicates = detect_semantic_duplicates(file, filename)
    if duplicates is None:
        abort(400, 'ફાઇલ વાંચી શકાય તેવી .docx અથવા .pdf હોવી જોઈએ')
    return render_template('result.html', duplicates=duplicates)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000)
