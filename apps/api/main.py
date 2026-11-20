"""FastAPI sürümü (gerçek sunucu için). Çalıştır: uvicorn main:app --host 0.0.0.0 --port 8000"""
from fastapi import FastAPI, HTTPException
from service import get_areas, get_events, get_summary

app = FastAPI(title="Hırt İPTAL API")

@app.get("/health")
def health():
    return {"ok": True}

@app.get("/areas")
def areas(parent: int | None = None):
    return get_areas(parent)

@app.get("/events")
def events():
    return get_events()

@app.get("/areas/{area_id}/summary")
def summary(area_id: int):
    data = get_summary(area_id)
    if data is None:
        raise HTTPException(404, "Bölge bulunamadı")
    return data
