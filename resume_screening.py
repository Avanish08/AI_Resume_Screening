

from __future__ import annotations

import csv
import math
import re
from collections import Counter
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Sequence, Set, Tuple



SKILL_ALIASES: Dict[str, Sequence[str]] = {
    "Python": ("python",),
    "SQL": ("sql", "structured query language"),
    "Microsoft Excel": ("excel", "microsoft excel"),
    "Power BI": ("power bi", "powerbi"),
    "Tableau": ("tableau",),
    "Pandas": ("pandas",),
    "NumPy": ("numpy",),
    "Matplotlib": ("matplotlib",),
    "Seaborn": ("seaborn",),
    "Statistics": ("statistics", "statistical analysis"),
    "Data cleaning": ("data cleaning", "cleaning data", "data cleansing"),
    "Data visualization": ("data visualization", "data visualisation", "data viz"),
    "Machine learning": ("machine learning", "ml"),
    "Natural language processing": ("natural language processing", "nlp"),
    "Deep learning": ("deep learning",),
    "Data analysis": ("data analysis", "data analytics"),
    "Data modelling": ("data modeling", "data modelling"),
    "ETL": ("etl", "extract transform load"),
    "Database management": ("database management", "database design"),
    "Git": ("git", "version control"),
    "Communication": ("communication", "written communication", "verbal communication"),
    "Problem solving": ("problem solving", "problem-solving", "analytical thinking"),
    "Project management": ("project management",),
    "Java": ("java",),
    "C++": ("c++",),
    "JavaScript": ("javascript", "js"),
    "HTML": ("html",),
    "CSS": ("css",),
}


STOP_WORDS: Set[str] = {
    "a", "an", "and", "are", "as", "at", "be", "been", "being", "by",
    "for", "from", "has", "have", "had", "he", "her", "his", "i", "in",
    "into", "is", "it", "its", "me", "my", "of", "on", "or", "our",
    "ours", "she", "that", "the", "their", "them", "there", "these",
    "they", "this", "to", "was", "we", "were", "will", "with", "you",
    "your", "years", "year", "work", "working", "experience", "experienced",
    "required", "preferred", "candidate", "candidates", "job", "role", "team",
    "responsibilities", "responsibility", "skills", "skill", "ability", "able",
}

PERSONAL_LINE_LABELS = re.compile(
    r"^\s*(?:name|email|e-mail|phone|mobile|contact|address|location|dob|date of birth|"
    r"age|gender|sex|marital status|nationality|religion|caste|ethnicity|passport|"
    r"photo|photograph|linkedin|github|website|portfolio)\s*[:|\-]",
    re.IGNORECASE,
)
EMAIL_PATTERN = re.compile(r"\b[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}\b")
PHONE_PATTERN = re.compile(r"(?<!\w)(?:\+?\d[\d ()\-]{7,}\d)(?!\w)")
URL_PATTERN = re.compile(r"\b(?:https?://|www\.)\S+", re.IGNORECASE)


DEGREE_PATTERNS: Dict[str, re.Pattern[str]] = {
    "phd": re.compile(r"\b(?:ph\.?d\.?|doctor of philosophy)\b", re.IGNORECASE),
    "master": re.compile(
        r"\b(?:master(?:'s)?|m\.?s\.?|m\.?sc\.?|m\.?tech\.?|mca|mba|mcom)\b",
        re.IGNORECASE,
    ),
    "bachelor": re.compile(
        r"\b(?:bachelor(?:'s)?|b\.?s\.?|b\.?sc\.?|b\.?tech\.?|b\.?e\.?|bca|bba|bcom)\b",
        re.IGNORECASE,
    ),
    "diploma": re.compile(r"\b(?:diploma|associate degree)\b", re.IGNORECASE),
}
DEGREE_RANK = {"unknown": 0, "diploma": 1, "bachelor": 2, "master": 3, "phd": 4}

FIELD_ALIASES: Dict[str, Sequence[str]] = {
    "Computer science": ("computer science", "computer engineering", "computer applications"),
    "Statistics": ("statistics", "statistical science"),
    "Mathematics": ("mathematics", "mathematical sciences", "maths"),
    "Data science": ("data science", "data analytics"),
    "Information technology": ("information technology", "information systems"),
    "Commerce": ("commerce", "accounting", "finance"),
    "Engineering": ("engineering",),
    "Physics": ("physics",),
    "Economics": ("economics",),
}

REQUIRED_MARKERS = re.compile(
    r"\b(required|must[- ]have|essential|mandatory|minimum|proficient in|strong skills in)\b",
    re.IGNORECASE,
)
PREFERRED_MARKERS = re.compile(
    r"\b(preferred|desirable|nice[- ]to[- ]have|bonus|a plus|would be an advantage|good to have)\b",
    re.IGNORECASE,
)



def read_text_file(path: str | Path) -> str:
    """Read a UTF-8 plain-text input file."""
    return Path(path).read_text(encoding="utf-8", errors="replace")


def remove_personal_information_lines(text: str) -> str:
    """Remove labelled personal-profile lines and common contact identifiers."""
    kept_lines: List[str] = []
    for line in text.splitlines():
        if PERSONAL_LINE_LABELS.search(line):
            continue
        cleaned = EMAIL_PATTERN.sub(" ", line)
        cleaned = PHONE_PATTERN.sub(" ", cleaned)
        cleaned = URL_PATTERN.sub(" ", cleaned)
        kept_lines.append(cleaned)
    return "\n".join(kept_lines)


def tokenize(text: str) -> List[str]:
    """Tokenize text using a small hand-written regular-expression tokenizer."""
    safe_text = remove_personal_information_lines(text).lower()
    safe_text = EMAIL_PATTERN.sub(" ", safe_text)
    safe_text = URL_PATTERN.sub(" ", safe_text)
    tokens = re.findall(r"[a-z][a-z0-9+#]*(?:\.[a-z0-9+#]+)*", safe_text)
    return [token for token in tokens if token not in STOP_WORDS and len(token) > 1]


def _alias_pattern(alias: str) -> re.Pattern[str]:
    """Create a case-insensitive phrase matcher with flexible whitespace."""
    escaped = re.escape(alias.strip()).replace(r"\ ", r"\s+")
    return re.compile(r"(?<!\w)" + escaped + r"(?!\w)", re.IGNORECASE)


_COMPILED_SKILL_PATTERNS: Dict[str, Sequence[re.Pattern[str]]] = {
    skill: tuple(_alias_pattern(alias) for alias in aliases)
    for skill, aliases in SKILL_ALIASES.items()
}


def find_skills(text: str) -> Set[str]:
    """Return canonical skills found in text using the editable skill dictionary."""
    text = remove_personal_information_lines(text)
    found: Set[str] = set()
    for canonical, patterns in _COMPILED_SKILL_PATTERNS.items():
        if any(pattern.search(text) for pattern in patterns):
            found.add(canonical)
    return found


def split_sentences(text: str) -> List[str]:
    """A lightweight sentence splitter used only for showing evidence."""
    chunks = re.split(r"(?<=[.!?])\s+|\n+", text)
    return [chunk.strip(" \t-•") for chunk in chunks if chunk.strip(" \t-•")]


def extract_skill_requirements(job_description: str) -> Tuple[Set[str], Set[str]]:
    """Extract required and preferred skills, respecting simple section headings.

    Skills mentioned without a priority marker default to required. This is a
    transparent heuristic; review the returned lists before using the ranking.
    """
    required: Set[str] = set()
    preferred: Set[str] = set()
    current_section: Optional[str] = None

    for line in job_description.splitlines():
        line = line.strip()
        if not line:
            continue

        if PREFERRED_MARKERS.search(line) or re.search(r"\b(preferred|desired) skills?\b", line, re.I):
            current_section = "preferred"
        elif REQUIRED_MARKERS.search(line) or re.search(r"\b(required|essential|must[- ]have) skills?\b", line, re.I):
            current_section = "required"

        skills_on_line = find_skills(line)
        for skill in skills_on_line:
            if PREFERRED_MARKERS.search(line) or current_section == "preferred":
                preferred.add(skill)
            elif REQUIRED_MARKERS.search(line) or current_section == "required":
                required.add(skill)
            else:
                required.add(skill)


    preferred -= required
    return required, preferred


def _find_degree_level(text: str) -> str:
    found = [level for level, pattern in DEGREE_PATTERNS.items() if pattern.search(text)]
    if not found:
        return "unknown"
    return max(found, key=lambda level: DEGREE_RANK[level])


def _find_fields(text: str) -> Set[str]:
    lowered = text.lower()
    found: Set[str] = set()
    for canonical, aliases in FIELD_ALIASES.items():
        if any(_alias_pattern(alias).search(lowered) for alias in aliases):
            found.add(canonical)
    return found


def extract_education(text: str) -> Dict[str, object]:
    """Extract degree level, study fields, and supporting resume lines.

    Field names are taken only from an education section or a line that contains
    an explicit degree term. This reduces false matches when a subject such as
    Statistics appears in a skills list rather than an academic qualification.
    """
    text = remove_personal_information_lines(text)
    evidence: List[str] = []
    education_fields: Set[str] = set()
    degree_levels: List[str] = []
    in_education_section = False

    for line in text.splitlines():
        stripped = line.strip()
        if not stripped:
            continue
        heading = stripped.rstrip(":").strip().lower()
        if re.match(r"^(education|academic background|educational qualifications)$", heading):
            in_education_section = True
            continue
        if re.match(r"^(skills|work experience|experience|employment|projects|certifications|achievements)$", heading):
            in_education_section = False
            continue

        line_degree = _find_degree_level(stripped)
        if line_degree != "unknown":
            degree_levels.append(line_degree)
        if line_degree != "unknown" or in_education_section:
            fields_on_line = _find_fields(stripped)
            if line_degree != "unknown" or fields_on_line:
                evidence.append(stripped)
            education_fields.update(fields_on_line)

    degree_level = max(degree_levels, key=lambda level: DEGREE_RANK[level]) if degree_levels else "unknown"
    return {
        "degree_level": degree_level,
        "fields": sorted(education_fields),
        "evidence": evidence,
    }


def extract_education_requirements(job_description: str) -> Dict[str, object]:
    """Extract any degree level and fields explicitly mentioned in the job text."""
    return {
        "degree_level": _find_degree_level(job_description),
        "fields": sorted(_find_fields(job_description)),
    }


def extract_experience_years(text: str) -> Optional[float]:
    """Extract the largest explicit years/months-of-experience statement.

    It does not calculate durations from employment dates. This avoids guessing
    from incomplete or overlapping date ranges.
    """
    text = remove_personal_information_lines(text)
    values: List[float] = []
    patterns = [
        re.compile(r"\b(\d+(?:\.\d+)?)\s*\+?\s*(?:years?|yrs?)\b", re.IGNORECASE),
        re.compile(r"\b(\d+(?:\.\d+)?)\s*\+?\s*months?\b", re.IGNORECASE),
    ]
    for pattern in patterns:
        for match in pattern.finditer(text):
            start, end = match.span()
            context = text[max(0, start - 55): min(len(text), end + 55)]
            if re.search(r"experience|professional|industry|employment|worked", context, re.I):
                amount = float(match.group(1))
                if "month" in match.group(0).lower():
                    amount /= 12.0
                values.append(amount)
    return max(values) if values else None


def extract_experience_evidence(text: str) -> List[str]:
    """Return lines that appear to contain explicit experience statements."""
    text = remove_personal_information_lines(text)
    evidence = []
    for line in text.splitlines():
        if re.search(r"experience|professional|employment|worked", line, re.I) and extract_experience_years(line) is not None:
            evidence.append(line.strip())
    return evidence



def build_tfidf_vectors(documents: Sequence[str]) -> List[Dict[str, float]]:
    """Build sparse TF-IDF vectors represented as dictionaries.

    Term frequency is count / document token count. IDF is
    log((N + 1) / (document_frequency + 1)) + 1.
    """
    token_lists = [tokenize(document) for document in documents]
    document_frequency: Counter[str] = Counter()
    for tokens in token_lists:
        document_frequency.update(set(tokens))

    number_of_documents = len(documents)
    idf = {
        token: math.log((number_of_documents + 1) / (frequency + 1)) + 1.0
        for token, frequency in document_frequency.items()
    }

    vectors: List[Dict[str, float]] = []
    for tokens in token_lists:
        counts = Counter(tokens)
        total = len(tokens)
        if total == 0:
            vectors.append({})
            continue
        vector = {
            token: (count / total) * idf[token]
            for token, count in counts.items()
        }
        vectors.append(vector)
    return vectors


def cosine_similarity(vector_a: Dict[str, float], vector_b: Dict[str, float]) -> float:
    """Calculate cosine similarity between two sparse numeric dictionaries."""
    if not vector_a or not vector_b:
        return 0.0
    shared_terms = set(vector_a) & set(vector_b)
    dot_product = sum(vector_a[term] * vector_b[term] for term in shared_terms)
    magnitude_a = math.sqrt(sum(value * value for value in vector_a.values()))
    magnitude_b = math.sqrt(sum(value * value for value in vector_b.values()))
    if magnitude_a == 0.0 or magnitude_b == 0.0:
        return 0.0
    return dot_product / (magnitude_a * magnitude_b)


def calculate_text_similarities(job_description: str, resumes: Sequence[str]) -> List[float]:
    """Compare the job text with each resume using this module's TF-IDF code."""
    documents = [job_description, *resumes]
    vectors = build_tfidf_vectors(documents)
    job_vector = vectors[0]
    return [cosine_similarity(job_vector, resume_vector) for resume_vector in vectors[1:]]



BASE_WEIGHTS = {
    "skills": 0.60,
    "text_similarity": 0.20,
    "experience": 0.12,
    "education": 0.08,
}


def calculate_skill_score(
    candidate_skills: Set[str], required_skills: Set[str], preferred_skills: Set[str]
) -> Optional[float]:
    """Calculate a 0-100 skill score; required skills carry 75% of skill weight."""
    if not required_skills and not preferred_skills:
        return None
    required_coverage = (
        len(candidate_skills & required_skills) / len(required_skills)
        if required_skills else None
    )
    preferred_coverage = (
        len(candidate_skills & preferred_skills) / len(preferred_skills)
        if preferred_skills else None
    )
    if required_coverage is not None and preferred_coverage is not None:
        return 100.0 * (0.75 * required_coverage + 0.25 * preferred_coverage)
    if required_coverage is not None:
        return 100.0 * required_coverage
    return 100.0 * float(preferred_coverage or 0.0)


def calculate_experience_score(candidate_years: Optional[float], required_years: Optional[float]) -> Optional[float]:
    """Score explicit experience against the job's stated minimum years."""
    if required_years is None or required_years <= 0:
        return None
    if candidate_years is None:
        return 0.0
    return min(candidate_years / required_years, 1.0) * 100.0


def calculate_education_score(
    candidate_education: Dict[str, object], education_requirement: Dict[str, object]
) -> Optional[float]:
    """Compare the parsed degree level and field against explicit job criteria."""
    required_level = str(education_requirement.get("degree_level", "unknown"))
    required_fields = set(education_requirement.get("fields", []))
    candidate_level = str(candidate_education.get("degree_level", "unknown"))
    candidate_fields = set(candidate_education.get("fields", []))

    has_requirement = required_level != "unknown" or bool(required_fields)
    if not has_requirement:
        return None

    checks: List[float] = []
    if required_level != "unknown":
        checks.append(1.0 if DEGREE_RANK[candidate_level] >= DEGREE_RANK[required_level] else 0.0)
    if required_fields:
        checks.append(1.0 if candidate_fields & required_fields else 0.0)
    return (sum(checks) / len(checks)) * 100.0


def _weighted_total(components: Dict[str, Optional[float]]) -> float:
    available = {
        name: value for name, value in components.items()
        if value is not None and name in BASE_WEIGHTS
    }
    if not available:
        return 0.0
    total_weight = sum(BASE_WEIGHTS[name] for name in available)
    return sum(float(value) * BASE_WEIGHTS[name] for name, value in available.items()) / total_weight


def parse_job_requirements(job_description: str) -> Dict[str, object]:
    """Collect the job-related criteria the program knows how to recognize."""
    required_skills, preferred_skills = extract_skill_requirements(job_description)
    education = extract_education_requirements(job_description)
    return {
        "required_skills": sorted(required_skills),
        "preferred_skills": sorted(preferred_skills),
        "minimum_experience_years": extract_experience_years(job_description),
        "education": education,
    }


def screen_resumes(job_description: str, resumes: Dict[str, str]) -> Dict[str, object]:
    """Analyze and rank resumes. `resumes` maps a candidate label to plain text."""
    if not job_description.strip():
        raise ValueError("The job description cannot be empty.")
    if not resumes:
        raise ValueError("Provide at least one resume.")

    requirements = parse_job_requirements(job_description)
    required_skills = set(requirements["required_skills"])
    preferred_skills = set(requirements["preferred_skills"])
    resume_labels = list(resumes.keys())
    resume_texts = [resumes[label] for label in resume_labels]
    similarities = calculate_text_similarities(job_description, resume_texts)

    results: List[Dict[str, object]] = []
    for label, resume_text, similarity in zip(resume_labels, resume_texts, similarities):
        candidate_skills = find_skills(resume_text)
        education = extract_education(resume_text)
        years = extract_experience_years(resume_text)
        components: Dict[str, Optional[float]] = {
            "skills": calculate_skill_score(candidate_skills, required_skills, preferred_skills),
            "text_similarity": similarity * 100.0,
            "experience": calculate_experience_score(
                years, requirements["minimum_experience_years"]
            ),
            "education": calculate_education_score(education, requirements["education"]),
        }
        results.append({
            "candidate_id": label,
            "overall_score": round(_weighted_total(components), 2),
            "components": {key: None if value is None else round(value, 2) for key, value in components.items()},
            "skills_found": sorted(candidate_skills),
            "required_skills_matched": sorted(candidate_skills & required_skills),
            "required_skills_missing": sorted(required_skills - candidate_skills),
            "preferred_skills_matched": sorted(candidate_skills & preferred_skills),
            "preferred_skills_missing": sorted(preferred_skills - candidate_skills),
            "education": education,
            "experience_years": years,
            "experience_evidence": extract_experience_evidence(resume_text),
            "personal_information_used_for_similarity": False,
        })

    results.sort(key=lambda item: (-float(item["overall_score"]), str(item["candidate_id"])))
    for rank, item in enumerate(results, start=1):
        item["rank"] = rank

    return {"requirements": requirements, "candidates": results}


def print_results(report: Dict[str, object]) -> None:
    """Print a compact ranked summary suitable for a notebook cell."""
    requirements = report["requirements"]
    candidates = report["candidates"]
    print("JOB REQUIREMENTS")
    print("  Required skills:", ", ".join(requirements["required_skills"]) or "Not detected")
    print("  Preferred skills:", ", ".join(requirements["preferred_skills"]) or "Not detected")
    exp = requirements["minimum_experience_years"]
    print("  Minimum experience:", f"{exp:g} years" if exp is not None else "Not detected")
    print("\nCANDIDATE RANKING")
    print("-" * 69)
    print(f"{'Rank':<6}{'Candidate':<24}{'Match score':>14}{'Required skills':>20}")
    print("-" * 69)
    for candidate in candidates:
        matched = len(candidate["required_skills_matched"])
        total = len(requirements["required_skills"])
        print(f"{candidate['rank']:<6}{candidate['candidate_id']:<24}{candidate['overall_score']:>11.2f}%{(str(matched) + '/' + str(total)):>20}")
    print("-" * 69)
    print("Scores are decision-support signals, not hiring recommendations.")


def export_results_csv(report: Dict[str, object], output_path: str | Path) -> Path:
    """Export an explainable summary using Python's built-in csv module."""
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "rank", "candidate_id", "overall_score", "skill_score",
        "text_similarity_score", "experience_score", "education_score",
        "experience_years", "required_skills_matched", "required_skills_missing",
        "preferred_skills_matched", "preferred_skills_missing", "education_level",
        "education_fields",
    ]
    with output_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for candidate in report["candidates"]:
            components = candidate["components"]
            education = candidate["education"]
            writer.writerow({
                "rank": candidate["rank"],
                "candidate_id": candidate["candidate_id"],
                "overall_score": candidate["overall_score"],
                "skill_score": components["skills"],
                "text_similarity_score": components["text_similarity"],
                "experience_score": components["experience"],
                "education_score": components["education"],
                "experience_years": candidate["experience_years"],
                "required_skills_matched": "; ".join(candidate["required_skills_matched"]),
                "required_skills_missing": "; ".join(candidate["required_skills_missing"]),
                "preferred_skills_matched": "; ".join(candidate["preferred_skills_matched"]),
                "preferred_skills_missing": "; ".join(candidate["preferred_skills_missing"]),
                "education_level": education["degree_level"],
                "education_fields": "; ".join(education["fields"]),
            })
    return output_path


def load_resume_folder(folder_path: str | Path) -> Dict[str, str]:
    """Load all .txt resumes in a folder; filenames become neutral candidate IDs."""
    folder = Path(folder_path)
    if not folder.exists():
        raise FileNotFoundError(f"Resume folder not found: {folder}")
    files = sorted(folder.glob("*.txt"))
    if not files:
        raise FileNotFoundError(f"No .txt resume files found in: {folder}")
    return {path.stem: read_text_file(path) for path in files}
