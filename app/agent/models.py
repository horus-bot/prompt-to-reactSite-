from typing import TypedDict, List, Optional
from pydantic import BaseModel
import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()
groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))
MODEL_NAME = "llama-3.1-70b-versatile"

class AgentState(TypedDict):
    website_desc: str
    landing_desc: str
    main_desc: str
    checkout_desc: str
    primary_color: str
    secondary_color: str
    logo_url: str
    nav_links: list
    features: list
    pricing: list
    testimonials: list
    faqs: list
    components: dict[str, str]
    component_css: dict[str, str]
    pages: dict[str, str]
    page_css: dict[str, str]
    react_project: dict[str, dict[str, str]]
    zip_path: str | None

class NavLink(BaseModel):
    name: str
    url: str

class Feature(BaseModel):
    icon: str
    title: str
    description: str

class PricingPlan(BaseModel):
    name: str
    price: str
    features: List[str]
    recommended: bool = False

class Testimonial(BaseModel):
    name: str
    avatar: Optional[str]
    quote: str

class FAQItem(BaseModel):
    question: str
    answer: str

class WebsiteRequest(BaseModel):
    website_desc: Optional[str] = None
    landing_desc: Optional[str] = None
    main_desc: Optional[str] = None
    checkout_desc: Optional[str] = None
    primary_color: Optional[str] = None
    secondary_color: Optional[str] = None
    logo_url: Optional[str] = None
    nav_links: Optional[List[NavLink]] = None
    features: Optional[List[Feature]] = None
    pricing: Optional[List[PricingPlan]] = None
    testimonials: Optional[List[Testimonial]] = None
    faqs: Optional[List[FAQItem]] = None
    
    class Config:
        extra = "ignore"