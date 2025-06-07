import os
import zipfile
import json
import re
from pathlib import Path
from typing import TypedDict
from langgraph.graph import Graph
from groq import Groq
from dotenv import load_dotenv
from pydantic import BaseModel
from typing import List, Optional

# Import from modular files
from .models import AgentState, WebsiteRequest, NavLink, Feature, PricingPlan, Testimonial, FAQItem
from .llm_utils import groq_client, MODEL_NAME
from .code_utils import extract_code_and_css, extract_code, clean_imports
from .css_utils import clean_css, add_professional_css_patterns
from .logo_generator import generate_professional_logo
from .component_generator import generate_components
from .page_generator import generate_pages
from .project_compiler import compile_project, create_zip_file

def llm_fill_field(field_name: str, field_description: str, context: dict) -> any:
    """Use LLM to generate a default value for a missing field"""
    
    field_prompts = {
        "website_desc": "Generate a professional, concise description (1-2 sentences) for a modern SaaS/tech platform.",
        "landing_desc": "Generate a compelling hero section welcome message (1-2 sentences) that encourages visitors to explore the platform.",
        "main_desc": "Generate a description for the main features page that showcases the platform's capabilities.",
        "checkout_desc": "Generate an encouraging checkout page description that builds trust and motivates purchase completion.",
        "primary_color": "Generate a modern, professional primary brand color in hex format (e.g., #4f46e5). Return only the hex color.",
        "secondary_color": "Generate a complementary secondary brand color in hex format (e.g., #06b6d4). Return only the hex color.",
        "logo_url": "Return an empty string - logos will be text-based.",
        "nav_links": """Generate 5 navigation links as JSON array. Format: [{"name": "Home", "url": "/"}, {"name": "Features", "url": "/main"}, {"name": "Pricing", "url": "/#pricing"}, {"name": "About", "url": "/#about"}, {"name": "Get Started", "url": "/checkout"}]. Return only valid JSON array.""",
        "features": """Generate 6 compelling features as JSON array. Format: [{"icon": "bi-star", "title": "Feature Name", "description": "Brief feature description"}]. Use Bootstrap icon names (bi-*). Return only valid JSON array.""",
        "pricing": """Generate 3 pricing plans as JSON array. Format: [{"name": "Basic", "price": "$9/month", "features": ["Feature 1", "Feature 2", "Feature 3"], "recommended": false}, {"name": "Pro", "price": "$29/month", "features": ["Everything in Basic", "Feature 4", "Feature 5"], "recommended": true}, {"name": "Enterprise", "price": "$99/month", "features": ["Everything in Pro", "Feature 6", "Feature 7"], "recommended": false}]. Return only valid JSON array.""",
        "testimonials": """Generate 4 customer testimonials as JSON array. Format: [{"name": "John Smith", "quote": "Great platform! Really improved our productivity.", "avatar": "https://via.placeholder.com/80x80/4f46e5/ffffff?text=JS"}]. Return only valid JSON array.""",
        "faqs": """Generate 6 FAQs as JSON array. Format: [{"question": "How does it work?", "answer": "Detailed answer explaining the process."}]. Return only valid JSON array."""
    }
    
    prompt = field_prompts.get(field_name, f"Generate appropriate content for {field_name}: {field_description}")
    
    # Add context if available
    if context:
        context_str = ", ".join([f"{k}: {v}" for k, v in context.items() if v])
        prompt += f"\n\nContext from other fields: {context_str}"
        prompt += "\n\nMake sure the generated content is consistent with the provided context."
    
    prompt += f"\n\nReturn ONLY the requested content in the exact format specified. No explanations or additional text."
    
    try:
        response = groq_client.chat.completions.create(
            model=MODEL_NAME,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=1000,
            timeout=30  # Add timeout
        )
        
        content = response.choices[0].message.content.strip()
        
        # Try to parse JSON for array fields
        if field_name in ["nav_links", "features", "pricing", "testimonials", "faqs"]:
            try:
                return json.loads(content)
            except json.JSONDecodeError:
                # Extract JSON from content if wrapped in markdown
                json_match = re.search(r'\[.*\]', content, re.DOTALL)
                if json_match:
                    return json.loads(json_match.group())
                
                # Return default values if JSON parsing fails
                return get_default_value(field_name)
        
        return content
        
    except Exception as e:
        print(f"Error generating field {field_name}: {e}")
        return get_default_value(field_name)

def get_default_value(field_name: str):
    """Get default values for fields"""
    defaults = {
        "website_desc": "Modern AI-powered platform designed to boost productivity and streamline workflows",
        "landing_desc": "Welcome to the future of productivity. Transform how you work with our innovative platform.",
        "main_desc": "Discover powerful features designed to enhance your workflow and boost team collaboration.",
        "checkout_desc": "Join thousands of satisfied customers. Choose your plan and start your journey today.",
        "primary_color": "#4f46e5",
        "secondary_color": "#06b6d4",
        "logo_url": "",
        "nav_links": [
            {"name": "Home", "url": "/"},
            {"name": "Features", "url": "/main"},
            {"name": "Pricing", "url": "/#pricing"},
            {"name": "About", "url": "/#about"},
            {"name": "Get Started", "url": "/checkout"}
        ],
        "features": [
            {"icon": "bi-lightning", "title": "Fast & Efficient", "description": "Lightning-fast performance for all your needs"},
            {"icon": "bi-shield-check", "title": "Secure & Safe", "description": "Enterprise-grade security for your data"},
            {"icon": "bi-people", "title": "Team Collaboration", "description": "Work together seamlessly with your team"},
            {"icon": "bi-graph-up", "title": "Analytics & Insights", "description": "Detailed analytics to track your progress"},
            {"icon": "bi-mobile", "title": "Mobile Ready", "description": "Access from anywhere on any device"},
            {"icon": "bi-headset", "title": "24/7 Support", "description": "Round-the-clock customer support"}
        ],
        "pricing": [
            {"name": "Starter", "price": "$9/month", "features": ["5 Projects", "10GB Storage", "Email Support"], "recommended": False},
            {"name": "Professional", "price": "$29/month", "features": ["Unlimited Projects", "100GB Storage", "Priority Support", "Advanced Analytics"], "recommended": True},
            {"name": "Enterprise", "price": "$99/month", "features": ["Everything in Pro", "Unlimited Storage", "Dedicated Support", "Custom Integrations"], "recommended": False}
        ],
        "testimonials": [
            {"name": "Sarah Johnson", "quote": "This platform has transformed how we work. Highly recommended!", "avatar": "https://via.placeholder.com/80x80/4f46e5/ffffff?text=SJ"},
            {"name": "Mike Chen", "quote": "Incredible features and excellent support team. Worth every penny.", "avatar": "https://via.placeholder.com/80x80/06b6d4/ffffff?text=MC"},
            {"name": "Emily Davis", "quote": "User-friendly interface with powerful capabilities. Love it!", "avatar": "https://via.placeholder.com/80x80/10b981/ffffff?text=ED"},
            {"name": "Alex Rodriguez", "quote": "Game-changer for our productivity. Couldn't imagine working without it.", "avatar": "https://via.placeholder.com/80x80/f59e0b/ffffff?text=AR"}
        ],
        "faqs": [
            {"question": "How do I get started?", "answer": "Simply sign up for an account and follow our guided onboarding process."},
            {"question": "Is there a free trial?", "answer": "Yes, we offer a 14-day free trial with full access to all features."},
            {"question": "Can I cancel anytime?", "answer": "Absolutely! You can cancel your subscription at any time with no penalties."},
            {"question": "What payment methods do you accept?", "answer": "We accept all major credit cards, PayPal, and bank transfers."},
            {"question": "Is my data secure?", "answer": "Yes, we use enterprise-grade encryption and security measures to protect your data."},
            {"question": "Do you offer customer support?", "answer": "Yes, we provide 24/7 customer support via email, chat, and phone."}
        ]
    }
    
    return defaults.get(field_name, "")

# Workflow Graph Functions
def initialize_state(data: dict) -> AgentState:
    """Initialize state with user input and fill missing fields"""
    print("🚀 Initializing website generation...")
    
    # Create state dictionary properly
    state = {
        "website_desc": "",
        "landing_desc": "",
        "main_desc": "",
        "checkout_desc": "",
        "primary_color": "#4f46e5",
        "secondary_color": "#06b6d4",
        "logo_url": "",
        "nav_links": [],
        "features": [],
        "pricing": [],
        "testimonials": [],
        "faqs": [],
        "components": {},
        "component_css": {},
        "pages": {},
        "page_css": {},
        "react_project": {},
        "zip_path": None
    }
    
    # Copy provided fields
    for key, value in data.items():
        if key in state and value is not None:
            state[key] = value
    
    # Fill missing fields with LLM or defaults
    context = {k: v for k, v in state.items() if v and k not in ["components", "component_css", "pages", "page_css", "react_project"]}
    
    field_descriptions = {
        "website_desc": "A brief, professional description of what this website/platform does",
        "landing_desc": "Compelling welcome message for the landing page hero section",
        "main_desc": "Description for the main features/product page",
        "checkout_desc": "Professional checkout page description encouraging users to complete purchase",
        "primary_color": "Primary brand color in hex format",
        "secondary_color": "Secondary brand color in hex format",
        "logo_url": "URL to brand logo image or empty for text-based logo",
        "nav_links": "Array of navigation menu items with name and url",
        "features": "Array of 6 key features with icon, title, and description",
        "pricing": "Array of 3 pricing plans with name, price, features list, and recommended flag",
        "testimonials": "Array of 4 customer testimonials with name, quote, and avatar",
        "faqs": "Array of 6 frequently asked questions with question and answer"
    }
    
    for field_name, field_info in field_descriptions.items():
        if not state.get(field_name):
            try:
                print(f"🔄 Generating {field_name}...")
                state[field_name] = llm_fill_field(field_name, field_info, context)
                context[field_name] = state[field_name]
                print(f"✅ Generated {field_name}")
            except Exception as e:
                print(f"❌ Error generating {field_name}: {e}")
                state[field_name] = get_default_value(field_name)
                context[field_name] = state[field_name]
    
    print(f"🎯 State initialized with all required fields")
    return state

def generate_logo_step(state: AgentState) -> AgentState:
    """Generate professional logo component"""
    print("🎨 Generating logo component...")
    
    try:
        logo_jsx, logo_css = generate_professional_logo(state)
        state["components"]["Logo"] = logo_jsx
        state["component_css"]["Logo"] = logo_css
        print("✅ Logo component generated successfully")
    except Exception as e:
        print(f"❌ Error generating logo: {e}")
        # Add fallback logo
        state["components"]["Logo"] = """import React from 'react';
import './Logo.css';

export default function Logo({ className = '' }) {
  return (
    <div className={`logo-container ${className}`}>
      <div className="text-logo">
        <span className="company-name">Company</span>
        <span className="logo-dot"></span>
      </div>
    </div>
  );
}"""
        state["component_css"]["Logo"] = """.logo-container {
  display: inline-flex;
  align-items: center;
}

.text-logo {
  font-size: 1.5rem;
  font-weight: 800;
  color: var(--primary-color, #4f46e5);
}

.logo-dot {
  height: 8px;
  width: 8px;
  border-radius: 50%;
  background-color: var(--primary-color, #4f46e5);
  margin-left: 4px;
}"""
    
    return state

def generate_components_step(state: AgentState) -> AgentState:
    """Generate all React components"""
    print("🧩 Generating React components...")
    return generate_components(state)

def generate_pages_step(state: AgentState) -> AgentState:
    """Generate all pages"""
    print("📄 Generating pages...")
    return generate_pages(state)

def compile_step(state: AgentState) -> AgentState:
    """Compile the React project"""
    print("🔧 Compiling React project...")
    return compile_project(state)

def create_zip_step(state: AgentState) -> AgentState:
    """Create downloadable ZIP file"""
    print("📦 Creating ZIP file...")
    return create_zip_file(state)

# Create Workflow Graph
def create_workflow():
    """Create the LangGraph workflow"""
    workflow = Graph()
    
    # Add nodes
    workflow.add_node("initialize", initialize_state)
    workflow.add_node("generate_logo", generate_logo_step)
    workflow.add_node("generate_components", generate_components_step)
    workflow.add_node("generate_pages", generate_pages_step)
    workflow.add_node("compile", compile_step)
    workflow.add_node("create_zip", create_zip_step)
    
    # Add edges (execution flow)
    workflow.add_edge("initialize", "generate_logo")
    workflow.add_edge("generate_logo", "generate_components")
    workflow.add_edge("generate_components", "generate_pages")
    workflow.add_edge("generate_pages", "compile")
    workflow.add_edge("compile", "create_zip")
    
    # Set entry point
    workflow.set_entry_point("initialize")
    
    return workflow.compile()

# Main generation function
def generate_website(
    website_desc: str,
    landing_desc: str = "",
    main_desc: str = "",
    checkout_desc: str = "",
    primary_color: str = "#4f46e5",
    secondary_color: str = "#06b6d4",
    logo_url: str = "",
    nav_links: list = None,
    features: list = None,
    pricing: list = None,
    testimonials: list = None,
    faqs: list = None
) -> str:
    """
    Generate a complete React website based on specifications
    
    Returns:
        str: Path to the generated ZIP file
    """
    
    print("🌟 Starting website generation process...")
    
    # Prepare input data
    input_data = {
        "website_desc": website_desc,
        "landing_desc": landing_desc,
        "main_desc": main_desc,
        "checkout_desc": checkout_desc,
        "primary_color": primary_color,
        "secondary_color": secondary_color,
        "logo_url": logo_url,
        "nav_links": nav_links or [],
        "features": features or [],
        "pricing": pricing or [],
        "testimonials": testimonials or [],
        "faqs": faqs or []
    }
    
    try:
        # Create and run workflow
        workflow = create_workflow()
        result = workflow.invoke(input_data)
        
        zip_path = result.get("zip_path")
        if zip_path and Path(zip_path).exists():
            print(f"🎉 Website generated successfully!")
            print(f"📁 ZIP file created: {zip_path}")
            print(f"📊 File size: {Path(zip_path).stat().st_size / 1024:.1f} KB")
            return zip_path
        else:
            raise Exception("ZIP file was not created successfully")
            
    except Exception as e:
        print(f"❌ Error during generation: {e}")
        raise e

# Compatibility functions for existing code
def llm_fill_field_legacy(field_name: str, description: str, context: dict):
    """Legacy function for backward compatibility"""
    return llm_fill_field(field_name, description, context)

if __name__ == "__main__":
    # Test the workflow
    test_result = generate_website(
        website_desc="BloomCraft - Premium flower delivery service",
        primary_color="#d946ef",
        secondary_color="#06b6d4"
    )
    print(f"Test completed: {test_result}")