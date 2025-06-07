from .models import AgentState
from .code_utils import extract_code_and_css, clean_imports
from .css_utils import clean_css
from .llm_utils import groq_client, MODEL_NAME

def generate_landing_page(state: AgentState) -> AgentState:
    """Generate Landing Page using advanced Bootstrap and custom CSS"""
    components = ["Navbar", "Hero", "Features", "Pricing", "Testimonials", "FAQ", "Newsletter", "Footer", "ContactButton", "Logo"]
    desc = state["landing_desc"]
    primary_color = state.get("primary_color", "#0d6efd")
    secondary_color = state.get("secondary_color", "#6610f2")
    logo_url = state.get("logo_url", "")
    nav_links = state.get("nav_links", [])
    features = state.get("features", [])
    pricing = state.get("pricing", [])
    testimonials = state.get("testimonials", [])
    faqs = state.get("faqs", [])

    try:
        response = groq_client.chat.completions.create(
            model=MODEL_NAME,
            messages=[{
                "role": "user",
                "content": (
                    f"Create a visually stunning, highly interactive, and modern React landing page using components {', '.join(components)}. "
                    f"Description: {desc}. Use advanced Bootstrap 5 classes, gradients, glassmorphism, cards, shadows, carousels, modals, and color utilities for a premium SaaS experience. "
                    f"Theme the entire page using the primary color {primary_color} and secondary color {secondary_color} consistently throughout all sections. "
                    f"Logo URL: {logo_url}. Navigation links: {nav_links}. Features: {features}. Pricing: {pricing}. Testimonials: {testimonials}. FAQs: {faqs}. "
                    "Arrange components in this order: Navbar, Hero, Features, Pricing, Testimonials, FAQ, Newsletter, Footer, ContactButton. "
                    "Add section IDs for smooth scrolling: hero, features, pricing, testimonials, faq, newsletter. "
                    "Include scroll animations, particle effects (CSS only), interactive elements, and modern design patterns. "
                    "Use proper React Router Link components for navigation. Import { Link } from 'react-router-dom'. "
                    "Add React hooks (useState, useEffect, useNavigate) for interactivity, smooth scrolling, and dynamic content. "
                    "Include navigation buttons that link to /main and /checkout pages. "
                    "Return two code blocks: one with the React page (JSX, import './Landing.css'; at the top), and one with the CSS (in ```css code block). "
                    "Import all components from '../components/ComponentName', example: import Navbar from '../components/Navbar'. "
                    "Render all imported components with proper props and theming. "
                    "CRITICAL REQUIREMENTS:\n"
                    "- Use 'className' instead of 'class' for ALL HTML attributes\n"
                    "- Apply the primary and secondary colors consistently throughout\n"
                    "- Ensure all CSS syntax is valid and error-free\n"
                    "- CSS selectors must end with space then {{ not semicolon\n"
                    "- CSS properties must end with semicolon\n"
                    "- No comma-semicolon combinations like ',;'\n"
                    "- Use proper CSS syntax: selector {{ property: value; }}\n"
                    "- No FontAwesome dependencies - use Bootstrap Icons only\n"
                    "- Do NOT import any CSS files or external libraries except component CSS\n"
                    "- Do NOT reference local image files\n"
                    "- Add smooth animations and interactive elements\n"
                    "- Make it responsive and accessible\n"
                    "- Use React Router for navigation between pages\n"
                    "- No explanations, no markdown, no comments, no extra text."
                )
            }],
            temperature=0.3,
            max_tokens=3000
        )
        
        js_code, css_code = extract_code_and_css(response.choices[0].message.content)
        state.setdefault("pages", {})["Landing"] = clean_imports(js_code)
        state.setdefault("page_css", {})["Landing"] = clean_css(css_code)
        print("✅ Landing page generated successfully")
        
    except Exception as e:
        print(f"❌ Error generating landing page: {e}")
        # Add fallback landing page
        state.setdefault("pages", {})["Landing"] = get_fallback_landing_page(state)
        state.setdefault("page_css", {})["Landing"] = get_fallback_landing_css(state)
    
    return state

def generate_main_page(state: AgentState) -> AgentState:
    """Generate Main Page using advanced Bootstrap and custom CSS"""
    components = ["Navbar", "Sidebar", "Features", "Pricing", "Footer", "ContactButton", "Logo"]
    desc = state["main_desc"]
    primary_color = state.get("primary_color", "#0d6efd")
    secondary_color = state.get("secondary_color", "#6610f2")
    
    try:
        response = groq_client.chat.completions.create(
            model=MODEL_NAME,
            messages=[{
                "role": "user",
                "content": (
                    f"Create a professional, interactive React main page using components {', '.join(components)}. "
                    f"Description: {desc}. Use advanced Bootstrap 5 classes, cards, badges, gradients, and color utilities for a beautiful product showcase. "
                    f"Theme the page using primary color {primary_color} and secondary color {secondary_color} consistently. "
                    "Add at least 8 product/feature cards with hover effects, modal previews, and interactive elements. "
                    "Include a functional sidebar with navigation, search, and filters. "
                    "Add animations, loading states, and modern UI patterns. "
                    "Use React hooks (useState, useEffect, useNavigate) for state management and interactivity. "
                    "Include navigation buttons that link back to / (home) and to /checkout. "
                    "Use React Router Link for all navigation: import { Link } from 'react-router-dom'. "
                    "Return two code blocks: one with the React page (JSX, import './Main.css'; at the top), and one with CSS. "
                    "Import all components from '../components/ComponentName'. "
                    "CRITICAL: Apply consistent theming, use Bootstrap Icons only, no local image files, add interactivity. "
                    "Use React Router for navigation between pages. "
                    "No explanations, no markdown, no comments, no extra text."
                )
            }],
            temperature=0.3,
            max_tokens=3000
        )
        
        js_code, css_code = extract_code_and_css(response.choices[0].message.content)
        state.setdefault("pages", {})["Main"] = clean_imports(js_code)
        state.setdefault("page_css", {})["Main"] = clean_css(css_code)
        print("✅ Main page generated successfully")
        
    except Exception as e:
        print(f"❌ Error generating main page: {e}")
        # Add fallback main page
        state.setdefault("pages", {})["Main"] = get_fallback_main_page(state)
        state.setdefault("page_css", {})["Main"] = get_fallback_main_css(state)
    
    return state

def generate_checkout_page(state: AgentState) -> AgentState:
    """Generate Checkout Page using advanced Bootstrap and custom CSS"""
    components = ["Navbar", "Footer", "ContactButton", "Logo"]
    desc = state["checkout_desc"]
    primary_color = state.get("primary_color", "#0d6efd")
    secondary_color = state.get("secondary_color", "#6610f2")
    pricing = state.get("pricing", [])
    
    try:
        response = groq_client.chat.completions.create(
            model=MODEL_NAME,
            messages=[{
                "role": "user",
                "content": (
                    f"Create a professional, secure React checkout page using components {', '.join(components)}. "
                    f"Description: {desc}. Use advanced Bootstrap 5 classes, forms, cards, progress bars, and validation for a premium checkout experience. "
                    f"Theme the page using primary color {primary_color} and secondary color {secondary_color} consistently. "
                    f"Include pricing plans: {pricing}. "
                    "Add a multi-step checkout form with: plan selection, personal info, payment details, and confirmation. "
                    "Include form validation, loading states, secure payment UI, and order summary. "
                    "Add trust badges, security indicators, and professional styling. "
                    "Use React hooks (useState, useEffect, useNavigate) for form state and validation. "
                    "Include navigation buttons that link back to / (home) and /main. "
                    "Use React Router Link for navigation: import { Link } from 'react-router-dom'. "
                    "Return two code blocks: one with the React page (JSX, import './Checkout.css'; at the top), and one with CSS. "
                    "Import all components from '../components/ComponentName'. "
                    "CRITICAL: Apply consistent theming, use Bootstrap Icons only, no local image files, add form validation. "
                    "Use React Router for navigation between pages. "
                    "No explanations, no markdown, no comments, no extra text."
                )
            }],
            temperature=0.3,
            max_tokens=3000
        )
        
        js_code, css_code = extract_code_and_css(response.choices[0].message.content)
        state.setdefault("pages", {})["Checkout"] = clean_imports(js_code)
        state.setdefault("page_css", {})["Checkout"] = clean_css(css_code)
        print("✅ Checkout page generated successfully")
        
    except Exception as e:
        print(f"❌ Error generating checkout page: {e}")
        # Add fallback checkout page
        state.setdefault("pages", {})["Checkout"] = get_fallback_checkout_page(state)
        state.setdefault("page_css", {})["Checkout"] = get_fallback_checkout_css(state)
    
    return state

def get_fallback_landing_page(state: AgentState) -> str:
    """Fallback landing page if LLM generation fails"""
    primary_color = state.get("primary_color", "#4f46e5")
    secondary_color = state.get("secondary_color", "#06b6d4")
    
    return f"""import React from 'react';
import {{ Link }} from 'react-router-dom';
import Navbar from '../components/Navbar';
import Hero from '../components/Hero';
import Features from '../components/Features';
import Pricing from '../components/Pricing';
import Testimonials from '../components/Testimonials';
import FAQ from '../components/FAQ';
import Footer from '../components/Footer';
import './Landing.css';

export default function Landing() {{
  return (
    <div className="landing-page">
      <Navbar />
      <Hero />
      <Features />
      <Pricing />
      <Testimonials />
      <FAQ />
      <Footer />
    </div>
  );
}}"""

def get_fallback_landing_css(state: AgentState) -> str:
    """Fallback landing CSS if LLM generation fails"""
    primary_color = state.get("primary_color", "#4f46e5")
    secondary_color = state.get("secondary_color", "#06b6d4")
    
    return f""".landing-page {{
  min-height: 100vh;
  background: linear-gradient(135deg, {primary_color}, {secondary_color});
}}

.landing-page section {{
  padding: 4rem 0;
}}

.landing-page .hero {{
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  text-align: center;
  color: white;
}}"""

def get_fallback_main_page(state: AgentState) -> str:
    """Fallback main page if LLM generation fails"""
    return """import React from 'react';
import { Link } from 'react-router-dom';
import Navbar from '../components/Navbar';
import Sidebar from '../components/Sidebar';
import Features from '../components/Features';
import Footer from '../components/Footer';
import './Main.css';

export default function Main() {
  return (
    <div className="main-page">
      <Navbar />
      <div className="container-fluid">
        <div className="row">
          <div className="col-md-3">
            <Sidebar />
          </div>
          <div className="col-md-9">
            <Features />
          </div>
        </div>
      </div>
      <Footer />
    </div>
  );
}"""

def get_fallback_main_css(state: AgentState) -> str:
    """Fallback main CSS if LLM generation fails"""
    primary_color = state.get("primary_color", "#4f46e5")
    
    return f""".main-page {{
  min-height: 100vh;
  background-color: #f8f9fa;
}}

.main-page .sidebar {{
  background: {primary_color};
  color: white;
  min-height: calc(100vh - 76px);
}}"""

def get_fallback_checkout_page(state: AgentState) -> str:
    """Fallback checkout page if LLM generation fails"""
    return """import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import Navbar from '../components/Navbar';
import Footer from '../components/Footer';
import './Checkout.css';

export default function Checkout() {
  const [step, setStep] = useState(1);
  
  return (
    <div className="checkout-page">
      <Navbar />
      <div className="container my-5">
        <div className="row justify-content-center">
          <div className="col-md-8">
            <div className="card">
              <div className="card-body">
                <h2 className="text-center mb-4">Complete Your Order</h2>
                <div className="checkout-form">
                  <div className="mb-3">
                    <label className="form-label">Email</label>
                    <input type="email" className="form-control" />
                  </div>
                  <div className="mb-3">
                    <label className="form-label">Name</label>
                    <input type="text" className="form-control" />
                  </div>
                  <button className="btn btn-primary w-100">Complete Order</button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
      <Footer />
    </div>
  );
}"""

def get_fallback_checkout_css(state: AgentState) -> str:
    """Fallback checkout CSS if LLM generation fails"""
    primary_color = state.get("primary_color", "#4f46e5")
    
    return f""".checkout-page {{
  min-height: 100vh;
  background-color: #f8f9fa;
}}

.checkout-page .card {{
  border: none;
  box-shadow: 0 10px 25px rgba(0,0,0,0.1);
  border-radius: 1rem;
}}

.checkout-page .btn-primary {{
  background: {primary_color};
  border: none;
  padding: 0.75rem;
  border-radius: 0.5rem;
}}"""

def generate_pages(state: AgentState) -> AgentState:
    """Generate all pages"""
    print("🔄 Starting page generation...")
    
    # Generate each page
    state = generate_landing_page(state)
    state = generate_main_page(state)
    state = generate_checkout_page(state)
    
    print(f"📄 Generated {len(state.get('pages', {}))} pages total")
    return state