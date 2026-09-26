"""
Tiny in-memory store standing in for a real database.

Domain glossary (for onboarding purposes):
- Task: a unit of work with a title and a completion flag.
- TASKS_MAX_LIMIT: caps how many tasks a single GET /tasks call can return.
"""
import itertools

_id_counter = itertools.count(1)
_tasks = {}


def reset():
    """Clears all tasks. Used by tests."""
    _tasks.clear()


def create_task(title):
    task_id = next(_id_counter)
    task = {"id": task_id, "title": title, "completed": False}
    _tasks[task_id] = task
    return task


def get_task(task_id):
    return _tasks.get(task_id)


def list_tasks(limit=None):
    items = list(_tasks.values())
    if limit is not None:
        items = items[:limit]
    return items


def update_task(task_id, **fields):
    task = _tasks.get(task_id)
    if task is None:
        return None
    task.update(fields)
    return task


def delete_task(task_id):
    return _tasks.pop(task_id, None) is not None
