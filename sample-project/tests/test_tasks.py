import sys
import os
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app import create_app, db  # noqa: E402


class TasksApiTest(unittest.TestCase):
    def setUp(self):
        db.reset()
        self.client = create_app().test_client()

    def test_health(self):
        resp = self.client.get("/health")
        self.assertEqual(resp.status_code, 200)

    def test_create_and_get_task(self):
        resp = self.client.post("/tasks", json={"title": "Write onboarding doc"})
        self.assertEqual(resp.status_code, 201)
        body = resp.get_json()
        self.assertEqual(body["title"], "Write onboarding doc")
        self.assertFalse(body["completed"])

        resp2 = self.client.get(f"/tasks/{body['id']}")
        self.assertEqual(resp2.status_code, 200)
        self.assertEqual(resp2.get_json()["id"], body["id"])

    def test_create_requires_title(self):
        resp = self.client.post("/tasks", json={"title": "  "})
        self.assertEqual(resp.status_code, 400)

    def test_update_task_completed(self):
        created = self.client.post("/tasks", json={"title": "Ship it"}).get_json()
        resp = self.client.put(f"/tasks/{created['id']}", json={"completed": True})
        self.assertEqual(resp.status_code, 200)
        self.assertTrue(resp.get_json()["completed"])

    def test_delete_task(self):
        created = self.client.post("/tasks", json={"title": "Temp"}).get_json()
        resp = self.client.delete(f"/tasks/{created['id']}")
        self.assertEqual(resp.status_code, 204)
        resp2 = self.client.get(f"/tasks/{created['id']}")
        self.assertEqual(resp2.status_code, 404)

    def test_get_missing_task_404(self):
        resp = self.client.get("/tasks/999")
        self.assertEqual(resp.status_code, 404)


if __name__ == "__main__":
    unittest.main()
