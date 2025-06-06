from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
from .agent.workflow import generate_website, WebsiteRequest, llm_fill_field
import json

app = FastAPI(
    title="React Website Generator",
    description="Generate complete React websites using AI",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

@app.get("/")
async def root():
    return {
        "message": "React Website Generator API",
        "docs": "/docs",
        "status": "online",
        "version": "1.0.0"
    }

@app.post("/generate-website")
async def generate_site(req: WebsiteRequest = None):
    """Generate a complete React website based on the provided specifications."""
    try:
        # Handle empty request body
        if req is None:
            req = WebsiteRequest()
        
        # Convert to dict for easier manipulation
        req_dict = req.dict()
        
        # Fill missing/empty fields using LLM
        context = {k: v for k, v in req_dict.items() if v}
        
        # Define field descriptions for LLM
        field_descriptions = {
            "website_desc": "A brief, professional description of what this website/platform does (e.g., 'AI-powered task management platform')",
            "landing_desc": "Compelling welcome message for the landing page hero section",
            "main_desc": "Description for the main features/product page",
            "checkout_desc": "Professional checkout page description encouraging users to complete purchase",
            "primary_color": "Primary brand color in hex format (e.g., #4f46e5)",
            "secondary_color": "Secondary brand color in hex format (e.g., #06b6d4)",
            "logo_url": "URL to brand logo image or empty for text-based logo",
            "nav_links": "Array of navigation menu items with name and url",
            "features": "Array of 6 key features with icon, title, and description",
            "pricing": "Array of 3 pricing plans with name, price, features list, and recommended flag",
            "testimonials": "Array of 4 customer testimonials with name, quote, and avatar",
            "faqs": "Array of 6 frequently asked questions with question and answer"
        }
        
        # Fill missing fields with LLM-generated content
        for field_name, field_info in WebsiteRequest.__fields__.items():
            if not req_dict.get(field_name):
                description = field_descriptions.get(field_name, f"Generate content for {field_name}")
                req_dict[field_name] = llm_fill_field(field_name, description, context)
                context[field_name] = req_dict[field_name]
        
        # Generate the website
        zip_path = generate_website(
            req_dict["website_desc"],
            req_dict["landing_desc"],
            req_dict["main_desc"],
            req_dict["checkout_desc"],
            req_dict["primary_color"],
            req_dict["secondary_color"],
            req_dict["logo_url"],
            req_dict["nav_links"],
            req_dict["features"],
            req_dict["pricing"],
            req_dict["testimonials"],
            req_dict["faqs"]
        )
        
        if not Path(zip_path).exists():
            raise HTTPException(status_code=500, detail="Website generation failed")
        
        return FileResponse(
            zip_path,
            media_type="application/zip",
            filename="react_website.zip"
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Generation error: {str(e)}")

@app.get("/health")
async def health_check():
    return {
        "status": "healthy", 
        "service": "React Website Generator",
        "version": "1.0.0",
        "cors_enabled": True
    }

@app.get("/demo")
async def generate_demo_site():
    """Generate a demo website with default values."""
    try:
        # Create demo request with minimal data
        demo_req = WebsiteRequest(
            website_desc="TaskFlow - AI-powered productivity platform"
        )
        
        return await generate_site(demo_req)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Demo generation error: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)