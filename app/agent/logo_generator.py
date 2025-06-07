import re
from .models import AgentState

def generate_professional_logo(state: AgentState) -> tuple[str, str]:
    """Generate a professional text-based logo with CSS animations"""
    
    website_desc = state.get("website_desc", "Company")
    primary_color = state.get("primary_color", "#4f46e5")
    secondary_color = state.get("secondary_color", "#06b6d4")
    
    # Extract company name from description
    company_name = website_desc.split(" - ")[0].strip() if " - " in website_desc else website_desc.split()[0]
    
    logo_jsx = f"""import React from 'react';
import './Logo.css';

export default function Logo({{ className = '', size = 'md' }}) {{
  return (
    <div className={{`logo-container logo-${{size}} ${{className}}`}}>
      <div className="logo-text">
        <span className="company-name">{company_name}</span>
        <div className="logo-accent"></div>
      </div>
    </div>
  );
}}"""

    logo_css = f""".logo-container {{
  display: inline-flex;
  align-items: center;
  cursor: pointer;
  transition: all 0.3s ease;
}}

.logo-text {{
  position: relative;
  display: flex;
  align-items: center;
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
}}

.company-name {{
  font-size: 1.75rem;
  font-weight: 800;
  background: linear-gradient(135deg, {primary_color} 0%, {secondary_color} 100%);
  -webkit-background-clip: text;
  background-clip: text;
  -webkit-text-fill-color: transparent;
  letter-spacing: -0.02em;
  transition: all 0.3s ease;
}}

.logo-accent {{
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: linear-gradient(135deg, {primary_color} 0%, {secondary_color} 100%);
  margin-left: 4px;
  animation: pulse 2s infinite;
}}

.logo-container:hover .company-name {{
  transform: scale(1.05);
  filter: brightness(1.1);
}}

.logo-container:hover .logo-accent {{
  animation: bounce 0.6s ease-in-out;
}}

/* Size variants */
.logo-sm .company-name {{
  font-size: 1.25rem;
}}

.logo-sm .logo-accent {{
  width: 6px;
  height: 6px;
}}

.logo-lg .company-name {{
  font-size: 2.5rem;
}}

.logo-lg .logo-accent {{
  width: 12px;
  height: 12px;
}}

.logo-xl .company-name {{
  font-size: 3rem;
}}

.logo-xl .logo-accent {{
  width: 16px;
  height: 16px;
}}

/* Animations */
@keyframes pulse {{
  0% {{
    transform: scale(1);
    opacity: 1;
  }}
  50% {{
    transform: scale(1.2);
    opacity: 0.7;
  }}
  100% {{
    transform: scale(1);
    opacity: 1;
  }}
}}

@keyframes bounce {{
  0%, 20%, 53%, 80%, 100% {{
    transform: translate3d(0,0,0) scale(1);
  }}
  40%, 43% {{
    transform: translate3d(0, -8px, 0) scale(1.1);
  }}
  70% {{
    transform: translate3d(0, -4px, 0) scale(1.05);
  }}
  90% {{
    transform: translate3d(0, -1px, 0) scale(1.02);
  }}
}}

/* Dark mode support */
@media (prefers-color-scheme: dark) {{
  .company-name {{
    filter: brightness(1.2);
  }}
}}

/* Responsive adjustments */
@media (max-width: 768px) {{
  .logo-container .company-name {{
    font-size: 1.5rem;
  }}
  
  .logo-lg .company-name {{
    font-size: 2rem;
  }}
  
  .logo-xl .company-name {{
    font-size: 2.5rem;
  }}
}}"""

    return logo_jsx, logo_css

def extract_company_name(website_desc: str) -> str:
    """Extract company name from website description"""
    # Look for patterns like "CompanyName -" or "CompanyName:"
    patterns = [
        r'^([A-Z][a-zA-Z0-9]*(?:[A-Z][a-zA-Z0-9]*)*)\s*[-:]',  # "TaskFlow -" or "TaskFlow:"
        r'([A-Z][a-zA-Z0-9]*(?:[A-Z][a-zA-Z0-9]*)*)',  # Any CamelCase word
    ]
    
    for pattern in patterns:
        match = re.search(pattern, website_desc)
        if match:
            return match.group(1)
    
    # Fallback: use first word or generate name
    words = website_desc.split()
    if words:
        return words[0].title()
    
    return "Logo"

def determine_logo_style(website_desc: str) -> str:
    """Determine logo style based on website description"""
    desc_lower = website_desc.lower()
    
    if any(word in desc_lower for word in ['ai', 'tech', 'software', 'platform', 'app', 'digital', 'cloud', 'data']):
        return "tech"
    elif any(word in desc_lower for word in ['creative', 'design', 'art', 'studio', 'agency', 'media']):
        return "creative"
    elif any(word in desc_lower for word in ['corporate', 'business', 'enterprise', 'consulting', 'finance', 'professional']):
        return "corporate"
    else:
        return "modern"

def generate_tech_logo(company_name: str, primary_color: str, secondary_color: str) -> tuple:
    """Generate tech-style logo with geometric elements"""
    
    logo_jsx = f'''
import {{ Link }} from 'react-router-dom';
import './Logo.css';

export default function Logo() {{
  return (
    <Link to="/" className="logo-link tech-logo">
      <div className="logo-icon">
        <div className="logo-cube">
          <div className="cube-face cube-front"></div>
          <div className="cube-face cube-back"></div>
          <div className="cube-face cube-right"></div>
          <div className="cube-face cube-left"></div>
          <div className="cube-face cube-top"></div>
          <div className="cube-face cube-bottom"></div>
        </div>
      </div>
      <span className="logo-text">{company_name}</span>
    </Link>
  );
}}'''
    
    logo_css = f'''
.tech-logo {{
  display: inline-flex;
  align-items: center;
  gap: var(--space-sm, 0.5rem);
  text-decoration: none;
  transition: all var(--transition-base, 0.3s ease);
}}

.tech-logo:hover {{
  transform: scale(1.05);
}}

.logo-icon {{
  position: relative;
  width: 32px;
  height: 32px;
  perspective: 100px;
}}

.logo-cube {{
  position: relative;
  width: 100%;
  height: 100%;
  transform-style: preserve-3d;
  animation: rotateCube 6s infinite linear;
}}

.cube-face {{
  position: absolute;
  width: 32px;
  height: 32px;
  background: linear-gradient(135deg, {primary_color}, {secondary_color});
  border: 1px solid rgba(255, 255, 255, 0.3);
}}

.cube-front  {{ transform: rotateY(  0deg) translateZ(16px); }}
.cube-back   {{ transform: rotateY(180deg) translateZ(16px); }}
.cube-right  {{ transform: rotateY( 90deg) translateZ(16px); }}
.cube-left   {{ transform: rotateY(-90deg) translateZ(16px); }}
.cube-top    {{ transform: rotateX( 90deg) translateZ(16px); }}
.cube-bottom {{ transform: rotateX(-90deg) translateZ(16px); }}

.logo-text {{
  font-size: var(--font-size-xl, 1.25rem);
  font-weight: 700;
  background: linear-gradient(135deg, {primary_color}, {secondary_color});
  -webkit-background-clip: text;
  background-clip: text;
  -webkit-text-fill-color: transparent;
  letter-spacing: -0.025em;
}}

@keyframes rotateCube {{
  0% {{ transform: rotateX(0deg) rotateY(0deg); }}
  100% {{ transform: rotateX(360deg) rotateY(360deg); }}
}}

@media (max-width: 768px) {{
  .logo-icon {{
    width: 28px;
    height: 28px;
  }}
  
  .cube-face {{
    width: 28px;
    height: 28px;
  }}
  
  .cube-front, .cube-back, .cube-right, .cube-left, .cube-top, .cube-bottom {{
    transform-origin: center;
  }}
  
  .cube-front  {{ transform: rotateY(  0deg) translateZ(14px); }}
  .cube-back   {{ transform: rotateY(180deg) translateZ(14px); }}
  .cube-right  {{ transform: rotateY( 90deg) translateZ(14px); }}
  .cube-left   {{ transform: rotateY(-90deg) translateZ(14px); }}
  .cube-top    {{ transform: rotateX( 90deg) translateZ(14px); }}
  .cube-bottom {{ transform: rotateX(-90deg) translateZ(14px); }}
  
  .logo-text {{
    font-size: var(--font-size-lg, 1.125rem);
  }}
}}'''
    
    return logo_jsx, logo_css

def generate_creative_logo(company_name: str, primary_color: str, secondary_color: str) -> tuple:
    """Generate creative logo with artistic elements"""
    
    logo_jsx = f'''
import {{ Link }} from 'react-router-dom';
import './Logo.css';

export default function Logo() {{
  return (
    <Link to="/" className="logo-link creative-logo">
      <div className="logo-icon">
        <svg width="32" height="32" viewBox="0 0 32 32" className="logo-svg">
          <defs>
            <linearGradient id="creativeGradient" x1="0%" y1="0%" x2="100%" y2="100%">
              <stop offset="0%" stopColor="{primary_color}" />
              <stop offset="100%" stopColor="{secondary_color}" />
            </linearGradient>
          </defs>
          <circle cx="16" cy="16" r="14" fill="url(#creativeGradient)" className="logo-circle"/>
          <path d="M8 16 L16 8 L24 16 L16 24 Z" fill="white" opacity="0.9" className="logo-diamond"/>
        </svg>
      </div>
      <span className="logo-text">{company_name}</span>
    </Link>
  );
}}'''
    
    logo_css = f'''
.creative-logo {{
  display: inline-flex;
  align-items: center;
  gap: var(--space-sm, 0.5rem);
  text-decoration: none;
  transition: all var(--transition-base, 0.3s ease);
}}

.creative-logo:hover {{
  transform: scale(1.05);
}}

.creative-logo:hover .logo-circle {{
  transform: scale(1.1);
}}

.creative-logo:hover .logo-diamond {{
  transform: rotate(45deg) scale(1.1);
}}

.logo-svg {{
  transition: all var(--transition-base, 0.3s ease);
}}

.logo-circle {{
  transition: transform var(--transition-base, 0.3s ease);
  transform-origin: center;
}}

.logo-diamond {{
  transition: transform var(--transition-base, 0.3s ease);
  transform-origin: center;
}}

.logo-text {{
  font-size: var(--font-size-xl, 1.25rem);
  font-weight: 700;
  background: linear-gradient(135deg, {primary_color}, {secondary_color});
  -webkit-background-clip: text;
  background-clip: text;
  -webkit-text-fill-color: transparent;
  letter-spacing: -0.025em;
}}

@media (max-width: 768px) {{
  .logo-text {{
    font-size: var(--font-size-lg, 1.125rem);
  }}
}}'''
    
    return logo_jsx, logo_css

def generate_corporate_logo(company_name: str, primary_color: str, secondary_color: str) -> tuple:
    """Generate professional corporate logo"""
    
    logo_jsx = f'''
import {{ Link }} from 'react-router-dom';
import './Logo.css';

export default function Logo() {{
  return (
    <Link to="/" className="logo-link corporate-logo">
      <div className="logo-icon">
        <div className="logo-bars">
          <div className="bar bar-1"></div>
          <div className="bar bar-2"></div>
          <div className="bar bar-3"></div>
        </div>
      </div>
      <span className="logo-text">{company_name}</span>
    </Link>
  );
}}'''
    
    logo_css = f'''
.corporate-logo {{
  display: inline-flex;
  align-items: center;
  gap: var(--space-sm, 0.5rem);
  text-decoration: none;
  transition: all var(--transition-base, 0.3s ease);
}}

.corporate-logo:hover {{
  transform: scale(1.05);
}}

.logo-bars {{
  display: flex;
  align-items: end;
  gap: 3px;
  height: 28px;
}}

.bar {{
  width: 6px;
  background: linear-gradient(to top, {primary_color}, {secondary_color});
  border-radius: 2px;
  transition: all var(--transition-base, 0.3s ease);
}}

.bar-1 {{
  height: 60%;
  animation: barGrow1 2s ease-in-out infinite;
}}

.bar-2 {{
  height: 100%;
  animation: barGrow2 2s ease-in-out infinite 0.3s;
}}

.bar-3 {{
  height: 80%;
  animation: barGrow3 2s ease-in-out infinite 0.6s;
}}

.corporate-logo:hover .bar {{
  transform: scaleY(1.1);
}}

.logo-text {{
  font-size: var(--font-size-xl, 1.25rem);
  font-weight: 600;
  color: {primary_color};
  letter-spacing: 0.025em;
  text-transform: uppercase;
}}

@keyframes barGrow1 {{
  0%, 100% {{ height: 60%; }}
  50% {{ height: 80%; }}
}}

@keyframes barGrow2 {{
  0%, 100% {{ height: 100%; }}
  50% {{ height: 70%; }}
}}

@keyframes barGrow3 {{
  0%, 100% {{ height: 80%; }}
  50% {{ height: 100%; }}
}}

@media (max-width: 768px) {{
  .logo-text {{
    font-size: var(--font-size-lg, 1.125rem);
  }}
  
  .logo-bars {{
    height: 24px;
  }}
}}'''
    
    return logo_jsx, logo_css

def generate_modern_logo(company_name: str, primary_color: str, secondary_color: str) -> tuple:
    """Generate modern minimalist logo"""
    
    logo_jsx = f'''
import {{ Link }} from 'react-router-dom';
import './Logo.css';

export default function Logo() {{
  return (
    <Link to="/" className="logo-link modern-logo">
      <div className="logo-icon">
        <div className="logo-rings">
          <div className="ring ring-outer"></div>
          <div className="ring ring-inner"></div>
          <div className="ring ring-center"></div>
        </div>
      </div>
      <span className="logo-text">{company_name}</span>
    </Link>
  );
}}'''
    
    logo_css = f'''
.modern-logo {{
  display: inline-flex;
  align-items: center;
  gap: var(--space-sm, 0.5rem);
  text-decoration: none;
  transition: all var(--transition-base, 0.3s ease);
}}

.modern-logo:hover {{
  transform: scale(1.05);
}}

.logo-rings {{
  position: relative;
  width: 32px;
  height: 32px;
}}

.ring {{
  position: absolute;
  border-radius: 50%;
  animation: pulse 3s ease-in-out infinite;
}}

.ring-outer {{
  width: 32px;
  height: 32px;
  border: 3px solid {primary_color};
  opacity: 0.6;
  top: 0;
  left: 0;
}}

.ring-inner {{
  width: 22px;
  height: 22px;
  border: 2px solid {secondary_color};
  opacity: 0.8;
  top: 5px;
  left: 5px;
  animation-delay: 0.5s;
}}

.ring-center {{
  width: 12px;
  height: 12px;
  background: linear-gradient(135deg, {primary_color}, {secondary_color});
  top: 10px;
  left: 10px;
  animation-delay: 1s;
}}

.modern-logo:hover .ring {{
  animation-play-state: paused;
  transform: scale(1.1);
}}

.logo-text {{
  font-size: var(--font-size-xl, 1.25rem);
  font-weight: 300;
  color: {primary_color};
  letter-spacing: 0.05em;
}}

@keyframes pulse {{
  0%, 100% {{
    transform: scale(1);
    opacity: 1;
  }}
  50% {{
    transform: scale(1.05);
    opacity: 0.7;
  }}
}}

@media (max-width: 768px) {{
  .logo-rings {{
    width: 28px;
    height: 28px;
  }}
  
  .ring-outer {{
    width: 28px;
    height: 28px;
  }}
  
  .ring-inner {{
    width: 18px;
    height: 18px;
    top: 5px;
    left: 5px;
  }}
  
  .ring-center {{
    width: 10px;
    height: 10px;
    top: 9px;
    left: 9px;
  }}
  
  .logo-text {{
    font-size: var(--font-size-lg, 1.125rem);
  }}
}}'''
    
    return logo_jsx, logo_css