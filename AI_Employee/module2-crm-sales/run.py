import os
import sys
from pathlib import Path

module_dir = Path(__file__).resolve().parent
sys.path.insert(0, str(module_dir))
os.chdir(module_dir)

import uvicorn

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)
