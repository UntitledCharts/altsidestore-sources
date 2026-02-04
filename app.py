import json, os
from fastapi import FastAPI, HTTPException, status, Request
from fastapi.responses import FileResponse

app = FastAPI(openapi_url=None, docs_url=None, redoc_url=None)

# most simple fastest fastapi app i've ever coded

with open("repo.json", "r", encoding="utf-8") as f:
    repo = json.load(f)

assets: dict[str, str] = {}
ASSETS_ROOT = "assets"


def format_host(obj, host: str):
    if isinstance(obj, dict):
        return {k: format_host(v, host) for k, v in obj.items()}

    if isinstance(obj, list):
        return [format_host(v, host) for v in obj]

    if isinstance(obj, str) and obj.startswith("file://"):
        path = obj.removeprefix("file://")

        if path.startswith("assets/"):
            rel_path = path[len("assets/") :]
            fs_path = os.path.join(ASSETS_ROOT, rel_path)

            assets[rel_path] = fs_path
            return f"https://{host}/assets/{rel_path}"

    return obj


@app.get("/")
async def get_repo(request: Request):
    return format_host(repo, request.headers.get("host", "example.com"))


@app.get("/assets/{asset_path:path}")
async def get_asset(asset_path: str):
    fs_path = assets.get(asset_path)
    if not fs_path or not os.path.isfile(fs_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Asset not found"
        )
    return FileResponse(fs_path)
