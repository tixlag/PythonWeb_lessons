from fastapi import FastAPI

app = FastAPI(title="CRM API")

@app.get("/")
async def root():
    return {"message": "CRM API"}

@app.get("/health")
async def health():
    return {"status": "ok"}
