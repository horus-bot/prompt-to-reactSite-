import json
import re
from groq import Groq
import os
from dotenv import load_dotenv

load_dotenv()
groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))
MODEL_NAME = "llama-3.1-70b-versatile"

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