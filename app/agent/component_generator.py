from .models import AgentState
from .logo_generator import generate_professional_logo
from .code_utils import extract_code_and_css, clean_imports
from .css_utils import clean_css
from .llm_utils import groq_client, MODEL_NAME

def generate_components(state: AgentState) -> AgentState:
    """Generate shared React components with professional styling"""
    
    # Generate logo first
    logo_jsx, logo_css = generate_professional_logo(state)
    
    # Initialize components
    state["components"] = {"Logo": logo_jsx}
    state["component_css"] = {"Logo": logo_css}
    
    # Define all components that need to be generated
    component_specs = {
        "Navbar": f"""
Create a professional, glassmorphism navigation bar with:
- Sticky positioning with backdrop blur
- Mobile-responsive hamburger menu with smooth animations
- Logo integration using <Logo /> component
- Navigation links from props
- Dark mode toggle button
- Smooth hover animations and active states
- Professional spacing and typography
- Modern gradient borders and shadows
- CSS custom properties for theming
Use React hooks (useState, useEffect) for mobile menu toggle and scroll effects.
Primary color: {state.get('primary_color', '#4f46e5')}
Secondary color: {state.get('secondary_color', '#06b6d4')}
        """,
        
        "Hero": f"""
Create a stunning hero section with:
- Full viewport height with perfect centering
- Animated gradient backgrounds
- Typewriter effect for headlines using React hooks
- Floating elements with CSS animations
- Professional call-to-action buttons
- Responsive design with mobile optimizations
- CSS custom properties for colors and spacing
- Modern animations (fade-in, slide-up, scale)
- Glassmorphism cards and elements
- Interactive hover states and particle effects (CSS only)
Primary color: {state.get('primary_color', '#4f46e5')}
Secondary color: {state.get('secondary_color', '#06b6d4')}
        """,
        
        "Features": f"""
Create a modern features showcase section with:
- Grid layout for feature cards
- Animated icons and hover effects
- Glassmorphism card design
- Smooth reveal animations on scroll
- Interactive hover states with transform effects
- Responsive grid (1-2-3 columns based on screen size)
- Professional typography and spacing
- Bootstrap icons for feature icons
Primary color: {state.get('primary_color', '#4f46e5')}
Secondary color: {state.get('secondary_color', '#06b6d4')}
        """,
        
        "Pricing": f"""
Create professional pricing cards with:
- Modern card design with glassmorphism
- Recommended plan highlighting
- Interactive hover effects and animations
- Feature lists with checkmarks
- Call-to-action buttons
- Responsive grid layout
- Professional styling and spacing
- Smooth animations and transitions
Primary color: {state.get('primary_color', '#4f46e5')}
Secondary color: {state.get('secondary_color', '#06b6d4')}
        """,
        
        "Testimonials": f"""
Create testimonial carousel/grid with:
- Customer review cards
- Avatar images and star ratings
- Smooth carousel animations (CSS only)
- Glassmorphism card design
- Responsive layout
- Professional typography
- Hover effects and transitions
Primary color: {state.get('primary_color', '#4f46e5')}
Secondary color: {state.get('secondary_color', '#06b6d4')}
        """,
        
        "FAQ": f"""
Create interactive FAQ accordion with:
- Expandable question/answer sections
- Smooth accordion animations
- Professional styling
- Interactive states (hover, active, focus)
- Responsive design
- Search functionality (optional)
- Modern design patterns
Primary color: {state.get('primary_color', '#4f46e5')}
Secondary color: {state.get('secondary_color', '#06b6d4')}
        """,
        
        "Newsletter": f"""
Create newsletter signup component with:
- Email input with validation
- Professional form styling
- Success/error states
- Glassmorphism design
- Responsive layout
- Interactive animations
- Form submission handling with React hooks
Primary color: {state.get('primary_color', '#4f46e5')}
Secondary color: {state.get('secondary_color', '#06b6d4')}
        """,
        
        "Footer": f"""
Create comprehensive footer with:
- Multi-column layout
- Social media links
- Navigation links
- Company information
- Professional styling
- Responsive design
- Modern spacing and typography
Primary color: {state.get('primary_color', '#4f46e5')}
Secondary color: {state.get('secondary_color', '#06b6d4')}
        """,
        
        "ContactButton": f"""
Create floating contact button with:
- Fixed positioning (bottom-right)
- Smooth hover animations
- Glassmorphism design
- Professional styling
- Responsive behavior
- Interactive states
Primary color: {state.get('primary_color', '#4f46e5')}
Secondary color: {state.get('secondary_color', '#06b6d4')}
        """,
        
        "Sidebar": f"""
Create sidebar navigation with:
- Collapsible design
- Navigation links
- Search functionality
- Filter options
- Professional styling
- Smooth animations
- Responsive behavior
Primary color: {state.get('primary_color', '#4f46e5')}
Secondary color: {state.get('secondary_color', '#06b6d4')}
        """
    }
    
    # Generate each component
    for name, description in component_specs.items():
        try:
            print(f"Generating component: {name}")
            
            response = groq_client.chat.completions.create(
                model=MODEL_NAME,
                messages=[{
                    "role": "user",
                    "content": (
                        f"Create a professional, interactive React component named {name}. {description}\n\n"
                        f"COMPONENT REQUIREMENTS:\n"
                        f"- Create a functional React component with hooks (useState, useEffect as needed)\n"
                        f"- Use Bootstrap 5 classes for layout and basic styling\n"
                        f"- Add custom CSS for advanced effects, animations, and professional design\n"
                        f"- Import './Component.css' at the top for styles\n"
                        f"- Use React Router Link for navigation: import {{ Link }} from 'react-router-dom'\n"
                        f"- Use Bootstrap Icons: <i className='bi bi-icon-name'></i>\n"
                        f"- Make it fully responsive and accessible\n"
                        f"- Add smooth animations and hover effects\n"
                        f"- Use glassmorphism and modern design patterns\n"
                        f"- Apply the theme colors consistently\n\n"
                        f"CRITICAL CSS REQUIREMENTS:\n"
                        f"- All CSS selectors must end with space then {{ not semicolon\n"
                        f"- All CSS properties must end with semicolon\n"
                        f"- No comma-semicolon combinations\n"
                        f"- Use proper CSS syntax: .selector {{ property: value; }}\n"
                        f"- Add professional animations and transitions\n\n"
                        f"Return the React component in ```jsx block and CSS in ```css block.\n"
                        f"No explanations, just the code."
                    )
                }],
                temperature=0.3,
                max_tokens=2000
            )
            
            content = response.choices[0].message.content
            js_code, css_code = extract_code_and_css(content)
            
            if js_code:
                state["components"][name] = clean_imports(js_code)
                print(f"✅ Generated {name} component ({len(js_code)} chars)")
            else:
                print(f"❌ Failed to extract JS code for {name}")
                
            if css_code:
                state["component_css"][name] = clean_css(css_code)
                print(f"✅ Generated {name} CSS ({len(css_code)} chars)")
            else:
                print(f"⚠️ No CSS generated for {name}")
                
        except Exception as e:
            print(f"❌ Error generating component {name}: {e}")
            # Add a basic fallback component
            state["components"][name] = f"""
import './{name}.css';

export default function {name}() {{
  return (
    <div className="{name.lower()}-container">
      <h2>{name} Component</h2>
      <p>This is a placeholder for the {name} component.</p>
    </div>
  );
}}"""
            state["component_css"][name] = f"""
.{name.lower()}-container {{
  padding: 2rem;
  text-align: center;
  background: linear-gradient(135deg, {state.get('primary_color', '#4f46e5')}, {state.get('secondary_color', '#06b6d4')});
  color: white;
  border-radius: 1rem;
  margin: 1rem 0;
}}"""
    
    print(f"📦 Generated {len(state['components'])} components total")
    return state