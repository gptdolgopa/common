from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import Dict, List, Optional
import subprocess
import json
import os

app = FastAPI(title="grpcui")

DATA_FILE = os.path.join(os.path.dirname(__file__), "projects.json")

def load_data() -> Dict:
    if not os.path.exists(DATA_FILE):
        return {"projects": {}, "endpoints": {}}
    with open(DATA_FILE, "r") as f:
        return json.load(f)

def save_data(data: Dict):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)

data = load_data()

class Endpoint(BaseModel):
    name: str
    address: str
    plaintext: bool = False
    insecure: bool = False
    metadata: Dict[str, str] = Field(default_factory=dict)
    methods: List[str] = Field(default_factory=list)

class Request(BaseModel):
    id: str
    endpoint: str
    method: str
    body: Optional[dict] = None
    metadata: Dict[str, str] = Field(default_factory=dict)
    plaintext: bool = False
    insecure: bool = False

@app.post("/endpoints")
def add_endpoint(ep: Endpoint):
    cmd = ["grpcurl"]
    if ep.insecure:
        cmd.append("-insecure")
    if ep.plaintext:
        cmd.append("-plaintext")
    for k, v in ep.metadata.items():
        cmd.extend(["-H", f"{k}: {v}"])
    cmd.append(ep.address)
    cmd.append("list")
    try:
        out = subprocess.check_output(cmd, text=True)
        ep.methods = out.strip().splitlines()
    except subprocess.CalledProcessError as e:
        raise HTTPException(status_code=400, detail=e.stderr)
    data["endpoints"][ep.name] = ep.model_dump()
    save_data(data)
    return ep

@app.get("/endpoints")
def list_endpoints():
    return list(data["endpoints"].values())

@app.post("/projects/{project}/requests")
def add_request(project: str, req: Request):
    projects = data.setdefault("projects", {})
    proj = projects.setdefault(project, [])
    proj.append(req.model_dump())
    save_data(data)
    return req

@app.get("/projects/{project}/requests")
def list_requests(project: str):
    return data.get("projects", {}).get(project, [])

@app.post("/projects/{project}/requests/{idx}/run")
def run_request(project: str, idx: int):
    try:
        req = data["projects"][project][idx]
    except (KeyError, IndexError):
        raise HTTPException(status_code=404, detail="request not found")
    ep = data["endpoints"].get(req["endpoint"])
    if not ep:
        raise HTTPException(status_code=404, detail="endpoint not found")

    cmd = ["grpcurl"]
    if req.get("insecure") or ep.get("insecure"):
        cmd.append("-insecure")
    if req.get("plaintext") or ep.get("plaintext"):
        cmd.append("-plaintext")
    for k, v in {**ep.get("metadata", {}), **req.get("metadata", {})}.items():
        cmd.extend(["-H", f"{k}: {v}"])
    cmd.extend(["-d", json.dumps(req.get("body") or {})])
    cmd.append(ep["address"])
    cmd.append(req["method"])
    try:
        out = subprocess.check_output(cmd, stderr=subprocess.STDOUT, text=True)
    except subprocess.CalledProcessError as e:
        raise HTTPException(status_code=400, detail=e.output)
    return JSONResponse(content={"result": out})
