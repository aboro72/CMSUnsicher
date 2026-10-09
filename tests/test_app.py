import tempfile
import unittest
from pathlib import Path

import app as cms


class CMSTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.old_database = cms.DATABASE
        cms.DATABASE = Path(self.temp.name) / "test.sqlite3"
        cms.app.config["TESTING"] = True
        cms.init_db()
        self.client = cms.app.test_client()

    def tearDown(self):
        cms.DATABASE = self.old_database
        self.temp.cleanup()

    def test_normal_workflow(self):
        self.assertEqual(self.client.get("/health").json, {"status": "ok"})
        self.assertEqual(self.client.get("/").status_code, 200)
        self.assertEqual(self.client.get("/admin").status_code, 302)
        self.assertIn("fehlgeschlagen", self.client.post("/login", data={"username": "demo", "password": "wrong"}).text)
        self.client.post("/login", data={"username": "demo", "password": "demo123"})
        self.client.post("/posts/new", data={"title": "Testbeitrag", "body": "Inhalt"})
        self.assertIn("Testbeitrag", self.client.get("/").text)
        self.assertIn("Testbeitrag", self.client.get("/?q=Testbeitrag").text)
        self.client.get("/logout")
        self.assertEqual(self.client.get("/profile/1").status_code, 302)

    def test_training_vulnerabilities(self):
        self.client.post("/login", data={"username": "' OR 1=1 -- ", "password": "wrong"})
        self.assertEqual(self.client.get("/admin").status_code, 200)
        self.client.get("/logout")
        self.client.post("/login", data={"username": "demo", "password": "demo123"})
        self.assertIn("FLAG{profile_idor}", self.client.get("/profile/1").text)
        self.assertIn("FLAG{missing_role_check}", self.client.get("/admin").text)
        self.client.post("/posts/new", data={"title": "XSS", "body": "<script>alert('training')</script>"})
        self.assertIn("<script>alert('training')</script>", self.client.get("/").text)
        self.client.get("/admin/delete/2")
        self.assertNotIn("<script>alert('training')</script>", self.client.get("/").text)
        self.assertEqual(self.client.get("/?q=' OR 1=1 -- ").status_code, 200)


if __name__ == "__main__":
    unittest.main()
