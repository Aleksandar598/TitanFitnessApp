# Titan Fitness App

A Django web application for tracking workouts, nutrition, and fitness progress, with a community feed for sharing posts.

## Features

- **Accounts and goals:** Register, sign in, and manage profile details and fitness goals.
- **Dashboard:** View daily calorie and macronutrient intake, workout calories burned, adjusted nutrition goals, and weight history.
- **Nutrition:** Create and save foods, search USDA FoodData Central, log portions, and review today's intake or food-log history.
- **Workouts:** Create personal exercises and reusable workout plans, track session sets, finish workouts, and review workout history and personal records.
- **Community:** Publish posts, add comments, and like or unlike posts.
- **Administration:** Manage application data through Django's admin interface.

## Technology

- Python and Django (`Django==6.1.1` in `requirements.txt`)
- SQLite for local data storage
- Django templates and static CSS
- USDA FoodData Central integration using Python's standard-library HTTP client

The existing local environment uses Python 3.14.5. No separate frontend build is required.

## Local setup

Run the following from the repository root.

### 1. Create and activate a virtual environment

Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

macOS or Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 2. Install dependencies

```bash
python -m pip install -r TitanFitnessApp/requirements.txt
cd TitanFitnessApp
```

Run all remaining management commands from this inner directory, which contains `manage.py`.

### 3. Configure food search

Create `key.py` beside `manage.py` if it does not already exist, and define your USDA FoodData Central API key:

```python
API_KEY = "your-usda-fooddata-central-api-key"
```

Settings import this value directly from `key.py`; setting an environment variable alone does not configure the integration. Keep your actual key out of version control.

To use the app without USDA search, define `API_KEY = ""`. The module must still exist for Django to start. Manual food creation and logging do not require a USDA key.

### 4. Initialize the database

```bash
python manage.py migrate
```

If your checkout does not include the applications' initial migration files, generate them first, then migrate:

```bash
python manage.py makemigrations users nutrition workout community
python manage.py migrate
```

SQLite stores local data in `TitanFitnessApp/db.sqlite3`, relative to the repository root. No separate database server is needed.

### 5. Start the application

```bash
python manage.py runserver
```

Open [the local application](http://127.0.0.1:8000/) and register an account.

To access the admin interface, optionally create an administrator:

```bash
python manage.py createsuperuser
```

Then sign in at [the local admin page](http://127.0.0.1:8000/admin/).

## Using the app

1. Register and review your profile and fitness goals in **Settings**.
2. Use **Nutrition** to create foods or search USDA, then log the quantities you consume.
3. Use **Workouts** to create exercises and plans or start a workout session. Record sets and finish the session to update your history.
4. Review daily nutrition totals and weight progress on the **Dashboard**.
5. Visit **Community** to share posts and interact with other users.

Main routes:

| Page | Path |
| --- | --- |
| Home | `/` |
| Registration | `/register/` |
| Login | `/login/` |
| Dashboard | `/dashboard/` |
| Profile settings | `/settings/` |
| Nutrition | `/nutrition/` |
| Saved foods | `/saved-foods/` |
| Today's food log | `/food-log/today/` |
| Food-log history | `/food-log/history/` |
| Workouts | `/workouts/` |
| Community | `/community/` |
| Administration | `/admin/` |

## Project structure

```text
TitanFitnessApp/             # Repository root
├── README.md
└── TitanFitnessApp/         # Django working directory
    ├── manage.py
    ├── requirements.txt
    ├── key.py              # Local USDA API key configuration
    ├── TitanFitnessApp/    # Settings, root URLs, ASGI and WSGI
    ├── users/              # Accounts, profiles, goals and weight logs
    ├── nutrition/          # Foods, intake logs and USDA service
    ├── workout/            # Exercises, plans, sessions and records
    ├── dashboard/          # Daily summaries and weight progress
    ├── community/          # Posts, comments and likes
    ├── templates/          # HTML templates grouped by application
    └── static/             # Shared styles
```

## Development checks

With the virtual environment active, run these from the directory containing `manage.py`:

```bash
python manage.py check
python manage.py test
```

To run tests for specific applications:

```bash
python manage.py test users nutrition workout community dashboard
```

USDA service tests mock HTTP responses, so those tests do not need a live API key.

## Configuration

Application settings are in `TitanFitnessApp/TitanFitnessApp/settings.py`. The current configuration uses SQLite, UTC, and Django's custom `users.CustomUser` model.

The included settings are for local development: `DEBUG` is enabled, `ALLOWED_HOSTS` is empty, and the Django secret key is defined in the settings file. Before deploying, configure a private secret key, disable debug mode, set allowed hosts, and configure production static-file serving and an ASGI or WSGI server.
