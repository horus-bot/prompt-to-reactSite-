from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
from pathlib import Path
from agent.workflow import generate_website as workflow_generate_website
import os

app = FastAPI()

class WebsiteRequest(BaseModel):
    website_desc: str
    landing_desc: str
    main_desc: str
    checkout_desc: str

@app.post("/generate-website")
async def generate_site(req: WebsiteRequest):
    try:
        zip_path = workflow_generate_website(
            req.website_desc,
            req.landing_desc,
            req.main_desc,
            req.checkout_desc
        )
        if not Path(zip_path).exists():
            raise HTTPException(500, "Generation failed")
        
        return FileResponse(
            zip_path,
            media_type="application/zip",
            filename="react_website.zip"
        )
    except Exception as e:
        print("ERROR:", e)
        raise HTTPException(500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 10000))
    uvicorn.run("app.main:app", host="0.0.0.0", port=port)