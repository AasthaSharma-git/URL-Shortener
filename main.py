from fastapi import FastAPI, HTTPException
from fastapi.responses import RedirectResponse
from pydantic import BaseModel, HttpUrl
import secrets
import string

from database import get_connection

#Create FastAPI application
app = FastAPI()

#Request schema for the /shorten endpoint
#HttpUrl automatically validates that the provided value is a valid URL
class URLRequest(BaseModel):
    long_url:HttpUrl

@app.get("/")
def home():
    """
    Health-check endpoint.

    Used to verify that the API is running.
    """
    return {"messsage": "URL Shortener API is running!"}

@app.post("/shorten")
def shorten_url(req: URLRequest):
    """
    Create a shortened URL.

    If the original URL already exists in the database,
    return its existing short code.

    Otherwise:
    1. Generate a unique short code.
    2. Store the URL and short code in PostgreSQL.
    3. Return the shortened URL.
    """
    #Open a connection to PostgreSQL
    connection = get_connection()

    #Convert Pydantic's HttpUrl object into a normal string before storing it in PostgreSQL
    long_url = str(req.long_url)

    try:
        with connection.cursor() as cursor:

            #Check whether this URL has already been shortened
            cursor.execute(
                """
                SELECT short_code
                FROM urls
                WHERE original_url = %s
                """,
                (long_url,)
            )

            existing_url = cursor.fetchone()

            #If the URL already exists, reuse its short code.
            #This prevents unnecessary duplicate records.
            if existing_url:
                short_code = existing_url[0]

            else:
                #Characters that can be used to generate the short code
                chars = string.ascii_letters + string.digits

                #Keep generating codes until we find one that does not already exists in the database.
                while True:

                    short_code = "".join(
                        secrets.choice(chars)
                        for _ in range(6)
                    )

                    #Check whether the generated code us already being used by another URL.
                    cursor.execute(
                        """
                        SELECT short_code
                        FROM urls
                        WHERE short_code = %s
                        """,
                        (short_code,)
                    )

                    code_exists = cursor.fetchone()

                    #If no matching code was found, it is safe to use
                    if code_exists is None:
                        break

                #Store the new URL and its short code in PostgreSQL
                cursor.execute(
                    """
                    INSERT into urls (original_url, short_code)
                    VALUES (%s, %s)
                    """,
                    (long_url, short_code)
                )

                #Commit the transaction so the new record is permanently saved in the database.
                connection.commit()

    finally:
        #Always close the database connection even if an error occurs.
        connection.close()

    #Return the details of the shortened URL
    return{
        "original_url": long_url,
        "short_code": short_code,
        "shortened_url": f"http://127.0.0.1:8000/{short_code}"
    }

@app.get("/{short_code}")
def redirect_to_original(short_code: str):
    """
    Redirect a short code to its original URL.

    Example:
        GET /aB7xQ2

    The API looks up 'aB7xQ2' in PostgreSQL and
    redirects the user to the stored original URL.
    """

    #Open a connection to PostgreSQL
    connection =  get_connection()

    try:
        with connection.cursor() as cursor:

            #Find the original URL associated with the short code.
            cursor.execute(
                """
                SELECT original_url
                FROM urls
                WHERE short_code = %s
                """,
                (short_code,)
            )
            result = cursor.fetchone()
    finally:
        #Close the database connection after the query is complete
        connection.close()

    #If the short code doesn't exist, return a 404 response
    if result is None:
        raise HTTPException(
            status_code=404,
            detail="Short URL not found"
        )

    #The first value in the database result is the original URL
    original_url = result[0]

    #Redirect the user to the original URL
    return RedirectResponse(url=original_url)