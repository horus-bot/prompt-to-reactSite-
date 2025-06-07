from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
from .agent.workflow import generate_website
from .agent.models import WebsiteRequest
import json

app = FastAPI(
    title="React Website Generator",
    description="Generate complete React websites using AI with professional design patterns",
    version="2.0.0"
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
        "message": "React Website Generator API v2.0",
        "description": "Generate professional React websites with AI",
        "features": [
            "🎨 Professional design patterns",
            "📱 Fully responsive layouts", 
            "⚛️ Modern React components",
            "🎭 Bootstrap 5 integration",
            "🔧 Custom CSS animations",
            "🚀 Production-ready code"
        ],
        "endpoints": {
            "generate": "/generate-website",
            "demo": "/demo",
            "flower_demo": "/demo/flower-shop",
            "tech_demo": "/demo/tech-platform",
            "fitness_demo": "/demo/fitness-studio",
            "docs": "/docs",
            "health": "/health"
        },
        "status": "online",
        "version": "2.0.0"
    }

@app.post("/generate-website")
async def generate_site(req: WebsiteRequest = None):
    """
    Generate a complete React website based on the provided specifications.
    
    The AI will automatically fill in any missing fields with professional content.
    Returns a ZIP file containing a complete, production-ready React application.
    """
    try:
        # Handle empty request body - create default request
        if req is None:
            req = WebsiteRequest()
        
        print(f"🚀 Received generation request")
        print(f"📝 Website description: {req.website_desc or 'Auto-generated'}")
        print(f"🎨 Primary color: {req.primary_color or 'Auto-generated'}")
        
        # Convert Pydantic model to dict, filtering out None values
        req_dict = {k: v for k, v in req.dict().items() if v is not None}
        
        # Generate the website using the new workflow
        zip_path = generate_website(
            website_desc=req_dict.get("website_desc", ""),
            landing_desc=req_dict.get("landing_desc", ""),
            main_desc=req_dict.get("main_desc", ""),
            checkout_desc=req_dict.get("checkout_desc", ""),
            primary_color=req_dict.get("primary_color", "#4f46e5"),
            secondary_color=req_dict.get("secondary_color", "#06b6d4"),
            logo_url=req_dict.get("logo_url", ""),
            nav_links=req_dict.get("nav_links", []),
            features=req_dict.get("features", []),
            pricing=req_dict.get("pricing", []),
            testimonials=req_dict.get("testimonials", []),
            faqs=req_dict.get("faqs", [])
        )
        
        # Verify ZIP file was created
        if not zip_path or not Path(zip_path).exists():
            raise HTTPException(
                status_code=500, 
                detail="Website generation failed - ZIP file not created"
            )
        
        file_size = Path(zip_path).stat().st_size / 1024  # Size in KB
        print(f"✅ Website generated successfully!")
        print(f"📦 ZIP file: {zip_path} ({file_size:.1f} KB)")
        
        return FileResponse(
            zip_path,
            media_type="application/zip",
            filename="react_website.zip",
            headers={
                "Content-Disposition": "attachment; filename=react_website.zip",
                "X-Generated-By": "AI Website Generator v2.0",
                "X-File-Size": f"{file_size:.1f}KB"
            }
        )
        
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        error_msg = f"Generation error: {str(e)}"
        print(f"❌ {error_msg}")
        raise HTTPException(status_code=500, detail=error_msg)

@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring."""
    return {
        "status": "healthy", 
        "service": "React Website Generator",
        "version": "2.0.0",
        "features": {
            "cors_enabled": True,
            "ai_generation": True,
            "modular_architecture": True,
            "professional_designs": True
        },
        "dependencies": {
            "fastapi": "✅ Running",
            "groq": "✅ Connected",
            "langgraph": "✅ Active"
        }
    }

@app.get("/demo")
async def generate_demo_site():
    """Generate a demo website with AI-powered productivity platform theme."""
    try:
        demo_req = WebsiteRequest(
            website_desc="TaskFlow - AI-powered productivity platform that revolutionizes team collaboration",
            landing_desc="Supercharge your team's productivity with our intelligent workflow automation platform",
            primary_color="#4f46e5",
            secondary_color="#06b6d4"
        )
        
        return await generate_site(demo_req)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Demo generation error: {str(e)}")

@app.get("/demo/flower-shop")
async def generate_flower_shop_demo():
    """Generate a premium flower delivery service demo website."""
    try:
        demo_req = WebsiteRequest(
            website_desc="BloomCraft - Premium artisanal flower delivery service specializing in handcrafted bouquets",
            landing_desc="Transform special moments into unforgettable memories with our exquisite handcrafted floral arrangements",
            main_desc="Explore our curated collection of premium flowers sourced from local eco-friendly growers",
            checkout_desc="Complete your floral journey with confidence. Same-day delivery available with our freshness guarantee",
            primary_color="#d946ef",
            secondary_color="#06b6d4"
        )
        
        return await generate_site(demo_req)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Flower shop demo error: {str(e)}")

@app.get("/demo/tech-platform")
async def generate_tech_platform_demo():
    """Generate a modern tech platform demo website."""
    try:
        demo_req = WebsiteRequest(
            website_desc="CloudSync - Advanced cloud infrastructure platform for modern businesses",
            landing_desc="Scale your applications effortlessly with our enterprise-grade cloud infrastructure",
            primary_color="#1e293b",
            secondary_color="#0ea5e9"
        )
        
        return await generate_site(demo_req)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Tech platform demo error: {str(e)}")

@app.get("/demo/fitness-studio")
async def generate_fitness_studio_demo():
    """Generate a premium fitness studio demo website."""
    try:
        demo_req = WebsiteRequest(
            website_desc="FitnessPro Studio - Premium fitness center with personal training and wellness programs",
            landing_desc="Transform your body and mind with our state-of-the-art fitness facility and expert personal trainers",
            primary_color="#10b981",
            secondary_color="#f59e0b"
        )
        
        return await generate_site(demo_req)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Fitness studio demo error: {str(e)}")

@app.get("/demo/restaurant")
async def generate_restaurant_demo():
    """Generate a gourmet restaurant demo website."""
    try:
        demo_req = WebsiteRequest(
            website_desc="CloudKitchen - Gourmet food delivery with chef-curated meals and sustainable packaging",
            landing_desc="Experience restaurant-quality cuisine delivered fresh to your door by award-winning chefs",
            primary_color="#ef4444",
            secondary_color="#f97316"
        )
        
        return await generate_site(demo_req)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Restaurant demo error: {str(e)}")

@app.get("/demo/agency")
async def generate_agency_demo():
    """Generate a digital marketing agency demo website."""
    try:
        demo_req = WebsiteRequest(
            website_desc="DigitalAgency Pro - Full-service digital marketing agency specializing in brand transformation",
            landing_desc="Elevate your brand with our comprehensive digital marketing solutions and cutting-edge strategies",
            primary_color="#7c3aed",
            secondary_color="#06b6d4"
        )
        
        return await generate_site(demo_req)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Agency demo error: {str(e)}")

@app.post("/generate-custom")
async def generate_custom_site(
    website_desc: str,
    primary_color: str = "#4f46e5",
    secondary_color: str = "#06b6d4",
    landing_desc: str = "",
    main_desc: str = "",
    checkout_desc: str = ""
):
    """
    Generate a custom website with minimal required parameters.
    
    This endpoint allows for quick generation with just basic parameters.
    All other content will be generated automatically by AI.
    """
    try:
        custom_req = WebsiteRequest(
            website_desc=website_desc,
            landing_desc=landing_desc,
            main_desc=main_desc,
            checkout_desc=checkout_desc,
            primary_color=primary_color,
            secondary_color=secondary_color
        )
        
        return await generate_site(custom_req)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Custom generation error: {str(e)}")

@app.get("/examples")
async def get_examples():
    """Get example inputs for the website generator."""
    return {
        "examples": [
            {
                "name": "Flower Shop",
                "input": {
                    "website_desc": "BloomCraft - Premium flower delivery service",
                    "primary_color": "#d946ef",
                    "secondary_color": "#06b6d4"
                },
                "demo_url": "/demo/flower-shop"
            },
            {
                "name": "Tech Platform", 
                "input": {
                    "website_desc": "CloudSync - Advanced cloud infrastructure platform",
                    "primary_color": "#1e293b",
                    "secondary_color": "#0ea5e9"
                },
                "demo_url": "/demo/tech-platform"
            },
            {
                "name": "Fitness Studio",
                "input": {
                    "website_desc": "FitnessPro Studio - Premium fitness center",
                    "primary_color": "#10b981",
                    "secondary_color": "#f59e0b"
                },
                "demo_url": "/demo/fitness-studio"
            },
            {
                "name": "Restaurant",
                "input": {
                    "website_desc": "CloudKitchen - Gourmet food delivery",
                    "primary_color": "#ef4444", 
                    "secondary_color": "#f97316"
                },
                "demo_url": "/demo/restaurant"
            },
            {
                "name": "Digital Agency",
                "input": {
                    "website_desc": "DigitalAgency Pro - Full-service marketing agency",
                    "primary_color": "#7c3aed",
                    "secondary_color": "#06b6d4"
                },
                "demo_url": "/demo/agency"
            }
        ],
        "curl_examples": [
            {
                "name": "Basic Generation",
                "command": """curl -X POST "http://localhost:8000/generate-website" \\
     -H "Content-Type: application/json" \\
     -d '{"website_desc": "My Company - Description"}' \\
     --output website.zip"""
            },
            {
                "name": "Custom Colors",
                "command": """curl -X POST "http://localhost:8000/generate-website" \\
     -H "Content-Type: application/json" \\
     -d '{"website_desc": "My Company", "primary_color": "#ff6b6b", "secondary_color": "#4ecdc4"}' \\
     --output website.zip"""
            }
        ]
    }

@app.get("/status")
async def get_status():
    """Get detailed service status and statistics."""
    try:
        output_dir = Path("output")
        generated_files = list(output_dir.glob("*.zip")) if output_dir.exists() else []
        
        return {
            "service": "React Website Generator",
            "version": "2.0.0",
            "status": "operational",
            "features": {
                "ai_powered_generation": True,
                "professional_templates": True,
                "responsive_design": True,
                "bootstrap_integration": True,
                "custom_animations": True,
                "production_ready": True
            },
            "statistics": {
                "generated_websites": len(generated_files),
                "output_directory": str(output_dir),
                "latest_generation": generated_files[-1].name if generated_files else "None"
            },
            "endpoints": {
                "generation": "/generate-website",
                "custom": "/generate-custom", 
                "demos": ["/demo", "/demo/flower-shop", "/demo/tech-platform", "/demo/fitness-studio"],
                "utilities": ["/health", "/status", "/examples"]
            }
        }
    except Exception as e:
        return {
            "service": "React Website Generator",
            "version": "2.0.0", 
            "status": "error",
            "error": str(e)
        }

if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting React Website Generator v2.0...")
    print("📖 Documentation: http://localhost:8000/docs")
    print("🌐 API Root: http://localhost:8000/")
    print("🎨 Demo Sites: http://localhost:8000/demo")
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)