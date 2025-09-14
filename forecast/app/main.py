# uvicorn main: app - -reload - -port 8500
from fastapi import FastAPI
from api.v1.endpoints import health
app = FastAPI(title="Forecast Service")

# Routers
app.include_router(health.router, prefix="/api/v1")
# app = FastAPI()

# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run("app.main:app", host="localhost", port=8400, reload=True)
