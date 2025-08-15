# Gemini Project Analysis: cacrespo.xyz

## Project Overview

This project is a personal website and blog, built using the Django web framework. It is containerized with Docker for consistent development and deployment environments. The project includes separate applications for the blog and static pages, a complete set of tests, and uses `ruff` for code linting and formatting.

## Technologies

- **Backend:** Django, Python
- **Database:** PostgreSQL
- **Frontend:** Django Templates, HTML, CSS
- **Containerization:** Docker, Docker Compose
- **Dependency Management:** uv, `pyproject.toml`
- **Testing:** pytest, pytest-django
- **Linting & Formatting:** ruff
- **CI/CD:** GitHub Actions
- **Deployment:** Gunicorn

## Project Structure

- **`blog/`**: A Django app for the blog functionality.
- **`pages/`**: A Django app for the static pages of the website (e.g., about, contact).
- **`mysite/`**: The main Django project directory, containing the settings and main URL configuration.
- **`static/`**: Static files such as CSS and images.
- **`templates/`**: Base HTML templates that are extended by the app-specific templates.
- **`tests/`**: Contains the tests for the different Django apps.
- **`Dockerfile`**: Defines the Docker image for the application, with stages for development and production.
- **`docker-compose.yml`**: Defines the services, networks, and volumes for the Docker application.
- **`Makefile`**: Provides a set of commands to simplify common tasks like running the server, testing, and managing the Docker containers.
- **`pyproject.toml`**: The file that contains the project metadata and dependencies for `uv`.

## How to Run the Project

The project is designed to be run with Docker. The `Makefile` provides convenient commands to manage the application stack.

1.  **Build and start the development server:**
    ```bash
    make start
    ```
2.  The website will be available at [http://localhost:8000](http://localhost:8000).

## How to Run Tests

The project uses `pytest` for testing. You can run the test suite with the following command:

```bash
make test
```

## How to Install Dependencies

Dependencies are managed with `uv` and are defined in `pyproject.toml`.

- To install production dependencies:
  ```bash
  uv sync
  ```
- To install all dependencies, including development dependencies:
  ```bash
  uv sync --all-groups
  ```

## Linting and Formatting

The project uses `ruff` for code linting and formatting.

- To run the linter:
  ```bash
  make pep8
  ```
- The project is also configured to use `pre-commit` to run `ruff` automatically before each commit.

## Deployment

The `Dockerfile` includes a `production` stage that uses `gunicorn` to serve the Django application. The `.github/workflows/django.yml` file defines a GitHub Actions workflow for continuous integration and deployment.
