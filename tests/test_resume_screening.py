import tempfile
import unittest
from pathlib import Path

import sys
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

import resume_screening as rs


class ResumeScreeningTests(unittest.TestCase):
    def test_tokenizer_removes_stop_words(self):
        self.assertEqual(rs.tokenize("Python is useful for data analysis"), ["python", "useful", "data", "analysis"])

    def test_personal_details_removed_from_text_similarity(self):
        cleaned = rs.remove_personal_information_lines(
            "Name: Example Person\nGender: Female\nPython and SQL\nemail: test@example.com"
        )
        self.assertNotIn("Example Person", cleaned)
        self.assertNotIn("Female", cleaned)
        self.assertIn("Python and SQL", cleaned)

    def test_skill_extraction(self):
        found = rs.find_skills("I use Python, SQL, Power BI and data visualisation.")
        self.assertEqual(found, {"Python", "SQL", "Power BI", "Data visualization"})

    def test_required_and_preferred_skill_extraction(self):
        required, preferred = rs.extract_skill_requirements(
            "Required Skills:\nPython, SQL\nPreferred Skills:\nPower BI, Tableau"
        )
        self.assertEqual(required, {"Python", "SQL"})
        self.assertEqual(preferred, {"Power BI", "Tableau"})

    def test_experience_extraction_years_and_months(self):
        self.assertEqual(rs.extract_experience_years("Experience: 2 years as analyst"), 2.0)
        self.assertAlmostEqual(rs.extract_experience_years("Professional experience: 18 months"), 1.5)
        self.assertIsNone(rs.extract_experience_years("Studied for 4 years"))

    def test_education_extraction(self):
        education = rs.extract_education("Bachelor of Science in Statistics")
        self.assertEqual(education["degree_level"], "bachelor")
        self.assertIn("Statistics", education["fields"])

    def test_skills_are_not_misread_as_education_fields(self):
        education = rs.extract_education(
            "SKILLS\nPython, SQL, Statistics\nEDUCATION\nBachelor of Technology in Computer Science"
        )
        self.assertEqual(education["fields"], ["Computer science"])

    def test_cosine_similarity(self):
        self.assertAlmostEqual(rs.cosine_similarity({"python": 1.0}, {"python": 2.0}), 1.0)
        self.assertEqual(rs.cosine_similarity({}, {"python": 1.0}), 0.0)

    def test_skill_score(self):
        score = rs.calculate_skill_score({"Python", "SQL"}, {"Python", "SQL"}, {"Power BI"})
        self.assertAlmostEqual(score, 75.0)

    def test_ranking_and_explanations(self):
        jd = rs.read_text_file(PROJECT_ROOT / "data" / "job_description.txt")
        resumes = rs.load_resume_folder(PROJECT_ROOT / "data" / "resumes")
        report = rs.screen_resumes(jd, resumes)
        candidates = report["candidates"]
        self.assertEqual(len(candidates), 4)
        self.assertEqual(candidates[0]["candidate_id"], "candidate_001")
        self.assertTrue(candidates[0]["required_skills_matched"])
        self.assertTrue(candidates[0]["required_skills_missing"] == [])
        self.assertEqual([item["rank"] for item in candidates], [1, 2, 3, 4])

    def test_csv_export(self):
        jd = rs.read_text_file(PROJECT_ROOT / "data" / "job_description.txt")
        resumes = rs.load_resume_folder(PROJECT_ROOT / "data" / "resumes")
        report = rs.screen_resumes(jd, resumes)
        with tempfile.TemporaryDirectory() as temp_dir:
            output = rs.export_results_csv(report, Path(temp_dir) / "results.csv")
            self.assertTrue(output.exists())
            self.assertIn("overall_score", output.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main(verbosity=2)
