# Project Report: AI Resume Screening System Using NLP Techniques

## Abstract

This project implements a transparent, educational resume-screening prototype. It accepts a job description and a group of plain-text resumes, extracts job-related skills and selected qualification details, calculates text similarity using a hand-written TF-IDF implementation, and ranks candidate records using a weighted matching formula. The implementation uses Python's standard library and does not use pretrained models, external AI APIs, online datasets, or third-party machine-learning frameworks.

## 1. Problem statement

Organizations may receive many applications for one vacancy. Manually comparing every resume with the job description can take time and may lead to inconsistent first-pass comparisons. This project explores whether a small, explainable Python program can organize job-related evidence into a consistent comparison report. The system is designed to assist human review, not replace recruiter judgement.

## 2. Objectives

- Accept a job description and multiple resume text files.
- Identify recognized skills in the job description and resumes.
- Separate explicitly preferred skills from required skills using transparent rules.
- Extract explicit experience duration and basic education information.
- Implement tokenization, TF-IDF, and cosine similarity from first principles.
- Calculate and explain a matching score for each candidate.
- Rank the candidates and export a CSV summary.
- Create test cases for core algorithms and processing functions.

## 3. Scope and assumptions

The first version supports UTF-8 plain-text files only. The sample job description and all four sample resumes are fictional and were written specifically for this project. Applicant names are not needed; filenames such as `candidate_001.txt` serve as neutral identifiers. The system does not parse PDF/DOCX files, infer employment dates, evaluate personality, identify demographic attributes, or predict future job performance.

## 4. System design

```text
Job Description ──> Requirement Extraction ───────────────┐
                                                        │
Resume .txt files ──> Text Cleaning ──> Feature Extraction│
                         │                 │              │
                         │                 ├─ Skills      │
                         │                 ├─ Education   │
                         │                 └─ Experience  │
                         │                                │
                         └─ Tokenization ──> TF-IDF ──────┤
                                                        ▼
                                           Cosine Similarity
                                                        │
                                                        ▼
                                            Weighted Scoring
                                                        │
                                                        ▼
                                     Ranked, Explainable Results
                                                        │
                                                        ▼
                                                  CSV Export
```

### Main modules

1. **Text preparation:** removes labelled contact/profile lines and tokenizes text using regular expressions.
2. **Skill extraction:** checks text against the editable `SKILL_ALIASES` dictionary.
3. **Requirement extraction:** reads job-description lines and tracks required/preferred section headings.
4. **Education extraction:** recognizes a limited list of qualification levels and study fields.
5. **Experience extraction:** recognizes explicit year/month statements near experience-related words.
6. **TF-IDF:** builds sparse term-frequency/inverse-document-frequency vectors without using a prebuilt NLP package.
7. **Similarity:** calculates cosine similarity from sparse dictionaries.
8. **Scoring and ranking:** combines available components, lists missing/matched skills, and sorts the candidates.
9. **Export:** uses the standard-library `csv` module to write results.

## 5. Algorithms and formulas

### 5.1 Tokenization

Text is converted to lowercase and tokenized using a regular expression. A small stop-word list removes frequent words that add little value to the comparison.

### 5.2 Term frequency

For term `t` in document `d`:

`TF(t,d) = count(t in d) / total_tokens(d)`

### 5.3 Inverse document frequency

For `N` documents and `df(t)` documents containing term `t`:

`IDF(t) = log((N + 1) / (df(t) + 1)) + 1`

### 5.4 TF-IDF

`TFIDF(t,d) = TF(t,d) × IDF(t)`

### 5.5 Cosine similarity

For sparse vectors `A` and `B`:

`cosine(A,B) = dot(A,B) / (||A|| × ||B||)`

The similarity is multiplied by 100 to express it on a 0–100 scale.

### 5.6 Skill score

When both required and preferred skill groups exist:

`Skill Score = 100 × (0.75 × Required Coverage + 0.25 × Preferred Coverage)`

`Coverage = matched skills / total skills in that group`

If only one group exists, its coverage is used directly.

### 5.7 Experience score

When the job description specifies a minimum number of years:

`Experience Score = min(candidate years / required years, 1) × 100`

If no explicit candidate duration is found, the experience component is 0. The system does not infer years from dates.

### 5.8 Education score

When education criteria appear in the job description, the program compares recognized degree level and fields. Each recognized criterion contributes equally to this component. This is a simple keyword rule, not an academic equivalency assessment.

### 5.9 Overall score

Base component weights:

- Skills: 0.60
- Text similarity: 0.20
- Experience: 0.12
- Education: 0.08

If a component cannot be calculated because the job description does not state the relevant criterion, that component is excluded and the other available weights are normalized to sum to 1.

`Overall Score = Σ(component score × component weight) / Σ(available component weights)`

## 6. Sample data and demonstration

The included sample job is for a Junior Data Analyst. Four fictional resume files have different combinations of skills, experience, and education. On the bundled sample input, the program ranks:

| Rank | Candidate ID | Sample match score | Required skills matched |
|---:|---|---:|---:|
| 1 | candidate_001 | 84.91% | 6/6 |
| 2 | candidate_003 | 67.87% | 6/6 |
| 3 | candidate_002 | 46.39% | 3/6 |
| 4 | candidate_004 | 20.05% | 1/6 |

These figures demonstrate the program's arithmetic on synthetic examples only. They are not a benchmark, a validated accuracy measure, or evidence of job suitability.

## 7. Testing

The automated test suite contains 11 tests covering:

- stop-word removal and tokenization;
- removal of labelled personal information lines;
- skill extraction and required/preferred classification;
- explicit experience durations in years and months;
- basic education extraction;
- cosine similarity edge cases;
- skill scoring;
- ranking and explanation fields;
- CSV output creation.

Run the suite with:

`python -m unittest discover -s tests -v`

## 8. Privacy, fairness, and responsible use

The prototype uses neutral candidate IDs and excludes common labelled personal/contact lines from text similarity. It does not intentionally use protected or sensitive attributes. However, rule-based cleaning is imperfect and cannot guarantee full de-identification. Real resumes contain personal information; use synthetic or anonymized data for classroom demonstrations and protect real applicant files appropriately.

A matching percentage is not a probability of employee performance. The system may miss synonyms, misread a section heading, or misclassify an education term. Recruiters must inspect the original job requirements and evidence, correct extraction errors, and make decisions through a fair human process. The system must not automatically reject applicants.

## 9. Limitations

- The skill vocabulary is small and manually maintained.
- Simple patterns may miss alternative wording or abbreviations.
- Text similarity measures shared vocabulary, not deep semantic understanding.
- Education matching is simplistic and cannot determine credential equivalency.
- Experience extraction only recognizes explicit durations.
- Only `.txt` files are supported in this initial version.
- The score weights are illustrative and have not been validated against hiring outcomes.

## 10. Future work

Possible extensions, subject to project rules and careful evaluation, include: adding a manually reviewed role-specific skill dictionary; adding support for more document formats using approved parsing methods; expanding test data created by the project team; evaluating extraction precision/recall; and comparing alternative transparent scoring weights. Any extension should preserve explainability, privacy, and human oversight.

## Conclusion

The project demonstrates a from-scratch NLP pipeline for organizing resume evidence against a job description. It uses rule-based extraction, custom TF-IDF and cosine similarity, transparent weighted scoring, candidate ranking, and CSV reporting. Its primary value is educational: each major algorithm can be inspected, explained, and tested. The output is an aid to human review rather than a hiring decision.
