# AI Resume Screening System — From-Scratch Edition

A Jupyter Notebook project that compares plain-text resumes against a job description and produces an explainable, recruiter-review ranking.

**Development approach:** the text processing, skill matching, TF-IDF, cosine similarity, scoring, ranking, and CSV export are written for this project using Python's standard library. There is no pretrained model, external AI API, Streamlit app, downloaded resume dataset, or scikit-learn dependency.

## 1. What the project does

1. Reads a job description and multiple `.txt` resumes.
2. Finds skills using a small, editable dictionary of canonical skills and aliases.
3. Separates required and preferred skills using section headings and priority words.
4. Extracts explicitly stated experience durations.
5. Extracts basic education level and study-field terms.
6. Tokenizes the text and calculates TF-IDF vectors with code written in `resume_screening.py`.
7. Calculates cosine similarity from sparse dictionaries.
8. Computes transparent component scores and a final weighted score.
9. Ranks candidates and shows matched/missing requirements.
10. Exports an explanation-oriented CSV report.

This is a prototype for learning and decision support. It does not make hiring decisions and must not be used to automatically accept or reject applicants.

## 2. Project structure

```text
AI_Resume_Screening_From_Scratch/
├── resume_screening.ipynb       # Main step-by-step Jupyter Notebook
├── resume_screening.py          # All project algorithms, written from scratch
├── requirements.txt             # Jupyter Notebook only; algorithm uses stdlib
├── README.md
├── data/
│   ├── job_description.txt      # Fictional sample job description
│   └── resumes/                 # Four fictional sample resumes
├── tests/
│   └── test_resume_screening.py # Automated unit tests
├── docs/
│   └── PROJECT_REPORT.md        # Academic-style project report
└── outputs/                     # CSV report is written here
```

## 3. Requirements

- Python 3.10 or newer
- Jupyter Notebook (or JupyterLab)
- No third-party machine-learning or NLP package is required

The algorithm uses only these Python standard-library modules: `re`, `math`, `csv`, `pathlib`, `collections`, and `typing`.

## 4. Setup and run

Open a terminal in the project folder.

### Create and activate a virtual environment (recommended)

Windows:

```bash
python -m venv .venv
.venv\Scripts\activate
```

macOS/Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### Install Jupyter

```bash
python -m pip install -r requirements.txt
```

If Jupyter is already installed, this install step is not necessary.

### Start Jupyter Notebook

```bash
jupyter notebook
```

Open `resume_screening.ipynb` and run the cells from top to bottom. Keep the notebook and `resume_screening.py` in the same folder.

## 5. Run the tests

From the project root:

```bash
python -m unittest discover -s tests -v
```

The tests verify tokenization, removal of personal-information lines, skill extraction, requirement classification, experience/education extraction, cosine similarity, scoring, ranking, and CSV export.

## 6. Use your own job description and resumes

1. Replace the contents of `data/job_description.txt` with your own job description.
2. Add one plain-text resume per file in `data/resumes/`.
3. Give files neutral names such as `candidate_005.txt`, `candidate_006.txt`, and so on. Do not use applicant names as filenames.
4. Run the notebook again from the first cell.
5. Inspect `required_skills`, `preferred_skills`, extracted education, and experience to check whether the simple rules understood the text correctly.
6. Review the ranking and open `outputs/candidate_screening_results.csv`.

The starter version accepts **plain text (`.txt`) only**. This is deliberate: it keeps document parsing transparent and avoids adding a PDF/DOCX parsing dependency before the core NLP logic is understood. For an initial demonstration, you can paste resume text into `.txt` files yourself.

## 7. How scoring works

The base weights are:

| Component | Base weight | Meaning |
|---|---:|---|
| Skill score | 60% | Required skill coverage is weighted 75% within this component; preferred skill coverage is weighted 25% |
| TF-IDF text similarity | 20% | Similarity between job-description and resume terms |
| Experience | 12% | Explicit candidate experience compared with an explicit job minimum |
| Education | 8% | Simple degree-level and field comparison when the job description specifies them |

If the job description does not contain an extractable experience or education requirement, that component is omitted and the remaining component weights are re-normalized. The exact formula and all component scores are returned with each candidate.

The final score is **not a probability of job performance**. It is a weighted matching indicator based on this small rule set.

## 8. Important limitations and responsible use

- This is an educational prototype, not a validated hiring assessment.
- The included resumes and job description are fictional examples written specifically for this project; they are not real applicant records or downloaded data.
- The skill dictionary is small and must be reviewed/expanded for each domain.
- The priority parser uses simple section headings and keywords. Always inspect the parsed requirements before interpreting scores.
- Experience extraction recognizes explicit statements such as `2 years of professional experience`. It does not infer dates or add overlapping jobs.
- Education extraction recognizes only the degree and field terms listed in the source file.
- PDF, DOCX, scanned-resume OCR, semantic embeddings, and generative AI are not included.
- Names, contact details, and labelled demographic lines are excluded from the text-similarity tokenization. Candidate filenames should still be neutral IDs. This simple cleaning is not a guarantee that all sensitive information has been removed.
- Do not score age, gender, race, religion, caste, disability, marital status, nationality, photographs, or other protected/sensitive characteristics. Do not use the output as the sole basis for employment decisions. A human reviewer must examine original evidence and apply consistent, lawful criteria.

## 9. Where to customize

- `SKILL_ALIASES` in `resume_screening.py`: add or remove skill names and aliases.
- `STOP_WORDS`: adjust text preprocessing.
- `FIELD_ALIASES` and `DEGREE_PATTERNS`: adjust education vocabulary.
- `BASE_WEIGHTS`: change component weights only with a documented reason and evaluation.
- `extract_skill_requirements`: refine how your chosen job-description format marks required and preferred skills.

## 10. Reproducibility

No web services are called by the code. After Jupyter is installed, the analysis and tests run locally and do not require an internet connection.
