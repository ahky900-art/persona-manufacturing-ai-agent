"""Configurable client for a public-data REST API. Never hard-code service keys."""
from __future__ import annotations
import json
import os
import xml.etree.ElementTree as ET
from typing import Any
import pandas as pd
import requests

def _flatten_xml(element: ET.Element) -> list[dict[str, Any]]:
    # Most Korean public-data APIs wrap records in <items><item>...</item></items>.
    records=[]
    for node in element.iter():
        if node.tag.split("}")[-1].lower() in {"item","row","record"}:
            records.append({child.tag.split("}")[-1]: (child.text or "").strip() for child in list(node)})
    if records:
        return records
    return [{child.tag.split("}")[-1]: (child.text or "").strip() for child in list(element)}]

def _extract_records(payload: Any) -> list[dict[str, Any]]:
    if isinstance(payload, list):
        return [x for x in payload if isinstance(x, dict)]
    if not isinstance(payload, dict):
        return []
    # Common Korean OpenAPI response wrappers
    for key in ("items","item","list","data","results","records","response"):
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
                     params: dict | None = None, timeout: int = 30) -> tuple[pd.DataFrame, dict]:
    """Fetch one API page. Endpoint/key default to KOSHA_API_URL/KOSHA_SERVICE_KEY env vars."""
    endpoint=(endpoint or os.getenv("KOSHA_API_URL","")).strip()
    key=service_key or os.getenv("KOSHA_SERVICE_KEY","")
    if not endpoint:
        raise ValueError("KOSHA_API_URL이 설정되지 않았습니다. 공공데이터포털 API 명세의 '요청주소'가 필요합니다.")
    if not key:
        raise ValueError("KOSHA_SERVICE_KEY가 설정되지 않았습니다. Render/Streamlit Secrets에 서비스키를 등록하세요.")
    query=dict(params or {})
    # Support the common public-data portal parameter names; endpoint-specific parameters
    # should be supplied in KOSHA_API_PARAMS_JSON.
    if not any(k.lower() in {"servicekey","service_key"} for k in query):
        query["serviceKey"]=key
    headers={"Accept":"application/json, application/xml, text/xml"}
    response=requests.get(endpoint,params=query,headers=headers,timeout=timeout)
    response.raise_for_status()
    content_type=response.headers.get("content-type","").lower()
    body=response.text.lstrip()
    if "json" in content_type or body.startswith("{") or body.startswith("["):
        payload=response.json()
        records=_extract_records(payload)
        metadata={"format":"JSON","http_status":response.status_code,"record_count":len(records),"response_keys":list(payload.keys()) if isinstance(payload,dict) else []}
    elif body.startswith("<") or "xml" in content_type:
        root=ET.fromstring(response.content)
        records=_flatten_xml(root)
        metadata={"format":"XML","http_status":response.status_code,"record_count":len(records),"root":root.tag}
    else:
        raise ValueError(f"지원하지 않는 응답 형식입니다: {content_type or 'unknown'}")
    if not records:
        # Surface API error code/message without exposing the service key.
        error_text=body[:1200]
        raise ValueError("API 응답에서 레코드를 찾지 못했습니다. 응답 래퍼/요청변수를 확인하세요. 응답 일부: "+error_text)
    return pd.DataFrame.from_records(records), metadata

def load_env_params() -> dict:
    raw=os.getenv("KOSHA_API_PARAMS_JSON","").strip()
    if not raw:
        return {"pageNo":"1","numOfRows":"100","type":"json"}
    try:
        value=json.loads(raw)
    except json.JSONDecodeError as exc:
        raise ValueError("KOSHA_API_PARAMS_JSON은 JSON 객체여야 합니다.") from exc
    if not isinstance(value,dict):
        raise ValueError("KOSHA_API_PARAMS_JSON은 JSON 객체여야 합니다.")
    return value
