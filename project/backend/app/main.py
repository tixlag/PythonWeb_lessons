from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes import auth, deals

app = FastAPI(title="CRM API")

app.include_router(auth.router)
app.include_router(deals.router)

FRONTEND_URLS = ['0.0.0.0:8000', '0.0.0.0:8004', '127.0.0.1:8000', 'localhost:8000']
app.add_middleware(CORSMiddleware,
                   allow_origins=FRONTEND_URLS,  # Только ваши домены
                   allow_credentials=True,
                   allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS"],
                   allow_headers=["*"],  # Или конкретно: ["Authorization", "Content-Type"]
                   )

@app.get("/")
async def root():
    return {"message": "CRM API"}

@app.get("/health")
async def health():
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8004)