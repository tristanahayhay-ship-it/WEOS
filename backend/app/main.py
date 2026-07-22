from fastapi import FastAPI

app = FastAPI(
    title="WEOS",
    version="1.0.0"
)


@app.get("/")
def root():
    return {
        "project": "WEOS",
        "status": "running"
    }
