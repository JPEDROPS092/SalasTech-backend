from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
import os
from pathlib import Path


def add(app: FastAPI):
    # Check for static directory in the app folder (preferred location)
    app_static_dir = Path("app/static")
    root_static_dir = Path("static")
    
    if app_static_dir.exists() and app_static_dir.is_dir():
        app.mount("/static", StaticFiles(directory=str(app_static_dir)), name="static")
        print(f"Static files mounted from: {app_static_dir}")
    elif root_static_dir.exists() and root_static_dir.is_dir():
        app.mount("/static", StaticFiles(directory=str(root_static_dir)), name="static")
        print(f"Static files mounted from: {root_static_dir}")
    else:
        print("Warning: Static directory not found. Create 'app/static' or 'static' directory to serve static files.")
        # Create the directory if it doesn't exist
        app_static_dir.mkdir(parents=True, exist_ok=True)
        app.mount("/static", StaticFiles(directory=str(app_static_dir)), name="static")
        print(f"Created and mounted static directory: {app_static_dir}")