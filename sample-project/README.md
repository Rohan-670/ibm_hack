# Tasks API

A tiny Flask API used as the demo project for RepoPilot. Deliberately small so
that every diff/agent output in the demo is easy to verify by eye.

## Setup

```
pip install -r requirements.txt
cp .env.example .env
python run.py
```

## Endpoints

| Method | Path | Description |
|---|---|---|
| GET | /health | Liveness check |
| GET | /tasks | List all tasks |
| POST | /tasks | Create a task. Body: `{"title": "..."}` |
| GET | /tasks/:id | Get one task |
| PUT | /tasks/:id | Update `title` and/or `completed` |
| DELETE | /tasks/:id | Delete a task |

## Response contract

A task is always serialized as:

```json
{"id": 1, "title": "Write onboarding doc", "completed": false}
```

## Testing

```
python -m unittest discover tests
```

## Environment variables

None currently required. See `.env.example`.
