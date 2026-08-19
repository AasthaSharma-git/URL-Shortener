
# URL Shortener API

A basic URL Shortener API built using Python, FastAPI, and PostgreSQL.

## Overview

This project provides a simple API for shortening long URLs.

The API accepts a long URL, generates a unique six-character short code, and stores the URL mapping in PostgreSQL. When the shortened URL is accessed, the API retrieves the original URL from the database and redirects the user to it.

If the same URL is submitted again, the existing short code is returned instead of creating a duplicate entry.

The application also validates URLs and returns a `404 Not Found` response when a short code does not exist.

## Technologies

- Python
- FastAPI
- PostgreSQL
- Psycopg
- Pydantic
- python-dotenv

## Project Structure

```text
url-shortner/
├── main.py
├── database.py
├── requirements.txt
├── .env.example
└── README.md
````

## Database Setup

Make sure PostgreSQL is installed and running.

Create a PostgreSQL database named:

```text
url_shortener
```

Create the required table inside the database:

```sql
CREATE TABLE urls (
    id SERIAL PRIMARY KEY,
    original_url TEXT NOT NULL,
    short_code VARCHAR(10) UNIQUE NOT NULL
);
```

The table stores the original URL and its corresponding short code.

## Environment Configuration

Create a file named `.env` in the project root directory.

Add:

```text
DATABASE_URL=postgresql://postgres:YOUR_PASSWORD@localhost:5432/url_shortener
```

Replace `YOUR_PASSWORD` with the password configured for your PostgreSQL installation.

The `.env` file contains database credentials and should not be shared or uploaded.

## Installation

Open a terminal in the project directory.

Create a virtual environment:

```bash
python -m venv venv
```

Activate it on Windows:

```bash
venv\Scripts\activate
```

Install the required dependencies:

```bash
pip install -r requirements.txt
```

## Running the Application

Make sure PostgreSQL is running and the `.env` file is configured correctly.

Start the FastAPI application:

```bash
fastapi dev main.py
```

The application will run at:

```text
http://127.0.0.1:8000
```

Interactive API documentation is available at:

```text
http://127.0.0.1:8000/docs
```

The `/docs` page can be used to test the API directly from the browser.

## API Usage

### Create a Short URL

Send a `POST` request to:

```text
/shorten
```

Request body:

```json
{
    "long_url": "https://www.google.com"
}
```

Example response:

```json
{
    "original_url": "https://www.google.com",
    "short_code": "aB7xQ2",
    "shortened_url": "http://127.0.0.1:8000/aB7xQ2"
}
```

The generated short code is stored in PostgreSQL along with the original URL.

If the same original URL is submitted again, the API returns the existing short code.

### Redirect to the Original URL

Send a `GET` request using the generated short code:

```text
/aB7xQ2
```

For example:

```text
http://127.0.0.1:8000/aB7xQ2
```

If the short code exists, the API redirects the user to the original URL.

If the short code does not exist, the API returns:

```json
{
    "detail": "Short URL not found"
}
```

with HTTP status code `404`.

## Validation

The API uses Pydantic's `HttpUrl` type to validate the submitted URL.

Invalid URL values are rejected before they are stored in PostgreSQL.

## Short Code Generation

A six-character short code is generated using uppercase letters, lowercase letters, and digits.

Before storing a generated code, the application checks PostgreSQL to ensure that the code is not already being used.

## Running the Project from Scratch

The complete process is:

1. Install Python and PostgreSQL.
2. Start PostgreSQL.
3. Create the `url_shortener` database.
4. Create the `urls` table using the SQL provided above.
5. Create the `.env` file with the PostgreSQL connection string.
6. Create and activate the Python virtual environment.
7. Install dependencies using `pip install -r requirements.txt`.
8. Start the application using `fastapi dev main.py`.
9. Open `http://127.0.0.1:8000/docs`.
10. Use the Swagger UI to test the `/shorten` and `/{short_code}` endpoints.

## Security Note

The `.env` file contains database credentials and should not be included when sharing the project.

The provided `.env.example` file can be used as a template for creating the `.env` file.



