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

# Initialize Groq
load_dotenv()
groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))
MODEL_NAME = "meta-llama/llama-4-scout-17b-16e-instruct"

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
        # Allow extra fields in case they're provided
        extra = "ignore"

def extract_code_and_css(text: str):
    """
    Extracts JS/JSX and CSS from a string that may contain multiple code blocks.
    Returns (js_code, css_code)
    """
    code_blocks = re.findall(r"```([a-zA-Z]*)\n([\s\S]*?)```", text)
    js_code, css_code = "", ""
    for lang, block in code_blocks:
        if lang.strip() in ["js", "jsx", "javascript"]:
            js_code = block.strip()
        elif lang.strip() == "css":
            css_code = block.strip()
    if not js_code:
        js_code = extract_code(text)
    
    # Clean and validate the extracted code
    if js_code:
        js_code = clean_imports(js_code)
        # Fix common React issues
        js_code = js_code.replace(' class=', ' className=')
        js_code = js_code.replace('"class"', '"className"')
        js_code = js_code.replace("'class'", "'className'")
    
    if css_code:
        css_code = clean_css(css_code)
    
    return js_code, css_code

def extract_code(text: str) -> str:
    match = re.search(r"```(?:[a-zA-Z]+\n)?([\s\S]*?)```", text)
    if match:
        return match.group(1).strip()
    return text.strip()

def clean_imports(code: str) -> str:
    lines = code.splitlines()
    filtered = [
        line for line in lines
        if not (
            "@headlessui/react" in line or
            "@heroicons/react" in line or
            "react-bootstrap" in line or
            "react-icons" in line or
            "react-bootstrap-icons" in line or
            ("from 'react-bootstrap'" in line and "from 'react-router-dom'" not in line) or
            ("from \"react-bootstrap\"" in line and "from \"react-router-dom\"" not in line) or
            ("from 'react-icons'" in line and "from 'react-router-dom'" not in line) or
            ("from \"react-icons\"" in line and "from \"react-router-dom\"" not in line)
        )
    ]
    return "\n".join(filtered)

def clean_css(css_code: str) -> str:
    """Clean and validate CSS code comprehensively"""
    if not css_code:
        return ""
    
    # Remove any invalid syntax
    cleaned = css_code.replace('class=', 'className=')
    
    # Split into lines for processing
    lines = cleaned.split('\n')
    fixed_lines = []
    in_rule = False
    
    for i, line in enumerate(lines):
        original_line = line
        stripped_line = line.strip()
        
        # Skip empty lines
        if not stripped_line:
            fixed_lines.append("")
            continue
        
        # Remove local image references and replace with gradients
        if 'background-image' in stripped_line and any(ext in stripped_line for ext in ['.jpg', '.png', '.svg', '.jpeg', '.gif']):
            if 'url(' in stripped_line:
                # Replace with a beautiful gradient
                stripped_line = 'background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);'
        
        # Handle different line types
        if stripped_line.endswith('{'):
            # This is a CSS selector
            # Remove any semicolons from selectors
            stripped_line = re.sub(r';+\s*{', ' {', stripped_line)
            stripped_line = re.sub(r',\s*;\s*', ', ', stripped_line)
            stripped_line = re.sub(r';\s*$', '', stripped_line.rstrip('{')) + ' {'
            fixed_lines.append(stripped_line)
            in_rule = True
            
        elif stripped_line == '}':
            # End of CSS rule
            fixed_lines.append(stripped_line)
            in_rule = False
            
        elif in_rule and ':' in stripped_line and not stripped_line.startswith('@'):
            # This is a CSS property inside a rule
            # Ensure it ends with semicolon
            if not stripped_line.endswith(';'):
                stripped_line += ';'
            
            # Fix common issues
            stripped_line = re.sub(r';+', ';', stripped_line)  # Remove multiple semicolons
            stripped_line = re.sub(r',\s*;', ';', stripped_line)  # Fix comma-semicolon
            
            # Add proper indentation
            if not stripped_line.startswith('  '):
                stripped_line = '  ' + stripped_line
            
            fixed_lines.append(stripped_line)
            
        elif stripped_line.startswith('@'):
            # CSS at-rules (@media, @keyframes, etc.)
            # Remove semicolons from at-rule declarations
            if '{' in stripped_line:
                stripped_line = re.sub(r';+\s*{', ' {', stripped_line)
            fixed_lines.append(stripped_line)
            
        else:
            # Other lines (comments, etc.)
            # If this looks like a CSS property but isn't in a rule, it might be misformatted
            if ':' in stripped_line and not stripped_line.startswith('/*') and not stripped_line.endswith('*/'):
                if not stripped_line.endswith(';'):
                    stripped_line += ';'
                if not stripped_line.startswith('  '):
                    stripped_line = '  ' + stripped_line
            fixed_lines.append(stripped_line)
    
    # Join lines and do final cleanup
    result = '\n'.join(fixed_lines)
    
    # Final validation pass - add semicolons to any CSS properties that are missing them
    # This regex finds CSS properties (property: value) that don't end with semicolon
    result = re.sub(r':\s*([^;{}]+[^;{}\s])\s*$', r': \1;', result, flags=re.MULTILINE)
    
    # Fix any remaining issues
    result = re.sub(r';\s*{', ' {', result)  # Remove semicolons before braces
    result = re.sub(r',\s*;', ';', result)  # Fix comma-semicolon combinations
    result = re.sub(r';+', ';', result)  # Remove multiple semicolons
    
    return result

def generate_components(state: AgentState) -> AgentState:
    """Generate shared React components using advanced Bootstrap and custom CSS"""
    
    # Define default navigation links if none provided
    default_nav_links = [
        {"name": "Home", "url": "/"},
        {"name": "Features", "url": "/main"},
        {"name": "Pricing", "url": "/#pricing"},
        {"name": "About", "url": "/#about"},
        {"name": "Checkout", "url": "/checkout"}
    ]
    
    nav_links = state.get('nav_links', default_nav_links)
    
    component_specs = {
        "Logo": (
            "A professional, animated logo component that can be used in navbar and other places. "
            "If a logo URL is provided, display it as an image with proper sizing and hover effects. "
            "If no logo URL is provided, create a beautiful text-based logo with gradients and animations. "
            "Use Bootstrap classes for responsive sizing and add custom CSS for animations and effects. "
            "Make it clickable with React Router Link to navigate to home page (/). "
            "Import { Link } from 'react-router-dom' and wrap logo in Link component. "
            "Add hover animations and responsive sizing. "
            "CRITICAL: Do NOT reference local image files. Use only the provided logo URL or create text-based logo. "
            f"Logo URL: {state.get('logo_url', '')}. "
            f"Website name can be derived from: {state.get('website_desc', 'Generated Website')}."
        ),
        "Navbar": (
            "A fully responsive, sticky, animated navigation bar with a multi-color gradient background, glassmorphism effect, and navigation links. "
            "Use the Logo component for branding. Import Logo from './Logo' and use <Logo /> component. "
            "Use advanced Bootstrap 5 classes, gradients, shadows, and color utilities for a modern, vibrant look. "
            "Include a mobile menu toggle, smooth hover and active animations. "
            "Add custom CSS for glassmorphism, transitions, drop shadows, and a professional, premium feel. "
            "Use Bootstrap Icons via CDN with <i className='bi bi-icon-name'></i> syntax. "
            "Make ALL navigation links functional with React Router Link components: import { Link } from 'react-router-dom'. "
            "Use Link component for all navigation items instead of <a> tags. "
            "Add active state styling to show current page. "
            "CRITICAL: Do NOT import any external packages except react-router-dom for Link. "
            "Use only standard HTML elements with Bootstrap classes and Bootstrap Icons via CDN. "
            "Use 'className' instead of 'class' for all HTML attributes. "
            "Do NOT reference local image files - the Logo component handles logo display. "
            f"Use the provided primary color {state.get('primary_color', '#0d6efd')} and secondary color {state.get('secondary_color', '#6610f2')} for theming. "
            f"Navigation links: {nav_links}. Make sure to use Link for each navigation item."
        ),
        "Footer": (
            "A visually rich, elegant footer with a multi-color gradient background, copyright, "
            "social media icons, useful links, a newsletter signup form, and company info. "
            "Use the Logo component for branding. Import Logo from './Logo' and use <Logo /> component. "
            "Use advanced Bootstrap 5 classes, layout utilities, and color utilities. "
            "Use Bootstrap Icons via CDN with <i className='bi bi-icon-name'></i> syntax. "
            "Add functional links using React Router Link: import { Link } from 'react-router-dom'. "
            "Use Link component for internal navigation instead of <a> tags. "
            "CRITICAL: Do NOT import any external packages except react-router-dom for Link. "
            "Do NOT reference local image files - use only CSS gradients and colors. "
            "Add custom CSS for gradients, hover effects, and responsive design. "
            f"Use the provided primary color {state.get('primary_color', '#0d6efd')} and secondary color {state.get('secondary_color', '#6610f2')} for theming. "
            f"Include links to: {nav_links}."
        ),
        "ContactButton": (
            "A floating, animated contact button with a glowing effect, using Bootstrap 5 classes. "
            "Make it colorful, prominent, and show a tooltip on hover. "
            "Use Bootstrap Icons via CDN with <i className='bi bi-icon-name'></i> syntax. "
            "Add onClick functionality to navigate to contact section or checkout page using React Router. "
            "Import { useNavigate } from 'react-router-dom' and use navigate('/checkout') on click. "
            "CRITICAL: Do NOT import react-icons or any external packages except react-router-dom. "
            "Do NOT reference local image files - use only CSS gradients and colors. "
            "Add a bounce or pulse animation with custom CSS for extra attention. "
            f"Use the provided primary color {state.get('primary_color', '#0d6efd')}."
        ),
        "Hero": (
            "A visually stunning hero section with a gradient background, bold headline, subheadline, animated call-to-action buttons, and interactive elements. "
            "Use the Logo component if needed. Import Logo from './Logo' if displaying logo. "
            "Use advanced Bootstrap 5 classes, gradients, and custom CSS for animation and responsiveness. "
            "Use Bootstrap Icons via CDN with <i className='bi bi-icon-name'></i> syntax. "
            "Add CTA buttons that navigate to different pages using React Router Link: import { Link } from 'react-router-dom'. "
            "Include buttons for 'Get Started' (link to /main), 'Learn More' (link to /#features), 'Try Free' (link to /checkout). "
            "Add scroll animations, typing effects, particle backgrounds (CSS only), and interactive hover effects. "
            "CRITICAL: Do NOT import react-icons or any external packages except react-router-dom for Link. "
            "CRITICAL: Do NOT reference local image files like 'background-image.jpg'. Use only CSS gradients and shapes. "
            "Add micro-interactions, floating elements, and advanced CSS animations. "
            f"Use the provided primary color {state.get('primary_color', '#0d6efd')} and secondary color {state.get('secondary_color', '#6610f2')}."
        ),
        "Features": (
            "A comprehensive features section with at least 6 feature cards, each with an icon, title, description, and interactive hover effects. "
            "Use Bootstrap 5 grid, cards, and color utilities. "
            "Use Bootstrap Icons via CDN with <i className='bi bi-icon-name'></i> syntax for all icons. "
            "Add staggered animations, hover effects with scale transforms, and colorful gradients. "
            "Include 'Learn More' buttons that navigate to /main using React Router Link: import { Link } from 'react-router-dom'. "
            "Add progress bars, counters, and interactive elements. "
            "CRITICAL: Do NOT import react-icons or any external packages except react-router-dom for Link. "
            "Do NOT reference local image files - use only CSS styling and Bootstrap icons. "
            "Add custom CSS for hover effects, animated icons, card lift effects, and entrance animations. "
            f"Features: {state.get('features', [])}. If empty, create 6 compelling features related to: {state.get('website_desc', 'modern platform')}."
        ),
        "Pricing": (
            "A comprehensive pricing section with at least 3 pricing cards, each with a plan name, price, features list, and call-to-action button. "
            "Use Bootstrap 5 cards, badges, and color utilities. "
            "Use Bootstrap Icons via CDN with <i className='bi bi-icon-name'></i> syntax. "
            "Add CTA buttons that navigate to checkout page using React Router Link: import { Link } from 'react-router-dom'. "
            "Use Link to='/checkout' for all 'Get Started', 'Choose Plan', 'Subscribe' buttons. "
            "Add hover effects, recommended plan highlighting, animated price counters, and toggle for monthly/yearly pricing. "
            "Include testimonials snippets, money-back guarantee badges, and feature comparison tooltips. "
            "CRITICAL: Do NOT import any external packages except react-router-dom for Link. "
            "Do NOT reference local image files - use only CSS gradients and colors. "
            "Add custom CSS for highlighting the recommended plan, hover effects, and animated buttons. "
            f"Pricing plans: {state.get('pricing', [])}. If empty, create 3 compelling pricing tiers."
        ),
        "Testimonials": (
            "A dynamic testimonials section with at least 4 customer quotes, avatars, names, and companies. "
            "Use Bootstrap 5 cards, carousel, and grid utilities. "
            "Use Bootstrap Icons via CDN with <i className='bi bi-icon-name'></i> syntax for quote icons and star ratings. "
            "Add auto-rotating carousel, hover effects, star ratings, and company logos. "
            "Include social proof elements like customer count, satisfaction ratings, and review sources. "
            "CRITICAL: Do NOT import any external packages. Use only standard HTML elements. "
            "For avatar images, use placeholder URLs like: https://via.placeholder.com/80x80/4f46e5/ffffff?text=INITIALS "
            "Add custom CSS for quote styling, fade-in animation, carousel transitions, and interactive elements. "
            f"Testimonials: {state.get('testimonials', [])}. If empty, create 4 realistic testimonials."
        ),
        "FAQ": (
            "A comprehensive FAQ section with at least 6 questions and answers, using Bootstrap 5 accordion. "
            "Use Bootstrap Icons via CDN with <i className='bi bi-icon-name'></i> syntax. "
            "Add search functionality, category filters, and smooth accordion animations. "
            "Include helpful icons, related links using React Router Link, and 'Was this helpful?' voting. "
            "Add 'Contact Support' button that navigates to /checkout using Link: import { Link } from 'react-router-dom'. "
            "CRITICAL: Do NOT import any external packages except react-router-dom for Link. "
            "Do NOT reference local image files - use only CSS styling. "
            "Add custom CSS for smooth transitions, icons, modern design, and interactive elements. "
            f"FAQs: {state.get('faqs', [])}. If empty, create 6 comprehensive FAQs about the platform."
        ),
        "Newsletter": (
            "A compelling newsletter signup section with a gradient background, input field, subscribe button, and social proof. "
            "Use Bootstrap 5 forms, modals, and color utilities. "
            "Use Bootstrap Icons via CDN with <i className='bi bi-icon-name'></i> syntax. "
            "Add success animations, subscriber count, privacy assurance, and sample newsletter preview. "
            "Include social media links and email preview modal. "
            "CRITICAL: Do NOT import react-bootstrap/Modal or any external packages. Use standard HTML and Bootstrap modal. "
            "Do NOT reference local image files - use only CSS gradients and colors. "
            "Add custom CSS for focus and hover effects, success animations, and modal styling."
        ),
        "Sidebar": (
            "A modern, collapsible sidebar with navigation links, user info, and quick actions using Bootstrap 5 offcanvas. "
            "Use Bootstrap Icons via CDN with <i className='bi bi-icon-name'></i> syntax. "
            "Add navigation links using React Router Link: import { Link } from 'react-router-dom'. "
            "Use Link component for all navigation items instead of <a> tags. "
            "Add user avatar, navigation hierarchy, search functionality, and theme toggle. "
            "Include progress indicators, notifications, and contextual help. "
            "CRITICAL: Do NOT import react-bootstrap or any external packages except react-router-dom for Link. "
            "Do NOT reference local image files - use only CSS styling and placeholder images. "
            "Add custom CSS for transitions, glassmorphism, smooth animations, and modern design. "
            f"Navigation links: {nav_links}. Use Link for each navigation item."
        )
    }
    
    state["components"] = {}
    state["component_css"] = {}
    
    for name, desc in component_specs.items():
        response = groq_client.chat.completions.create(
            model=MODEL_NAME,
            messages=[{
                "role": "user",
                "content": (
                    f"Create a professional, interactive React component named {name}. {desc}\n"
                    f"Use only Bootstrap 5 classes for all styling, but also add advanced custom CSS for gradients, animations, interactivity, and modern design. "
                    f"Return two code blocks: one with the React component (JSX, no inline styles, import './{name}.css'; at the top), "
                    f"and one with the CSS for this component (in a ```css code block). "
                    "ABSOLUTE REQUIREMENTS:\n"
                    "- Use 'className' instead of 'class' for ALL HTML attributes\n"
                    "- Do NOT import react-bootstrap, react-icons, react-bootstrap-icons, or ANY external packages (except react-router-dom for Link)\n"
                    "- Use React Router Link for ALL internal navigation instead of <a> tags\n"
                    "- Import {{ Link }} from 'react-router-dom' when needed for navigation\n"
                    "- Use only standard HTML elements (div, button, nav, etc.) with Bootstrap classes\n"
                    "- Use Bootstrap Icons via CDN with <i className='bi bi-icon-name'></i> syntax\n"
                    "- Do NOT reference local image files (no .jpg, .png, .svg files)\n"
                    "- Use only CSS gradients, online placeholder images, or pure CSS graphics\n"
                    "- For placeholder images use: https://via.placeholder.com/WIDTHxHEIGHT/COLOR/TEXTCOLOR?text=TEXT\n"
                    "- CRITICAL CSS REQUIREMENTS:\n"
                    "  * All CSS selectors must end with space then {{ not semicolon\n"
                    "  * All CSS properties must end with semicolon\n"
                    "  * No comma-semicolon combinations like ',;'\n"
                    "  * Use proper CSS syntax: selector {{ property: value; }}\n"
                    "  * No semicolons in selectors (e.g., '.class:hover;' is wrong, '.class:hover' is correct)\n"
                    "- Add smooth animations, hover effects, and interactive elements\n"
                    "- Ensure all CSS syntax is valid and error-free\n"
                    "- Use React hooks (useState, useEffect, useNavigate) for interactivity when needed\n"
                    "- Make components responsive and accessible\n"
                    "- No explanations, no markdown, no comments, no extra text."
                )
            }]
        )
        js_code, css_code = extract_code_and_css(response.choices[0].message.content)
        state["components"][name] = clean_imports(js_code)
        state["component_css"][name] = clean_css(css_code)
    return state

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
        }]
    )
    js_code, css_code = extract_code_and_css(response.choices[0].message.content)
    state.setdefault("pages", {})["Landing"] = clean_imports(js_code)
    state.setdefault("page_css", {})["Landing"] = clean_css(css_code)
    return state

def generate_main_page(state: AgentState) -> AgentState:
    """Generate Main Page using advanced Bootstrap and custom CSS"""
    components = ["Navbar", "Sidebar", "Features", "Pricing", "Footer", "ContactButton", "Logo"]
    desc = state["main_desc"]
    primary_color = state.get("primary_color", "#0d6efd")
    secondary_color = state.get("secondary_color", "#6610f2")
    
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
        }]
    )
    js_code, css_code = extract_code_and_css(response.choices[0].message.content)
    state.setdefault("pages", {})["Main"] = clean_imports(js_code)
    state.setdefault("page_css", {})["Main"] = clean_css(css_code)
    return state

def generate_checkout_page(state: AgentState) -> AgentState:
    """Generate Checkout Page using advanced Bootstrap and custom CSS"""
    components = ["Navbar", "Footer", "ContactButton", "Logo"]
    desc = state["checkout_desc"]
    primary_color = state.get("primary_color", "#0d6efd")
    secondary_color = state.get("secondary_color", "#6610f2")
    
    response = groq_client.chat.completions.create(
        model=MODEL_NAME,
        messages=[{
            "role": "user",
            "content": (
                f"Create a professional, secure-looking React checkout page using components {', '.join(components)}. "
                f"Description: {desc}. Use advanced Bootstrap 5 classes, forms, cards, and validation styling. "
                f"Theme the page using primary color {primary_color} and secondary color {secondary_color}. "
                "Include a comprehensive checkout form with validation, order summary, payment options, and security badges. "
                "Add form validation, progress indicators, price calculations, and trust signals. "
                "Use React hooks (useState, useEffect, useNavigate) for form handling, validation, and interactive elements. "
                "Include multiple payment methods, discount codes, and order confirmation flow. "
                "Add navigation buttons that link back to / (home) and /main using React Router Link. "
                "Import { Link } from 'react-router-dom' for navigation. "
                "Return two code blocks: one with the React page (JSX, import './Checkout.css'; at the top), and one with CSS. "
                "Import all components from '../components/ComponentName'. "
                "CRITICAL: Add form validation, security styling, consistent theming, Bootstrap Icons only. "
                "Use React Router for navigation between pages. "
                "No explanations, no markdown, no comments, no extra text."
            )
        }]
    )
    js_code, css_code = extract_code_and_css(response.choices[0].message.content)
    state.setdefault("pages", {})["Checkout"] = clean_imports(js_code)
    state.setdefault("page_css", {})["Checkout"] = clean_css(css_code)
    return state

def compile_project(state: AgentState) -> AgentState:
    """Create complete React project structure with Bootstrap and per-file CSS"""
    state["react_project"] = {
        "src": {
            "components": {
                **{f"{name}.jsx": code for name, code in state["components"].items()},
                **{f"{name}.css": css for name, css in state.get("component_css", {}).items()}
            },
            "pages": {
                **{f"{name}.jsx": code for name, code in state["pages"].items()},
                **{f"{name}.css": css for name, css in state.get("page_css", {}).items()}
            },
            "App.jsx": """import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Landing from './pages/Landing';
import Main from './pages/Main';
import Checkout from './pages/Checkout';

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Landing />} />
        <Route path="/main" element={<Main />} />
        <Route path="/checkout" element={<Checkout />} />
      </Routes>
    </BrowserRouter>
  );
}""",
            "index.js": """import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';
import './index.css';

const root = ReactDOM.createRoot(document.getElementById('root'));
root.render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);""",
            "index.css": """body {
  margin: 0;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen',
    'Ubuntu', 'Cantarell', 'Fira Sans', 'Droid Sans', 'Helvetica Neue',
    sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

code {
  font-family: source-code-pro, Menlo, Monaco, Consolas, 'Courier New',
    monospace;
}"""
        },
        "public": {
            "index.html": """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <link rel="icon" href="%PUBLIC_URL%/favicon.ico" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <meta name="theme-color" content="#000000" />
  <meta name="description" content="Professional React website generated automatically" />
  <link rel="apple-touch-icon" href="%PUBLIC_URL%/logo192.png" />
  <link rel="manifest" href="%PUBLIC_URL%/manifest.json" />
  <title>Generated React App</title>
  <!-- Bootstrap 5 CDN -->
  <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet" integrity="sha384-T3c6CoIi6uLrA9TneNEoa7RxnatzjcDSCmG1MXxSR1GAsXEV/Dwwykc2MPK8M2HN" crossorigin="anonymous">
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/font/bootstrap-icons.min.css">
</head>
<body>
  <noscript>You need to enable JavaScript to run this app.</noscript>
  <div id="root"></div>
  <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/js/bootstrap.bundle.min.js" integrity="sha384-C6RzsynM9kWDrMNeT87bh95OGNyZPhcTNXj1NW7RuBCsyN/o0jlpcV8Qyq46cDfL" crossorigin="anonymous"></script>
</body>
</html>""",
            "favicon.ico": "",
            "logo192.png": "",
            "logo512.png": "",
            "robots.txt": """# https://www.robotstxt.org/robotstxt.html
User-agent: *
Disallow:
""",
            "manifest.json": json.dumps({
                "short_name": "React App",
                "name": "Generated React Website",
                "icons": [
                    {
                        "src": "favicon.ico",
                        "sizes": "64x64 32x32 24x24 16x16",
                        "type": "image/x-icon"
                    },
                    {
                        "src": "logo192.png",
                        "type": "image/png",
                        "sizes": "192x192"
                    },
                    {
                        "src": "logo512.png",
                        "type": "image/png",
                        "sizes": "512x512"
                    }
                ],
                "start_url": ".",
                "display": "standalone",
                "theme_color": "#000000",
                "background_color": "#ffffff"
            }, indent=2)
        },
        "package.json": json.dumps({
            "name": "generated-react-website",
            "version": "0.1.0",
            "private": True,
            "dependencies": {
                "@testing-library/jest-dom": "6.4.2",
                "@testing-library/react": "14.2.1",
                "@testing-library/user-event": "14.5.2",
                "react": "18.3.1",
                "react-dom": "18.3.1",
                "react-router-dom": "6.26.1",
                "react-scripts": "5.0.1",
                "web-vitals": "4.2.3",
                "bootstrap": "^5.3.2"
            },
            "scripts": {
                "start": "react-scripts start",
                "build": "react-scripts build",
                "test": "react-scripts test",
                "eject": "react-scripts eject"
            },
            "eslintConfig": {
                "extends": [
                    "react-app",
                    "react-app/jest"
                ]
            },
            "browserslist": {
                "production": [
                    "Chrome >= 90",
                    "Firefox >= 88", 
                    "Safari >= 14",
                    "Edge >= 90",
                    ">0.2%",
                    "not dead",
                    "not op_mini all"
                ],
                "development": [
                    "last 1 chrome version",
                    "last 1 firefox version",
                    "last 1 safari version",
                    "last 1 edge version"
                ]
            }
        }, indent=2),
        ".gitignore": """# See https://help.github.com/articles/ignoring-files/ for more about ignoring files.

# dependencies
/node_modules
/.pnp
.pnp.js

# testing
/coverage

# production
/build

# misc
.DS_Store
.env.local
.env.development.local
.env.test.local
.env.production.local

npm-debug.log*
yarn-debug.log*
yarn-error.log*
""",
        ".env.example": """# Environment variables for the React app
# Rename this file to .env.local and fill in your values

REACT_APP_API_URL=http://localhost:3001
REACT_APP_SITE_NAME=Generated React Website
""",
        "README.md": """# Generated React Website

This project was generated automatically and includes:

- ⚛️ **React 18** with functional components and hooks
- 🎨 **Bootstrap 5** for responsive design and components
- 🧭 **React Router** for client-side routing
- 🎭 **Bootstrap Icons** for beautiful iconography
- 📱 **Fully responsive** design for all devices
- 🚀 **Production-ready** build configuration
- 🧪 **Testing setup** with Jest and React Testing Library

## Browser Support

This project supports the following browsers:

### Production
- **Chrome** >= 90
- **Firefox** >= 88
- **Safari** >= 14
- **Edge** >= 90
- All browsers with >0.2% market share

### Development
- Latest Chrome, Firefox, Safari, and Edge versions

## Quick Start

1. **Extract the ZIP file**
2. **Navigate to the project directory**
   ```bash
   cd generated-react-website
   ```
3. **Install dependencies**
   ```bash
   npm install
   ```
4. **Start the development server**
   ```bash
   npm start
   ```
5. **Open [http://localhost:3000](http://localhost:3000)** to view in browser

## Available Scripts

### `npm start`
Runs the app in development mode with hot reloading.

### `npm run build`
Builds the app for production to the `build` folder.
Optimizes the build for best performance.

### `npm test`
Launches the test runner in interactive watch mode.

### `npm run eject`
**Note: this is a one-way operation. Once you eject, you can't go back!**

## Project Structure

```
src/
├── components/          # Reusable React components
│   ├── Navbar.jsx
│   ├── Footer.jsx
│   └── ...
├── pages/              # Page components
│   ├── Landing.jsx
│   ├── Main.jsx
│   └── Checkout.jsx
├── App.jsx             # Main app component
└── index.js            # Entry point
```

## Features Included

- 🏠 **Landing Page** with hero, features, pricing, testimonials, and FAQ
- 📋 **Main Page** with product showcase and features
- 🛒 **Checkout Page** with form and payment integration ready
- 🧭 **Navigation** with responsive mobile menu
- 📞 **Contact Button** with floating design
- 📧 **Newsletter** signup component
- ❓ **FAQ** accordion section
- 💰 **Pricing** cards with feature comparison

## Customization

All components use Bootstrap 5 classes and custom CSS for easy customization:

- Edit `src/components/*.css` for component-specific styles
- Edit `src/pages/*.css` for page-specific styles
- Modify Bootstrap variables in CSS files for theme customization

## Deployment

After running `npm run build`, the `build` folder contains optimized files ready for deployment to:

- **Vercel**: `vercel --prod`
- **Netlify**: Drag and drop the `build` folder
- **GitHub Pages**: Upload `build` folder contents
- **Any static hosting service**

## Learn More

- [React Documentation](https://reactjs.org/)
- [Bootstrap 5 Documentation](https://getbootstrap.com/)
- [React Router Documentation](https://reactrouter.com/)

---

**Generated automatically with love** ❤️
"""
    }
    return state

def create_zip(state: AgentState) -> AgentState:
    """Generate ZIP file with project"""
    zip_path = "react_website.zip"
    with zipfile.ZipFile(zip_path, 'w') as zipf:
        def add_folder(folder_path, files):
            if isinstance(files, dict):
                for name, content in files.items():
                    add_folder(f"{folder_path}/{name}", content)
            else:
                zipf.writestr(folder_path.lstrip('/'), files)
        for name, content in state["react_project"].items():
            if isinstance(content, dict):
                add_folder(name, content)
            else:
                zipf.writestr(name, content)
    state["zip_path"] = zip_path
    return state

def build_workflow() -> Graph:
    workflow = Graph()
    workflow.add_node("components", generate_components)
    workflow.add_node("landing", generate_landing_page)
    workflow.add_node("main", generate_main_page)
    workflow.add_node("checkout", generate_checkout_page)
    workflow.add_node("compile", compile_project)
    workflow.add_node("zip", create_zip)
    
    workflow.set_entry_point("components")
    workflow.add_edge("components", "landing")
    workflow.add_edge("landing", "main")
    workflow.add_edge("main", "checkout")
    workflow.add_edge("checkout", "compile")
    workflow.add_edge("compile", "zip")
    workflow.set_finish_point("zip")
    
    return workflow.compile()

# Update the generate_website function to accept all parameters
def generate_website(
    website_desc: str,
    landing_desc: str,
    main_desc: str,
    checkout_desc: str,
    primary_color: str = "#0d6efd",
    secondary_color: str = "#6610f2", 
    logo_url: str = "",
    nav_links: list = None,
    features: list = None,
    pricing: list = None,
    testimonials: list = None,
    faqs: list = None
) -> str:
    workflow = build_workflow()
    initial_state: AgentState = {
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
        "faqs": faqs or [],
        "components": {},
        "component_css": {},
        "pages": {},
        "page_css": {},
        "react_project": {},
        "zip_path": None
    }
    final_state = workflow.invoke(initial_state)
    return final_state["zip_path"]

def llm_fill_field(field_name: str, field_description: str, context: dict) -> any:
    """Use LLM to generate a default value for a missing field."""
    
    # Define specific prompts for each field type
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
            max_tokens=1000
        )
        
        content = response.choices[0].message.content.strip()
        
        # Try to parse JSON for array fields
        if field_name in ["nav_links", "features", "pricing", "testimonials", "faqs"]:
            try:
                return json.loads(content)
            except json.JSONDecodeError:
                # Extract JSON from content if wrapped in markdown
                import re
                json_match = re.search(r'\[.*\]', content, re.DOTALL)
                if json_match:
                    return json.loads(json_match.group())
                
                # Return default values if JSON parsing fails
                defaults = {
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
                return defaults.get(field_name, [])
        
        return content
        
    except Exception as e:
        print(f"Error generating field {field_name}: {e}")
        
        # Return sensible defaults
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
            "features": [],
            "pricing": [],
            "testimonials": [],
            "faqs": []
        }
        
        return defaults.get(field_name, "")