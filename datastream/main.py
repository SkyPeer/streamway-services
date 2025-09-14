# toStart:
# uvicorn main:app --reload --port 8000

from fastapi import FastAPI, HTTPException
import psycopg2
from meteo.config import database_config
import random
import queue
import asyncio
from concurrent.futures import ThreadPoolExecutor

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

# Create a thread pool executor for background tasks
executor = ThreadPoolExecutor(max_workers=4)
result_queue = queue.Queue()

# -> list[dict[str, Any]]
def get_big_data():
    print('get_big_data START')
    result = []

    # cursor.execute(""" SELECT id, slug, title, description, body, "tagList", "favoritesCount" FROM public.articles; """)
    # cursor.execute(
    #     """ SELECT * FROM public.articles WHERE "authorId" = 2 AND "description" = 'first-article1' AND id > 11182 AND id < 11200; """)
    cursor.execute(""" SELECT * FROM public.articles LIMIT 50000; """)
    data = cursor.fetchall()
    columns = [desc[0] for desc in cursor.description]

    def id_parser(e):
        return e['id']

    for row in data:
        list_row = list(row)
        random_element = random.getrandbits(8000)
        list_row.append(random_element)
        result_row = list(list_row)
        result.append(dict(zip(columns, result_row)))
        result.sort(key=id_parser)

    result_queue.put(result[0:10])
    print('get_big_data END')


# def get_articles_count():
#     cursor.execute(""" SELECT COUNT (*) FROM public.articles """)
#     counter = cursor.fetchone()  # tupple
#     return counter[0]


@app.get("/articles")
async def root():

    loop = asyncio.get_event_loop()
    await loop.run_in_executor(executor, get_big_data)

    # thread = threading.Thread(target=get_big_data)
    # thread.start()
    # thread.join()
    articles = result_queue.get()

    # get_articles()
    # articles = result_data
    response_length = len(articles)

    try:
        return {"len": response_length, "articles": articles}
    except ValueError as e:
        return HTTPException(status_code=400, detail=e)
    except Exception as e:
        # Catch other unexpected exceptions and raise a generic HTTPException
        raise HTTPException(status_code=500, detail="ArticletycsService: unexpected error occurred")


@app.get("/status")
async def test():
        return {
            # "active_tasks": active_tasks,
            "max_workers": executor._max_workers,
            "threads": len(executor._threads),
            "queue_size": executor._work_queue.qsize() if hasattr(executor._work_queue, 'qsize') else 0
        }


