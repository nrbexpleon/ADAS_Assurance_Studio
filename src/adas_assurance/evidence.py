from __future__ import annotations
import copy,hashlib,hmac,json
from datetime import datetime,timezone

def canonical(value)->bytes:return json.dumps(value,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode()
def create_evidence(report:dict)->dict:
    body={"schema_version":"1.0","generated_at":datetime.now(timezone.utc).isoformat(),"report":copy.deepcopy(report)}
    return {**body,"integrity":{"algorithm":"sha256","digest":hashlib.sha256(canonical(body)).hexdigest()}}
def verify_evidence(evidence:dict)->bool:
    integrity=evidence.get("integrity",{});body={k:v for k,v in evidence.items() if k!="integrity"}
    return integrity.get("algorithm")=="sha256" and hmac.compare_digest(integrity.get("digest",""),hashlib.sha256(canonical(body)).hexdigest())
