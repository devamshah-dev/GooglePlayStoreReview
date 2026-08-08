# Google Play Review Classification Platform

End-to-end web application that classifies Google Play Store reviews by **sentiment** and **theme** using classical CPU-based machine learning (TF-IDF + Logistic Regression / Multinomial Naive Bayes / Linear SVM).

No TensorFlow, PyTorch, CUDA, Docker, or LLMs are required for the core demo.

---

## 1. Project overview

| Capability | Description |
|---|---|
| Single review analysis | Paste a review → sentiment + theme |
| CSV batch analysis | Upload reviews CSV → predictions + stats |
| Dashboard | Totals, averages, Recharts distributions |
| Download | Processed CSV with prediction columns |

**Sentiment labeling (training only):** derived from star rating

- 1–2 → Negative
- 3 → Neutral
- 4–5 → Positive

At prediction time, sentiment is inferred **only from review text**.

**Theme labels (training bootstrap):** keyword/rule-based automatic labels from `training/create_theme_labels.py`. These are **not** human-annotated ground truth; they bootstrap the prototype classifier.

Theme categories: Crash, Login Problem, Performance Issue, UI Problem, Feature Request, Ads Complaint, Security Concern, Payment Problem, General Praise, Other.

---

## 2. Architecture

```
React (Vite)  --HTTP JSON / multipart-->  FastAPI
                                            |
                                            +-- text cleaner
                                            +-- TF-IDF vectorizers (joblib)
                                            +-- best sentiment model
                                            +-- best theme model
                                            +-- statistics service
```

Training pipeline (offline):

```
raw CSV → prepare_data → theme rules + rating→sentiment
       → train_sentiment / train_theme
       → models/*.pkl + artifacts/metrics/*.json
```

---

## 3. Folder structure

```
GooglePlayReviewPlatform/
├── backend/
│   ├── app/
│   │   ├── api/            # /predict, /upload
│   │   ├── preprocessing/  # text_cleaner.py
│   │   ├── services/       # predictor, statistics
│   │   ├── schemas/
│   │   ├── utils/          # CSV column detection
│   │   ├── config.py
│   │   └── main.py
│   ├── training/           # prepare / label / train / evaluate
│   ├── models/             # *.pkl artifacts
│   ├── artifacts/metrics/  # evaluation JSON
│   ├── datasets/raw/       # place CSVs here (includes sample_reviews.csv)
│   ├── datasets/processed/
│   ├── tests/
│   └── requirements.txt
├── frontend/               # React + Vite + Recharts
├── README.md
└── .gitignore
```

---

## 4. Installation (Windows 11 PowerShell)

Open PowerShell in the project root:

```powershell
cd C:\Users\DEVAMDR\Downloads\GooglePlayReviewPlatform
```

### 5. Python virtual environment

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r backend\requirements.txt
```

If script activation is blocked:

```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```

### 6. Frontend setup

```powershell
cd frontend
npm install
cd ..
```

---

## 7. Dataset placement

Place Google Play review CSVs in:

```text
backend\datasets\raw\
```

A synthetic development file is included:

```text
backend\datasets\raw\sample_reviews.csv
```

**This sample is NOT a real Play Store dataset.** It exists only for local training and demos.

### Expected CSV columns

The backend auto-detects common names:

| Role | Accepted names |
|---|---|
| Rating | `Rating`, `rating`, `score`, `Score` |
| Review | `Review`, `review`, `Review Text`, `review_text`, `reviewText`, `Content`, `content` |

Normalized internally to `rating` and `review`. Extra columns are preserved on upload. If the review column cannot be found, the API returns a clear error.

For **training**, both rating and review are required. For **upload prediction**, review is required; rating is optional (used for dashboard averages when present).

---

## 8. Model training

From the project root with the venv activated:

```powershell
.\.venv\Scripts\Activate.ps1
cd backend
python -m training.train_all
```

Or step-by-step:

```powershell
cd backend
python -m training.prepare_data
python -m training.train_sentiment
python -m training.train_theme
```

To train on a specific CSV:

```powershell
python -m training.train_all --input datasets\raw\your_file.csv
```

Outputs:

- `backend\models\sentiment_vectorizer.pkl`
- `backend\models\sentiment_model.pkl`
- `backend\models\theme_vectorizer.pkl`
- `backend\models\theme_model.pkl`
- `backend\artifacts\metrics\sentiment_metrics.json`
- `backend\artifacts\metrics\theme_metrics.json`

Models are selected by **weighted F1** on a held-out stratified test set (TF-IDF fitted only on training data).

---

## 9. Running the backend

```powershell
.\.venv\Scripts\Activate.ps1
cd backend
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

API docs: http://127.0.0.1:8000/docs  
Health: http://127.0.0.1:8000/health

---

## 10. Running the frontend

In a second PowerShell window:

```powershell
cd C:\Users\DEVAMDR\Downloads\GooglePlayReviewPlatform\frontend
npm run dev
```

Open: http://127.0.0.1:5173

Optional API base override:

```powershell
$env:VITE_API_BASE="http://127.0.0.1:8000"
npm run dev
```

---

## 11. API endpoints

| Method | Path | Purpose |
|---|---|---|
| GET | `/` | Health / status |
| GET | `/health` | Health + models_loaded |
| POST | `/predict` | Single review JSON |
| POST | `/upload` | CSV multipart upload |
| GET | `/metrics` | Training evaluation metrics |

### Example `/predict` body

```json
{
  "review": "The app crashes after the latest update."
}
```

### Example response

```json
{
  "success": true,
  "review": "The app crashes after the latest update.",
  "sentiment": "Negative",
  "theme": "Crash"
}
```

---

## 12. Testing

With models trained and venv active:

```powershell
cd backend
python -m pytest tests -q
```

Manual smoke checks (with backend running):

```powershell
curl -X POST http://127.0.0.1:8000/predict -H "Content-Type: application/json" -d "{\"review\":\"The app crashes every time I open it.\"}"
```

Expected theme: **Crash**

```powershell
curl -X POST http://127.0.0.1:8000/predict -H "Content-Type: application/json" -d "{\"review\":\"I cannot login to my account.\"}"
```

Expected theme: **Login Problem**

```powershell
curl -X POST http://127.0.0.1:8000/predict -H "Content-Type: application/json" -d "{\"review\":\"Excellent application. I love it.\"}"
```

Expected sentiment: **Positive**

---

## 13. Troubleshooting

| Issue | Fix |
|---|---|
| `Models are not loaded` | Run `python -m training.train_all` then restart uvicorn |
| CORS / network error in browser | Ensure backend is on `127.0.0.1:8000` and frontend on `5173` |
| CSV column error | Ensure a review column matches the accepted names above |
| `Activate.ps1` blocked | `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` |
| npm not found | Install Node.js LTS from https://nodejs.org |
| Slow first prediction | Normal cold start; models load once at API startup |

---

## 14. Important notes

- Theme training labels are **automatically generated** (keyword rules), not human ground truth.
- The included `sample_reviews.csv` is synthetic for development only.
- No user uploads are permanently stored on disk; results are returned in the API response for download.
- Keep preprocessing light — suitable for TF-IDF; negation cues such as “NOT” are preserved.
