# apps/api
Arka uç (ilk taslak, örnek veriyle). Mantık `service.py` içinde, iki sunucu sürümü var.

## Termux / hızlı deneme (kurulum yok)
```
python dev_server.py
```
Dene: `curl localhost:8000/areas/1/summary`

## Gerçek sunucu (FastAPI)
```
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8000
```
Not: Termux'ta `pydantic-core` derlenemediği için FastAPI orada kurulmaz.

Uç noktalar: `/health`, `/events`, `/areas/{id}/summary`
