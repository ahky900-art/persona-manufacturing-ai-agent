"""ODCloud client for KOSHA manufacturing accident case API."""
from __future__ import annotations
import json
import os
import xml.etree.ElementTree as ET
from typing import Any
import pandas as pd
import requests

DEFAULT_ENDPOINT = "https://api.odcloud.kr/api/15163146/v1/uddi:3c9aaf7a-965f-4531-9f31-d1049e13e115"

def _flatten_xml(element: ET.Element) -> list[dict[str, Any]]:
    records=[]
    for node in element.iter():
        if node.tag.split("}")[-1].lower() in {"item","row","record"}:
            records.append({child.tag.split("}")[-1]: (child.text or "").strip() for child in list(node)})
    if records:
        return records
    return [{child.tag.split("}")[-1]: (child.text or "").strip() for child in list(element)}]

def _extract_records(payload: Any) -> list[dict[str, Any]]:
    if isinstance(payload,list):
        return [x for x in payload if isinstance(x,dict)]
    if not isinstance(payload,dict):
        return []
    for key in ("data","items","item","list","results","records","response"):
        if key in payload:
            found=_extract_records(payload[key])
            if found:
                return found
    if all(not isinstance(v,(dict,list)) for v in payload.values()):
        return [payload]
    for value in payload.values():
        found=_extract_records(value)
        if found:
            return found
    return []

def fetch_public_api(endpoint: str | None = None, service_key: str | None = None,
                     params: dict | None = None, timeout: int = 30,
                     max_pages: int = 30) -> tuple[pd.DataFrame, dict]:
    """Fetch paginated ODCloud JSON/XML records; credentials come only from env vars."""
    endpoint=(endpoint or os.getenv("KOSHA_API_URL",DEFAULT_ENDPOINT)).strip()
    key=service_key or os.getenv("KOSHA_SERVICE_KEY","")
    if not key:
        raise ValueError("KOSHA_SERVICE_KEY가 설정되지 않았습니다. Render/Streamlit Secrets에 인증키를 등록하세요.")
    query=dict(params or load_env_params())
    query.setdefault("page",1)
    query.setdefault("perPage",100)
    if not any(k.lower() in {"servicekey","service_key"} for k in query):
        query["serviceKey"]=key
    headers={"Accept":"application/json, application/xml, text/xml"}
    records_all=[]
    fmt="unknown"
    status=None
    total=None
    response_keys=[]
    start_page=int(query.get("page",1))
    page_size=int(query.get("perPage",100))
    for page_no in range(start_page,start_page+max_pages):
        page_query=dict(query)
        page_query["page"]=page_no
        response=requests.get(endpoint,params=page_query,headers=headers,timeout=timeout)
        response.raise_for_status()
        if status is None:
            status=response.status_code
        ctype=response.headers.get("content-type","").lower()
        body=response.text.lstrip()
        if "json" in ctype or body.startswith("{") or body.startswith("["):
            payload=response.json()
            page_records=_extract_records(payload)
            fmt="JSON"
            if isinstance(payload,dict):
                response_keys=list(payload.keys())
                total=payload.get("matchCount",payload.get("totalCount",payload.get("total_count",total)))
        elif body.startswith("<") or "xml" in ctype:
            root=ET.fromstring(response.content)
            page_records=_flatten_xml(root)
            fmt="XML"
        else:
            raise ValueError(f"지원하지 않는 응답 형식: {ctype or 'unknown'}")
        if not page_records:
            if not records_all:
                raise ValueError("API 응답에 데이터 레코드가 없습니다. 인증키와 요청변수를 확인하세요. 응답 일부: "+body[:1000])
            break
        records_all.extend(page_records)
        if len(page_records)<page_size:
            break
        if total is not None and len(records_all)>=int(total):
            break
    if not records_all:
        raise ValueError("API에서 산재 사례를 가져오지 못했습니다.")
    metadata={"format":fmt,"http_status":status,"record_count":len(records_all),
              "total_count":total,"response_keys":response_keys,"endpoint":endpoint,
              "page_size":page_size}
    return pd.DataFrame.from_records(records_all),metadata

def load_env_params() -> dict:
    raw=os.getenv("KOSHA_API_PARAMS_JSON","").strip()
    if not raw:
        return {"page":1,"perPage":100}
    try:
        value=json.loads(raw)
    except json.JSONDecodeError as exc:
        raise ValueError("KOSHA_API_PARAMS_JSON은 JSON 객체여야 합니다.") from exc
    if not isinstance(value,dict):
        raise ValueError("KOSHA_API_PARAMS_JSON은 JSON 객체여야 합니다.")
    return value
