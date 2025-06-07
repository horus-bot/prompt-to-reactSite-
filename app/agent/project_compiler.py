import json
import zipfile
import os
from pathlib import Path
from .models import AgentState

def compile_project(state: AgentState) -> AgentState:
    """Create complete React project structure with Bootstrap and per-file CSS"""
    
    # Debug: Print what components were generated
    print(f"🔍 Compiling project with {len(state.get('components', {}))} components:")
    for name in state.get('components', {}):
        print(f"   - {name}")
    
    # Get theme colors for global CSS
    primary_color = state.get("primary_color", "#4f46e5")
    secondary_color = state.get("secondary_color", "#06b6d4")
    
    state["react_project"] = {
        "src": {
            "components": {
                # Add ALL generated components (both .jsx and .css files)
                **{f"{name}.jsx": code for name, code in state.get("components", {}).items()},
                **{f"{name}.css": css for name, css in state.get("component_css", {}).items()}
            },
            "pages": {
                # Add ALL generated pages (both .jsx and .css files)
                **{f"{name}.jsx": code for name, code in state.get("pages", {}).items()},
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
            "index.css": f"""/* Global styles with theme colors */
body {{
  margin: 0;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', 'Oxygen',
    'Ubuntu', 'Cantarell', 'Fira Sans', 'Droid Sans', 'Helvetica Neue',
    sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  scroll-behavior: smooth;
  background-color: #ffffff;
}}

code {{
  font-family: source-code-pro, Menlo, Monaco, Consolas, 'Courier New',
    monospace;
}}

/* Global CSS Variables with theme colors */
:root {{
  /* Theme Colors */
  --primary-color: {primary_color};
  --secondary-color: {secondary_color};
  --primary-hover: {adjust_color_brightness(primary_color, -20)};
  --secondary-hover: {adjust_color_brightness(secondary_color, -20)};
  
  /* Standard Colors */
  --success-color: #10b981;
  --error-color: #ef4444;
  --warning-color: #f59e0b;
  --info-color: #3b82f6;
  
  /* Gradients */
  --primary-gradient: linear-gradient(135deg, var(--primary-color) 0%, var(--secondary-color) 100%);
  --hero-gradient: linear-gradient(135deg, {primary_color} 0%, {secondary_color} 100%);
  --card-gradient: linear-gradient(145deg, #ffffff 0%, #f8fafc 100%);
  
  /* Spacing */
  --space-xs: 0.25rem;
  --space-sm: 0.5rem;
  --space-md: 1rem;
  --space-lg: 1.5rem;
  --space-xl: 2rem;
  --space-2xl: 3rem;
  --space-3xl: 4rem;
  
  /* Typography */
  --font-size-xs: 0.75rem;
  --font-size-sm: 0.875rem;
  --font-size-base: 1rem;
  --font-size-lg: 1.125rem;
  --font-size-xl: 1.25rem;
  --font-size-2xl: 1.5rem;
  --font-size-3xl: 1.875rem;
  --font-size-4xl: 2.25rem;
  --font-size-5xl: 3rem;
  
  /* Shadows */
  --shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
  --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
  --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
  --shadow-xl: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
  --shadow-2xl: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
  
  /* Border Radius */
  --radius-sm: 0.375rem;
  --radius-md: 0.5rem;
  --radius-lg: 0.75rem;
  --radius-xl: 1rem;
  --radius-2xl: 1.5rem;
  --radius-full: 9999px;
  
  /* Transitions */
  --transition-fast: 0.15s ease-in-out;
  --transition-base: 0.3s ease-in-out;
  --transition-slow: 0.5s ease-in-out;
  
  /* Glassmorphism */
  --glass-bg: rgba(255, 255, 255, 0.1);
  --glass-border: rgba(255, 255, 255, 0.2);
  --glass-blur: blur(20px);
  
  /* Z-index scale */
  --z-dropdown: 1000;
  --z-sticky: 1020;
  --z-fixed: 1030;
  --z-modal-backdrop: 1040;
  --z-modal: 1050;
  --z-popover: 1060;
  --z-tooltip: 1070;
}}

/* Dark mode support */
@media (prefers-color-scheme: dark) {{
  :root {{
    --glass-bg: rgba(0, 0, 0, 0.1);
    --glass-border: rgba(255, 255, 255, 0.1);
    --card-gradient: linear-gradient(145deg, #1f2937 0%, #111827 100%);
  }}
  
  body {{
    background-color: #0f172a;
    color: #f1f5f9;
  }}
}}

/* Professional animations */
@keyframes fadeInUp {{
  from {{
    opacity: 0;
    transform: translateY(30px);
  }}
  to {{
    opacity: 1;
    transform: translateY(0);
  }}
}}

@keyframes fadeInLeft {{
  from {{
    opacity: 0;
    transform: translateX(-30px);
  }}
  to {{
    opacity: 1;
    transform: translateX(0);
  }}
}}

@keyframes fadeInRight {{
  from {{
    opacity: 0;
    transform: translateX(30px);
  }}
  to {{
    opacity: 1;
    transform: translateX(0);
  }}
}}

@keyframes scaleIn {{
  from {{
    opacity: 0;
    transform: scale(0.9);
  }}
  to {{
    opacity: 1;
    transform: scale(1);
  }}
}}

@keyframes bounce {{
  0%, 20%, 53%, 80%, 100% {{
    transform: translate3d(0,0,0);
  }}
  40%, 43% {{
    transform: translate3d(0, -15px, 0);
  }}
  70% {{
    transform: translate3d(0, -7px, 0);
  }}
  90% {{
    transform: translate3d(0, -2px, 0);
  }}
}}

@keyframes pulse {{
  0% {{
    transform: scale(1);
  }}
  50% {{
    transform: scale(1.05);
  }}
  100% {{
    transform: scale(1);
  }}
}}

@keyframes shimmer {{
  0% {{
    background-position: -200px 0;
  }}
  100% {{
    background-position: calc(200px + 100%) 0;
  }}
}}

@keyframes spin {{
  to {{
    transform: rotate(360deg);
  }}
}}

/* Global utility classes */
.glassmorphism {{
  background: var(--glass-bg);
  backdrop-filter: var(--glass-blur);
  -webkit-backdrop-filter: var(--glass-blur);
  border: 1px solid var(--glass-border);
  border-radius: var(--radius-lg);
}}

.gradient-text {{
  background: var(--primary-gradient);
  -webkit-background-clip: text;
  background-clip: text;
  -webkit-text-fill-color: transparent;
}}

.animate-fade-in-up {{
  animation: fadeInUp 0.6s ease-out;
}}

.animate-fade-in-left {{
  animation: fadeInLeft 0.6s ease-out;
}}

.animate-fade-in-right {{
  animation: fadeInRight 0.6s ease-out;
}}

.animate-scale-in {{
  animation: scaleIn 0.5s ease-out;
}}

.animate-bounce {{
  animation: bounce 2s infinite;
}}

.animate-pulse {{
  animation: pulse 2s infinite;
}}

.animate-spin {{
  animation: spin 1s linear infinite;
}}

/* Professional hover effects */
.hover-lift {{
  transition: transform var(--transition-base), box-shadow var(--transition-base);
}}

.hover-lift:hover {{
  transform: translateY(-5px);
  box-shadow: var(--shadow-xl);
}}

.hover-glow {{
  transition: box-shadow var(--transition-base);
}}

.hover-glow:hover {{
  box-shadow: 0 0 20px rgba(79, 70, 229, 0.4);
}}

.hover-scale {{
  transition: transform var(--transition-base);
}}

.hover-scale:hover {{
  transform: scale(1.05);
}}

/* Professional button styles */
.btn-professional {{
  background: var(--primary-gradient);
  border: none;
  border-radius: var(--radius-lg);
  padding: var(--space-md) var(--space-xl);
  font-weight: 600;
  color: white;
  text-decoration: none;
  display: inline-flex;
  align-items: center;
  gap: var(--space-sm);
  transition: all var(--transition-base);
  box-shadow: var(--shadow-md);
}}

.btn-professional:hover {{
  transform: translateY(-2px);
  box-shadow: var(--shadow-lg);
  color: white;
}}

/* Professional card styles */
.card-professional {{
  background: var(--card-gradient);
  border: 1px solid rgba(0, 0, 0, 0.05);
  border-radius: var(--radius-xl);
  padding: var(--space-xl);
  box-shadow: var(--shadow-sm);
  transition: all var(--transition-base);
}}

.card-professional:hover {{
  transform: translateY(-5px);
  box-shadow: var(--shadow-lg);
  border-color: var(--primary-color);
}}

/* Professional navigation */
.nav-professional {{
  background: var(--glass-bg);
  backdrop-filter: var(--glass-blur);
  -webkit-backdrop-filter: var(--glass-blur);
  border-bottom: 1px solid var(--glass-border);
}}

/* Professional loading states */
.loading-shimmer {{
  background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
  background-size: 200px 100%;
  animation: shimmer 1.5s infinite;
}}

/* Responsive breakpoints helpers */
@media (max-width: 576px) {{
  .animate-fade-in-up,
  .animate-fade-in-left,
  .animate-fade-in-right {{
    animation-duration: 0.4s;
  }}
}}

/* Accessibility improvements */
@media (prefers-reduced-motion: reduce) {{
  * {{
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
  }}
}}

/* Print styles */
@media print {{
  .btn,
  .navbar,
  .footer {{
    display: none !important;
  }}
}}"""
        },
        "public": {
            "index.html": f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <link rel="icon" href="%PUBLIC_URL%/favicon.ico" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <meta name="theme-color" content="{primary_color}" />
  <meta name="description" content="Professional React website generated automatically with modern design and responsive layout" />
  <meta name="keywords" content="react, website, professional, responsive, bootstrap" />
  <meta name="author" content="AI Website Generator" />
  
  <!-- Open Graph Meta Tags -->
  <meta property="og:title" content="Generated React Website" />
  <meta property="og:description" content="Professional React website with modern design" />
  <meta property="og:type" content="website" />
  <meta property="og:url" content="/" />
  
  <!-- Twitter Card Meta Tags -->
  <meta name="twitter:card" content="summary_large_image" />
  <meta name="twitter:title" content="Generated React Website" />
  <meta name="twitter:description" content="Professional React website with modern design" />
  
  <link rel="apple-touch-icon" href="%PUBLIC_URL%/logo192.png" />
  <link rel="manifest" href="%PUBLIC_URL%/manifest.json" />
  
  <!-- Preconnect to external domains for performance -->
  <link rel="preconnect" href="https://cdn.jsdelivr.net" />
  <link rel="dns-prefetch" href="https://cdn.jsdelivr.net" />
  
  <title>Generated React Website</title>
  
  <!-- Bootstrap 5 CDN -->
  <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet" integrity="sha384-T3c6CoIi6uLrA9TneNEoa7RxnatzjcDSCmG1MXxSR1GAsXEV/Dwwykc2MPK8M2HN" crossorigin="anonymous">
  
  <!-- Bootstrap Icons -->
  <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/font/bootstrap-icons.min.css">
  
  <!-- Custom CSS Variables -->
  <style>
    :root {{
      --bs-primary: {primary_color};
      --bs-secondary: {secondary_color};
      --bs-primary-rgb: {hex_to_rgb(primary_color)};
      --bs-secondary-rgb: {hex_to_rgb(secondary_color)};
    }}
  </style>
</head>
<body>
  <noscript>You need to enable JavaScript to run this app.</noscript>
  <div id="root"></div>
  
  <!-- Bootstrap JS Bundle -->
  <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/js/bootstrap.bundle.min.js" integrity="sha384-C6RzsynM9kWDrMNeT87bh95OGNyZPhcTNXj1NW7RuBCsyN/o0jlpcV8Qyq46cDfL" crossorigin="anonymous"></script>
</body>
</html>""",
            "favicon.ico": "",
            "logo192.png": "",
            "logo512.png": "",
            "robots.txt": """# https://www.robotstxt.org/robotstxt.html
User-agent: *
Disallow: /admin/
Disallow: /private/
Allow: /

# Sitemap
Sitemap: /sitemap.xml""",
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
                "theme_color": primary_color,
                "background_color": "#ffffff",
                "orientation": "portrait-primary"
            }, indent=2)
        },
        "package.json": json.dumps({
            "name": "generated-react-website",
            "version": "0.1.0",
            "private": True,
            "description": "Professional React website generated automatically",
            "keywords": ["react", "website", "bootstrap", "responsive"],
            "author": "AI Website Generator",
            "license": "MIT",
            "dependencies": {
                "@testing-library/jest-dom": "^5.16.5",
                "@testing-library/react": "^13.4.0",
                "@testing-library/user-event": "^13.5.0",
                "react": "^18.2.0",
                "react-dom": "^18.2.0",
                "react-router-dom": "^6.8.1",
                "react-scripts": "5.0.1",
                "web-vitals": "^2.1.4",
                "bootstrap": "^5.3.2"
            },
            "scripts": {
                "start": "react-scripts start",
                "build": "react-scripts build",
                "test": "react-scripts test",
                "eject": "react-scripts eject",
                "analyze": "npm run build && npx source-map-explorer 'build/static/js/*.js'",
                "lint": "eslint src --ext .js,.jsx,.ts,.tsx",
                "format": "prettier --write src"
            },
            "eslintConfig": {
                "extends": [
                    "react-app",
                    "react-app/jest"
                ]
            },
            "browserslist": {
                "production": [
                    ">0.2%",
                    "not dead",
                    "not op_mini all"
                ],
                "development": [
                    "last 1 chrome version",
                    "last 1 firefox version",
                    "last 1 safari version"
                ]
            },
            "engines": {
                "node": ">=16.0.0",
                "npm": ">=8.0.0"
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
.env
.env.local
.env.development.local
.env.test.local
.env.production.local

# logs
npm-debug.log*
yarn-debug.log*
yarn-error.log*
lerna-debug.log*

# Runtime data
pids
*.pid
*.seed
*.pid.lock

# IDE files
.vscode/
.idea/
*.swp
*.swo
*~

# OS generated files
.DS_Store
.DS_Store?
._*
.Spotlight-V100
.Trashes
ehthumbs.db
Thumbs.db""",
        "README.md": f"""# Generated React Website

This professional React website was generated automatically using AI and includes modern design patterns, responsive layout, and production-ready features.

## 🚀 Features

- ⚛️ **React 18** with functional components and hooks
- 🎨 **Bootstrap 5** for responsive design and components
- 🧭 **React Router** for seamless navigation
- 🎭 **Bootstrap Icons** for comprehensive iconography
- 📱 **Fully responsive** design for all devices
- 🎯 **Professional animations** and interactions
- 🔧 **CSS Custom Properties** for consistent theming
- 🌙 **Dark mode support** with system preference detection
- ♿ **Accessibility features** built-in
- 🚀 **Production-ready** build configuration

## 🎨 Theme Colors

- **Primary Color:** `{primary_color}`
- **Secondary Color:** `{secondary_color}`

## 📦 Generated Components

{chr(10).join([f'- **{name}** - Professional component with CSS animations and interactions' for name in state.get('components', {}).keys()])}

## 📄 Generated Pages

{chr(10).join([f'- **{name}** - Responsive page with modern design patterns' for name in state.get('pages', {}).keys()])}

## 🚀 Quick Start

1. **Extract the ZIP file**
   ```bash
   unzip react_website.zip
   cd generated-react-website
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```

3. **Start development server**
   ```bash
   npm start
   ```

4. **Open in browser**
   - Navigate to [http://localhost:3000](http://localhost:3000)
   - The app will automatically reload when you make changes

## 📜 Available Scripts

- `npm start` - Runs the app in development mode
- `npm run build` - Builds the app for production
- `npm test` - Launches the test runner
- `npm run eject` - **Note: this is a one-way operation!**
- `npm run analyze` - Analyzes the bundle size
- `npm run lint` - Runs ESLint for code quality
- `npm run format` - Formats code with Prettier

## 📁 Project Structure

```
src/
├── components/          # {len(state.get('components', {}))} Reusable UI components
│   ├── Navbar.jsx      # Navigation component
│   ├── Hero.jsx        # Hero section
│   ├── Features.jsx    # Features showcase
│   ├── Pricing.jsx     # Pricing cards
│   ├── Footer.jsx      # Site footer
│   └── *.css          # Component-specific styles
├── pages/              # {len(state.get('pages', {}))} Page components
│   ├── Landing.jsx     # Landing/home page
│   ├── Main.jsx        # Main/features page
│   ├── Checkout.jsx    # Checkout/pricing page
│   └── *.css          # Page-specific styles
├── App.jsx            # Main app component with routing
├── index.js           # Entry point
└── index.css          # Global styles and CSS variables
```

## 🎨 Styling Architecture

- **Global Variables** - CSS custom properties for consistent theming
- **Component Styles** - Modular CSS files for each component
- **Bootstrap Integration** - Enhanced with custom CSS for unique designs
- **Responsive Design** - Mobile-first approach with breakpoint utilities
- **Animations** - Smooth transitions and micro-interactions

## 🔧 Customization

### Changing Theme Colors

Edit the CSS custom properties in `src/index.css`:

```css
:root {{
  --primary-color: {primary_color};
  --secondary-color: {secondary_color};
}}
```

### Adding New Components

1. Create component file: `src/components/MyComponent.jsx`
2. Create styles file: `src/components/MyComponent.css`
3. Import and use in your pages

### Modifying Layout

- Edit page components in `src/pages/`
- Adjust component arrangements and props
- Update routing in `src/App.jsx` if needed

## 📱 Responsive Breakpoints

- **Mobile**: < 576px
- **Tablet**: 576px - 768px
- **Desktop**: 768px - 992px
- **Large Desktop**: > 992px

## 🌙 Dark Mode Support

The website automatically detects system theme preference and applies appropriate styles.

## ♿ Accessibility Features

- Semantic HTML structure
- ARIA labels and roles
- Keyboard navigation support
- Screen reader compatibility
- High contrast ratios

## 🚀 Production Deployment

1. **Build the project**
   ```bash
   npm run build
   ```

2. **Deploy the `build` folder** to your hosting service:
   - Netlify, Vercel, GitHub Pages
   - AWS S3, Azure Static Web Apps
   - Any static hosting service

## 🔗 Useful Links

- [React Documentation](https://reactjs.org/)
- [Bootstrap Documentation](https://getbootstrap.com/)
- [React Router Documentation](https://reactrouter.com/)
- [Bootstrap Icons](https://icons.getbootstrap.com/)

## 📝 License

This project is generated automatically and is available under the MIT License.

---

Generated with ❤️ by **AI Website Generator**

**Enjoy your new professional React website!** 🎉
"""
    }
    
    # Debug: Print final project structure
    print(f"📁 Final project structure:")
    print(f"   Components: {len(state['react_project']['src']['components'])} files")
    print(f"   Pages: {len(state['react_project']['src']['pages'])} files")
    print(f"   Public files: {len(state['react_project']['public'])} files")
    
    return state

def create_zip_file(state: AgentState) -> AgentState:
    """Create ZIP file from the React project structure"""
    
    if not state.get("react_project"):
        print("❌ No React project to zip")
        return state
    
    # Create output directory
    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)
    
    # Create unique ZIP filename
    import time
    timestamp = int(time.time())
    zip_filename = f"react_website_{timestamp}.zip"
    zip_path = output_dir / zip_filename
    
    try:
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            project = state["react_project"]
            
            # Write all files to ZIP
            def write_directory(directory_dict, base_path=""):
                for filename, content in directory_dict.items():
                    if isinstance(content, dict):
                        # It's a subdirectory
                        write_directory(content, f"{base_path}{filename}/")
                    else:
                        # It's a file
                        file_path = f"{base_path}{filename}"
                        zipf.writestr(file_path, content)
                        print(f"   📄 Added: {file_path}")
            
            print(f"📦 Creating ZIP file: {zip_filename}")
            write_directory(project)
            
        state["zip_path"] = str(zip_path)
        print(f"✅ ZIP file created successfully: {zip_path}")
        print(f"📊 ZIP file size: {zip_path.stat().st_size / 1024:.1f} KB")
        
    except Exception as e:
        print(f"❌ Error creating ZIP file: {e}")
        state["zip_path"] = None
    
    return state

def adjust_color_brightness(hex_color: str, percent: int) -> str:
    """Adjust color brightness by percentage (-100 to 100)"""
    try:
        # Remove # if present
        hex_color = hex_color.lstrip('#')
        
        # Convert hex to RGB
        r = int(hex_color[0:2], 16)
        g = int(hex_color[2:4], 16)
        b = int(hex_color[4:6], 16)
        
        # Adjust brightness
        factor = 1 + (percent / 100)
        r = min(255, max(0, int(r * factor)))
        g = min(255, max(0, int(g * factor)))
        b = min(255, max(0, int(b * factor)))
        
        # Convert back to hex
        return f"#{r:02x}{g:02x}{b:02x}"
    except:
        return hex_color  # Return original if error

def hex_to_rgb(hex_color: str) -> str:
    """Convert hex color to RGB values"""
    try:
        hex_color = hex_color.lstrip('#')
        r = int(hex_color[0:2], 16)
        g = int(hex_color[2:4], 16)
        b = int(hex_color[4:6], 16)
        return f"{r}, {g}, {b}"
    except:
        return "79, 70, 229"  # Default blue