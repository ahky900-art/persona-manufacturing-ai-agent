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



@app.get("/api/huggingface/personas")
def huggingface_personas(
    offset: int = Query(0, ge=0, le=1000000),
    length: int = Query(10, ge=1, le=100)
):
    """Server-side proxy for the public Nemotron-Personas-Korea dataset.
    Keeps Hugging Face requests off the browser to avoid client-side CORS/network failures.
    """
    import requests
    endpoint = "https://datasets-server.huggingface.co/rows"
    params = {
        "dataset": "nvidia/Nemotron-Personas-Korea",
        "config": "default",
        "split": "train",
        "offset": offset,
        "length": length,
    }
    try:
        response = requests.get(
            endpoint,
            params=params,
            headers={"Accept": "application/json", "User-Agent": "persona-manufacturing-ai-agent/1.0"},
            timeout=(8, 35),
        )
        if not response.ok:
            raise HTTPException(
                status_code=502,
                detail=f"Hugging Face upstream HTTP {response.status_code}: {response.text[:600]}",
            )
        payload = response.json()
        rows = payload.get("rows")
        if not isinstance(rows, list):
            raise ValueError("Hugging Face 응답에 rows 배열이 없습니다.")
        records = [item.get("row", item) for item in rows]
        return {
            "dataset": params["dataset"],
            "config": params["config"],
            "split": params["split"],
            "offset": offset,
            "length": len(records),
            "total": payload.get("num_rows_total"),
            "records": records,
            "source": "Hugging Face Datasets Server",
        }
    except HTTPException:
        raise
    except requests.RequestException as exc:
        raise HTTPException(status_code=502, detail=f"Hugging Face 연결 실패: {str(exc)[:600]}")
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Hugging Face 응답 처리 실패: {str(exc)[:600]}")
