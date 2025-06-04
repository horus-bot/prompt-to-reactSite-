import os
import zipfile
import json
import re
from pathlib import Path
from typing import TypedDict
from langgraph.graph import Graph
from groq import Groq
from dotenv import load_dotenv

# Initialize Groq
load_dotenv()
groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))
MODEL_NAME = "meta-llama/llama-4-scout-17b-16e-instruct"

class AgentState(TypedDict):
    website_desc: str
    landing_desc: str
    main_desc: str
    checkout_desc: str
    components: dict[str, str]
    component_css: dict[str, str]
    pages: dict[str, str]
    page_css: dict[str, str]
    react_project: dict[str, dict[str, str]]
    zip_path: str | None

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
            "@heroicons/react" in line
        )
    ]
    return "\n".join(filtered)

def generate_components(state: AgentState) -> AgentState:
    """Generate shared React components using advanced Bootstrap and custom CSS"""
    component_specs = {
        "Navbar": (
            "A responsive, sticky, animated navigation bar with a colorful gradient background, logo, and at least 4 navigation links. "
            "Use advanced Bootstrap 5 classes, gradients, shadows, and color utilities for a modern, vibrant look. "
            "Include a mobile menu toggle, smooth hover animations, and a brand/logo on the left. "
            "Add custom CSS for subtle transitions, drop shadows, and a professional feel."
        ),
        "Footer": (
            "A visually rich, elegant footer with a multi-color gradient background, copyright, "
            "social media icons (use Bootstrap Icons via CDN), at least 4 useful links, and a newsletter signup form. "
            "Use advanced Bootstrap 5 classes, layout utilities, and color utilities. "
            "Add custom CSS for gradients, hover effects, and responsive design. Make it look like a premium SaaS website."
        ),
        "ContactButton": (
            "A floating, animated contact button with a glowing effect, using Bootstrap 5 classes. "
            "Make it colorful, prominent, and show a tooltip or popover on hover. "
            "Add a bounce or pulse animation with custom CSS for extra attention."
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
                    f"Create a professional React component named {name}. {desc}\n"
                    f"Use only Bootstrap 5 classes for all styling, but also add advanced custom CSS for gradients, animation, color, and elegance. "
                    f"Return two code blocks: one with the React component (JSX, no inline styles, import './{name}.css'; at the top), "
                    f"and one with the CSS for this component (in a ```css code block). "
                    "Do NOT import any CSS files or external libraries. "
                    "Do NOT use Tailwind CSS. "
                    "No explanations, no markdown, no comments, no extra text."
                )
            }]
        )
        js_code, css_code = extract_code_and_css(response.choices[0].message.content)
        state["components"][name] = clean_imports(js_code)
        state["component_css"][name] = css_code
    return state

def generate_landing_page(state: AgentState) -> AgentState:
    """Generate Landing Page using advanced Bootstrap and custom CSS"""
    components = ["Navbar", "Footer", "ContactButton"]
    desc = state["landing_desc"]
    response = groq_client.chat.completions.create(
        model=MODEL_NAME,
        messages=[{
            "role": "user",
            "content": (
                f"Create a professional, visually stunning, and colorful React landing page using components {', '.join(components)}. "
                f"Description: {desc}. Use advanced Bootstrap 5 classes, gradients, cards, shadows, and color utilities for a premium SaaS hero section, call-to-action, and feature highlights. "
                "Add a hero section with a gradient background, a bold headline, a call-to-action button, and at least 3 feature cards with icons. "
                "Return two code blocks: one with the React page (JSX, no inline styles, import './Landing.css'; at the top), "
                "and one with the CSS for this page (in a ```css code block). "
                "Import all components from '../components/ComponentName', for example: import Navbar from '../components/Navbar'. "
                "Render all imported components in the page JSX. "
                "Do NOT import any CSS files or external libraries. "
                "Do NOT use Tailwind CSS. "
                "No explanations, no markdown, no comments, no extra text."
            )
        }]
    )
    js_code, css_code = extract_code_and_css(response.choices[0].message.content)
    state.setdefault("pages", {})["Landing"] = clean_imports(js_code)
    state.setdefault("page_css", {})["Landing"] = css_code
    return state

def generate_main_page(state: AgentState) -> AgentState:
    """Generate Main Page using advanced Bootstrap and custom CSS"""
    components = ["Navbar", "ContactButton"]
    desc = state["main_desc"]
    response = groq_client.chat.completions.create(
        model=MODEL_NAME,
        messages=[{
            "role": "user",
            "content": (
                f"Create a professional, elegant, and colorful React main page using components {', '.join(components)}. "
                f"Description: {desc}. Use advanced Bootstrap 5 classes, cards, badges, gradients, and color utilities for a beautiful product grid and layout. "
                "Add at least 4 product or feature cards with images, titles, badges, and descriptions. "
                "Return two code blocks: one with the React page (JSX, no inline styles, import './Main.css'; at the top), "
                "and one with the CSS for this page (in a ```css code block). "
                "Import all components from '../components/ComponentName', for example: import Navbar from '../components/Navbar'. "
                "Render all imported components in the page JSX. "
                "Do NOT import any CSS files or external libraries. "
                "Do NOT use Tailwind CSS. "
                "No explanations, no markdown, no comments, no extra text."
            )
        }]
    )
    js_code, css_code = extract_code_and_css(response.choices[0].message.content)
    state.setdefault("pages", {})["Main"] = clean_imports(js_code)
    state.setdefault("page_css", {})["Main"] = css_code
    return state

def generate_checkout_page(state: AgentState) -> AgentState:
    """Generate Checkout Page using advanced Bootstrap and custom CSS"""
    components = ["Navbar", "Footer"]
    desc = state["checkout_desc"]
    response = groq_client.chat.completions.create(
        model=MODEL_NAME,
        messages=[{
            "role": "user",
            "content": (
                f"Create a professional, elegant, and colorful React checkout page using components {', '.join(components)}. "
                f"Description: {desc}. Use advanced Bootstrap 5 classes, cards, gradients, and color utilities for a stylish checkout form and summary. "
                "Add a checkout form with at least 4 fields, a summary card, and a visually rich layout. "
                "Return two code blocks: one with the React page (JSX, no inline styles, import './Checkout.css'; at the top), "
                "and one with the CSS for this page (in a ```css code block). "
                "Import all components from '../components/ComponentName', for example: import Navbar from '../components/Navbar'. "
                "Render all imported components in the page JSX. "
                "Do NOT import any CSS files or external libraries. "
                "Do NOT use Tailwind CSS. "
                "No explanations, no markdown, no comments, no extra text."
            )
        }]
    )
    js_code, css_code = extract_code_and_css(response.choices[0].message.content)
    state.setdefault("pages", {})["Checkout"] = clean_imports(js_code)
    state.setdefault("page_css", {})["Checkout"] = css_code
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
            "index.css": "body { margin: 0; font-family: sans-serif; }"
        },
        "public": {
            "index.html": """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <title>Generated React App</title>
  <!-- Bootstrap 5 CDN -->
  <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/font/bootstrap-icons.min.css">
</head>
<body>
  <div id="root"></div>
  <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>"""
        },
        "package.json": json.dumps({
            "name": "generated-website",
            "version": "1.0.0",
            "private": True,
            "dependencies": {
                "react": "^18.2.0",
                "react-dom": "^18.2.0", 
                "react-router-dom": "^6.22.0",
                "react-scripts": "5.0.1"
            },
            "scripts": {
                "start": "react-scripts start",
                "build": "react-scripts build"
            }
        }, indent=2)
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

def generate_website(
    website_desc: str,
    landing_desc: str,
    main_desc: str,
    checkout_desc: str
) -> str:
    workflow = build_workflow()
    initial_state: AgentState = {
        "website_desc": website_desc,
        "landing_desc": landing_desc,
        "main_desc": main_desc,
        "checkout_desc": checkout_desc,
        "components": {},
        "component_css": {},
        "pages": {},
        "page_css": {},
        "react_project": {},
        "zip_path": None
    }
    final_state = workflow.invoke(initial_state)
    return final_state["zip_path"]