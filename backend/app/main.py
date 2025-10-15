import os, json, yaml
from typing import List, Dict, Any, Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

WORKSPACE = os.getenv("WORKSPACE", "/workspace")
ROLES_DIR = os.path.join(WORKSPACE, os.getenv("RELATIVE_ROLES_DIR", "roles"))
CATEGORIES_FILE = os.path.join(WORKSPACE, os.getenv("RELATIVE_CATEGORIES_FILE", "roles/categories.yml"))

app = FastAPI(
    title="Infinito Inventory Builder API",
    description="REST backend for dynamically generating inventories from Infinito.Nexus roles.",
    version="0.1.0"
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], allow_credentials=True,
    allow_methods=["*"], allow_headers=["*"]
)

def load_yaml(path: str) -> Dict[str, Any]:
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}

def load_json(path: str) -> Any:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def get_categories() -> Dict[str, Any]:
    return load_yaml(CATEGORIES_FILE)

def get_role_list() -> List[str]:
    lp = os.path.join(ROLES_DIR, "list.json")
    if os.path.exists(lp):
        return load_json(lp)
    # Fallback: Verzeichnisse scannen
    return sorted([
        d for d in os.listdir(ROLES_DIR)
        if os.path.isdir(os.path.join(ROLES_DIR, d)) and not d.startswith("_")
    ])

def flatten_categories_to_invokable_paths(cat: Dict[str, Any], prefix: List[str]=[]) -> Dict[str, bool]:
    invokable_map = {}
    roles = cat.get("roles", {})
    for key, node in roles.items():
        path = prefix + [key]
        invokable = bool(node.get("invokable", False))
        invokable_map["/".join(path)] = invokable
        invokable_map.update(flatten_categories_to_invokable_paths(node, path))
    return invokable_map

def role_is_invokable(role_id: str, cats: Dict[str, Any]) -> bool:
    inv_paths = {k for k, v in flatten_categories_to_invokable_paths(cats).items() if v}
    prefixes = [(p.replace("/", "-") + "-") for p in inv_paths]
    return any(role_id.startswith(pfx) for pfx in prefixes)

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/categories")
def categories():
    return get_categories()

@app.get("/roles")
def roles(invokable_only: bool = True) -> Dict[str, Any]:
    cats = get_categories()
    role_ids = get_role_list()
    if invokable_only:
        role_ids = [r for r in role_ids if role_is_invokable(r, cats)]
    return {"count": len(role_ids), "items": role_ids}

class InventoryRequest(BaseModel):
    host: str
    style: str = "group"          # "group" | "hostvars"
    ignore: Optional[List[str]] = []

def build_group_inventory(apps: List[str], host: str) -> Dict[str, Any]:
    groups = {app: {"hosts": [host]} for app in apps}
    return {
        "all": {"hosts": [host], "children": {app: {} for app in apps}},
        **groups
    }

def build_hostvar_inventory(apps: List[str], host: str) -> Dict[str, Any]:
    return {
        "all": {"hosts": [host]},
        "_meta": {"hostvars": {host: {"invokable_applications": apps}}}
    }

@app.post("/generate/inventory")
def generate_inventory(req: InventoryRequest):
    cats = get_categories()
    all_roles = [r for r in get_role_list() if role_is_invokable(r, cats)]
    if req.ignore:
        ignore = set(req.ignore)
        all_roles = [r for r in all_roles if r not in ignore]
    if req.style not in ("group", "hostvars"):
        raise HTTPException(status_code=400, detail="style must be 'group' or 'hostvars'")
    inv = build_group_inventory(all_roles, req.host) if req.style == "group" else build_hostvar_inventory(all_roles, req.host)
    content = yaml.safe_dump(inv, sort_keys=False, allow_unicode=True)
    return {"filename": "inventory.yml", "content": content}
