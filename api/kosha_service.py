import os
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from accident_knowledge.openapi_client import fetch_public_api

app = FastAPI(title="KOSHA Accident Data API", version="1.0.0")
allowed = [x.strip() for x in os.getenv("CORS_ORIGINS", "https://ahky900-art.github.io").split(",") if x.strip()]
app.add_middleware(CORSMiddleware, allow_origins=allowed, allow_methods=["GET"], allow_headers=["*"])

@app.get("/health")
def health():
    return {"status": "ok", "service": "kosha-accident-api"}

@app.get("/api/kosha/accidents")
def accidents(page: int = Query(1, ge=1), per_page: int = Query(100, ge=1, le=500)):
    try:
        import pandas as pd
        frame, meta = fetch_public_api(params={"page": page, "perPage": per_page}, max_pages=1)
        frame = frame.fillna("").astype(str)
        records = frame.to_dict(orient="records")
        return {"records": records, "count": len(records), "page": page, "per_page": per_page,
                "source": "KOSHA ODCloud API", "metadata": {k:v for k,v in meta.items() if k != "endpoint"}}
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"KOSHA 원천 API 조회 실패: {str(exc)[:1200]}")
