# KanMind DRF Backend

> Token‑based Django REST Framework API for a kanban‑inspired board and task management system with user authentication, role‑ and object‑level permissions, as well as nested resources (tasks + comments).

## Table of Contents
- [Project Overview](#project-overview)
- [Features](#features)
- [Getting Started](#getting-started)
- [Authentication](#authentication)
- [Usage Examples](#usage-examples)
- [API Reference](#api-reference)
- [Testing](#testing)
- [Support](#support)
- [Contributing](#contributing)
- [License](#license)

## Project Overview
The KanMind DRF Backend provides the server-side API for managing:
- User registration & login (token auth)
- Collaborative boards with member management
- Tasks with status, priority, assignee, reviewer, due date
- Filtered task views (assigned-to-me, reviewing)
- Nested task comments

Built with Django 5.x, Django REST Framework and token-based authentication.

## Features
- Secure token-based user authentication (registration & login)
- Board CRUD with member assignment and ownership checks
- Task management (status workflow: `to-do → in-progress → review → done`)
- Priority levels (`low | medium | high`)
- Assignee & reviewer relationships restricted to board members
- Nested comments under tasks
- Filtered listing endpoints for personal workload & review queue
- Granular permission classes (board owner/member, task assignee, comment author)
- CORS support for local frontend development

## Getting Started
### Prerequisites
- Python >= 3.10 (recommended 3.11/3.12)
- `pip` & virtual environment tool (`venv` or `pyenv`)

### Installation
```bash
# Clone repository
git clone https://github.com/AbbasEl11/KanMind-DRF-Backend.git
cd KanMind-DRF-Backend/projekt_kanmind

# Create & activate virtual environment
python -m venv .venv
# Windows (cmd)
.venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Apply migrations
python manage.py migrate

# (Optional) Create superuser for admin access
python manage.py createsuperuser

# Start development server
python manage.py runserver
```
Server runs at: `http://127.0.0.1:8000/`

## Authentication
The API uses DRF Token Authentication.
- Obtain token via `/api/registration/` or `/api/login/`
- Include header in subsequent requests:
```
Authorization: Token <your_token_here>
```
Default permission class (`settings.py`): `IsAuthenticated` — most endpoints require a valid token.

## Usage Examples
Below examples use `curl`. Replace `<TOKEN>` with a valid token and IDs accordingly.

### Register
```bash
curl -X POST http://127.0.0.1:8000/api/registration/ \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "Secret123!",
    "repeated_password": "Secret123!",
    "fullname": "Jane Doe"
  }'
```
Response:
```json
{
  "token": "<token>",
  "fullname": "Jane Doe",
  "email": "user@example.com",
  "user_id": 5
}
```

### Login
```bash
curl -X POST http://127.0.0.1:8000/api/login/ \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "Secret123!"}'
```

### Create Board
```bash
curl -X POST http://127.0.0.1:8000/api/boards/ \
  -H "Authorization: Token <TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{"title": "Marketing", "members": [3,4]}'
```

### List Boards
```bash
curl -H "Authorization: Token <TOKEN>" http://127.0.0.1:8000/api/boards/
```

### Email Lookup
```bash
curl -H "Authorization: Token <TOKEN>" \
  "http://127.0.0.1:8000/api/email-check/?email=member@example.com"
```

### Create Task
```bash
curl -X POST http://127.0.0.1:8000/api/tasks/ \
  -H "Authorization: Token <TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{
    "board": 2,
    "title": "Design Landing Page",
    "description": "First draft of layout",
    "priority": "high",
    "assignee_id": 3,
    "reviewer_id": 4,
    "due_date": "2025-12-15"
  }'
```

### Tasks Assigned to Me
```bash
curl -H "Authorization: Token <TOKEN>" http://127.0.0.1:8000/api/tasks/assigned-to-me/
```

### Add Comment to Task
```bash
curl -X POST http://127.0.0.1:8000/api/tasks/7/comments/ \
  -H "Authorization: Token <TOKEN>" \
  -H "Content-Type: application/json" \
  -d '{"content": "Looks good, please adjust spacing."}'
```

## API Reference
Only endpoints defined in source code listed below.

### Authentication
| Method | Endpoint | Description | Serializer (Request) |
|--------|----------|-------------|-----------------------|
| POST | `/api/registration/` | Register new user & return token | RegistrationSerializer (`email`, `password`, `repeated_password`, `fullname`) |
| POST | `/api/login/` | Login by email & password, returns token | LoginSerializer (`email`, `password`) |

### Boards
| Method | Endpoint | Description | Notes |
|--------|----------|-------------|-------|
| GET | `/api/boards/` | List boards where user is owner or member | `BoardListSerializer` |
| POST | `/api/boards/` | Create board | Body: `title`, `members` (list of user IDs) |
| GET | `/api/boards/{id}/` | Retrieve board details | `BoardDetailSerializer` (includes tasks) |
| PUT/PATCH | `/api/boards/{id}/` | Update title and/or members | `BoardUpdateSerializer` |
| DELETE | `/api/boards/{id}/` | Delete board | Owner only |
| GET | `/api/email-check/?email=<email>` | Lookup user by email | Returns `id`, `email`, `fullname` |

### Tasks
| Method | Endpoint | Description | Notes |
|--------|----------|-------------|-------|
| POST | `/api/tasks/` | Create task | Board owner only |
| PUT/PATCH | `/api/tasks/{id}/` | Update task | Board members; cannot change board |
| DELETE | `/api/tasks/{id}/` | Delete task | Board owner or assignee |
| GET | `/api/tasks/assigned-to-me/` | Tasks where user is assignee | Filter view |
| GET | `/api/tasks/reviewing/` | Tasks where user is reviewer | Filter view |

Task fields (request): `board`, `title`, `description?`, `status?`, `priority?`, `assignee_id?`, `reviewer_id?`, `due_date?`

### Task Comments (Nested)
| Method | Endpoint | Description | Notes |
|--------|----------|-------------|-------|
| GET | `/api/tasks/{task_id}/comments/` | List comments | Board member/owner |
| POST | `/api/tasks/{task_id}/comments/` | Add comment | Field: `content` |
| DELETE | `/api/tasks/{task_id}/comments/{id}/` | Delete comment | Author only |


## Support
Open issues or questions via GitHub Issues: `https://github.com/AbbasEl11/KanMind-DRF-Backend/issues`

