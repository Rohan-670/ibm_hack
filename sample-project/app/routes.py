from flask import Blueprint, jsonify, request

from . import db

bp = Blueprint("tasks", __name__)


@bp.get("/health")
def health():
    return jsonify({"status": "ok"})


@bp.get("/tasks")
def list_tasks():
    """Returns all tasks. See README for the response contract."""
    tasks = db.list_tasks()
    return jsonify([_serialize(t) for t in tasks])


@bp.post("/tasks")
def create_task():
    payload = request.get_json(force=True)
    title = payload.get("title", "").strip()
    if not title:
        return jsonify({"error": "title is required"}), 400
    task = db.create_task(title)
    return jsonify(_serialize(task)), 201


@bp.get("/tasks/<int:task_id>")
def get_task(task_id):
    task = db.get_task(task_id)
    if task is None:
        return jsonify({"error": "not found"}), 404
    return jsonify(_serialize(task))


@bp.put("/tasks/<int:task_id>")
def update_task(task_id):
    payload = request.get_json(force=True)
    fields = {}
    if "title" in payload:
        fields["title"] = payload["title"]
    if "completed" in payload:
        fields["completed"] = bool(payload["completed"])
    task = db.update_task(task_id, **fields)
    if task is None:
        return jsonify({"error": "not found"}), 404
    return jsonify(_serialize(task))


@bp.delete("/tasks/<int:task_id>")
def delete_task(task_id):
    ok = db.delete_task(task_id)
    if not ok:
        return jsonify({"error": "not found"}), 404
    return "", 204


def _serialize(task):
    """The public response contract for a task. Documented in README.md."""
    return {"id": task["id"], "title": task["title"], "completed": task["completed"]}
