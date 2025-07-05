# toStart:
# uvicorn main:app --reload --port 8000

from typing import Any
from fastapi import FastAPI, Request, HTTPException
import psycopg2
from config import database_config

connection = psycopg2.connect(
    database=database_config["database"],
    user=database_config["user"],
    password=database_config["password"],
    host=database_config["host"],
    port=database_config["port"],
)

connection.autocommit = True
cursor = connection.cursor()

print('__name__', __name__)
app = FastAPI()


def get_articles() -> list[dict[str, Any]]:
    # cursor.execute(""" SELECT id, slug, title, description, body, "tagList", "favoritesCount" FROM public.articles; """)
    cursor.execute(
        """ SELECT * FROM public.articles WHERE "authorId" = 2 AN "description" = 'first-article1' AND id > 11182 AND id < 11200; """)
    data = cursor.fetchall()

    columns = [desc[0] for desc in cursor.description]

    result = []
    for row in data:
        result.append(dict(zip(columns, row)))

    return result

def get_articles_count():
    cursor.execute(""" SELECT COUNT (*) FROM public.articles """)
    counter = cursor.fetchone()  # tupple
    return counter[0]


@app.get("/articles")
async def root():
    try:
        return {"articles": get_articles(), "count": get_articles_count()}
    except ValueError as e:
        return HTTPException(status_code=400, detail=e)
    except Exception as e:
        # Catch other unexpected exceptions and raise a generic HTTPException
        raise HTTPException(status_code=500, detail="ArticletycsService: unexpected error occurred")


