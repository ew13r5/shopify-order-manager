from fastapi import FastAPI

app = FastAPI(
    title="Shopify Order Manager",
    version="1.0.0",
    description="Backend API for Shopify Order Manager dashboard",
)


@app.get("/api/health")
def health_check():
    return {"status": "ok"}
