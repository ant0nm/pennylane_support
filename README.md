# PennyLane Support API

## About

This API was built to power PennyLane Support - a community-driven support conversations platform for PennyLane quantum computing challenges.

## Prerequisites

* Python 3.14+
* PostgreSQL 17
* Docker

## Quick Overview

FastAPI + SQLModel + PostgreSQL + Docker

ALL users can...

* Browse coding challenges
  * `GET /challenges/`
  * `GET /challenges/{challenge_id}`
* Browse specific conversations
  * `GET /conversations/{conversation_id}`
  * `GET /conversations/{conversation_id}/posts/`

* Create support conversations
  * `POST /conversations/`
* Add posts/replies to support conversations
  * `POST /conversations/{conversation_id}/posts/`

ONLY ADMINS can...

* View all support conversations
  * `GET /conversations/`
* Manage support conversations (update, delete, etc.)
  * `PATCH /conversations/{conversation_id}/`
  * `DELETE /conversations/{conversation_id}/`

Note that the service currently doesn't have a robust auth layer. We simply check for the presence of a `username` query param and use that to determine the user's privileges.

Lastly, due to time constraints, automated tests were not implemented. That said, all of the endpoints have been tested manually. You can try issuing some of these requests once you have the app running locally:

```bash
curl -X GET "http://127.0.0.1:8000/challenges/?username=quantum_learner42" -H "Content-Type: application/json" | jq
curl -X GET "http://127.0.0.1:8000/challenges/CHAL_001?username=quantum_learner42" -H "Content-Type: application/json" | jq
curl -X GET "http://localhost:8000/conversations/?username=pennylane_support" -H "Content-Type: application/json" | jq
```

## Running the app

1. Install poetry

```bash
pipx install poetry
```

2. Install poe

```bash
pipx install poethepoet
```

3. Install Docker

```bash
brew install --cask docker
```

4. Install PostgreSQL 17

```bash
brew install postgresql@17
# Make sure to add this to your PATH.
# export PATH="/opt/homebrew/opt/postgresql@17/bin:$PATH"
```

5. Add an `.env` file with all of the required env vars (see `.env.example` for reference).

6. Install the dependencies

```bash
cd pennylane_support
poetry install
```

7. Spin up the DB

```
poe pg_dev_start
```

8. Seed the DB

```
poe seed_db
```

9. Start the development server

```
poe server_dev_start
```

You are good to go! Try sending a few requests:
```bash
curl -X GET "http://127.0.0.1:8000/challenges/?username=quantum_learner42" -H "Content-Type: application/json" | jq
curl -X GET "http://127.0.0.1:8000/challenges/CHAL_001?username=quantum_learner42" -H "Content-Type: application/json" | jq
```

The API docs will be available at http://127.0.0.1:8000/docs.