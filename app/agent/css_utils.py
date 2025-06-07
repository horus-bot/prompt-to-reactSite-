import re

def clean_css(css_code: str) -> str:
    """Enhanced CSS cleaning with professional design patterns"""
    if not css_code:
        return ""
    
    # Remove any invalid syntax
    cleaned = css_code.replace('class=', 'className=')
    
    # Split into lines for processing
    lines = cleaned.split('\n')
    fixed_lines = []
    in_rule = False
    in_media = False
    in_keyframes = False
    brace_count = 0
    
    for i, line in enumerate(lines):
        stripped_line = line.strip()
        
        # Skip empty lines
        if not stripped_line:
            fixed_lines.append("")
            continue
        
        # Handle closing braces
        if stripped_line == '}':
            fixed_lines.append(stripped_line)
            brace_count -= 1
            if brace_count <= 0:
                in_rule = False
                in_media = False
                in_keyframes = False
                brace_count = 0
            continue
        
        # Handle CSS selectors
        if stripped_line.endswith('{'):
            stripped_line = re.sub(r';+\s*{', ' {', stripped_line)
            stripped_line = re.sub(r',\s*;\s*', ', ', stripped_line)
            stripped_line = re.sub(r';\s*$', '', stripped_line.rstrip('{')) + ' {'
            
            fixed_lines.append(stripped_line)
            in_rule = True
            brace_count += 1
            continue
        
        # Handle CSS properties
        if (in_rule or in_media or in_keyframes) and ':' in stripped_line and not stripped_line.startswith('/*'):
            if not stripped_line.endswith(';'):
                stripped_line += ';'
            
            stripped_line = re.sub(r';+', ';', stripped_line)
            stripped_line = re.sub(r',\s*;', ';', stripped_line)
            
            if not stripped_line.startswith(('  ', '\t')):
                stripped_line = '  ' + stripped_line
            
            fixed_lines.append(stripped_line)
            continue
        
        fixed_lines.append(stripped_line)
    
    result = '\n'.join(fixed_lines)
    return add_professional_css_patterns(result)

def add_professional_css_patterns(css_code: str) -> str:
    """Add professional design patterns to CSS"""
    
    css_variables = """
:root {
  /* Color Palette */
  --primary-color: #4f46e5;
  --primary-hover: #4338ca;
  --secondary-color: #06b6d4;
  --secondary-hover: #0891b2;
  --accent-color: #f59e0b;
  --success-color: #10b981;
  --error-color: #ef4444;
  --warning-color: #f59e0b;
  
  /* Gradients */
  --primary-gradient: linear-gradient(135deg, var(--primary-color) 0%, var(--secondary-color) 100%);
  --hero-gradient: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  --card-gradient: linear-gradient(145deg, #ffffff 0%, #f8fafc 100%);
  
  /* Spacing */
  --space-xs: 0.25rem;
  --space-sm: 0.5rem;
  --space-md: 1rem;
  --space-lg: 1.5rem;
  --space-xl: 2rem;
  --space-2xl: 3rem;
  
  /* Typography */
  --font-size-xs: 0.75rem;
  --font-size-sm: 0.875rem;
  --font-size-base: 1rem;
  --font-size-lg: 1.125rem;
  --font-size-xl: 1.25rem;
  --font-size-2xl: 1.5rem;
  --font-size-3xl: 1.875rem;
  --font-size-4xl: 2.25rem;
  
  /* Shadows */
  --shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
  --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
  --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
  --shadow-xl: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
  
  /* Border Radius */
  --radius-sm: 0.375rem;
  --radius-md: 0.5rem;
  --radius-lg: 0.75rem;
  --radius-xl: 1rem;
  --radius-full: 9999px;
  
  /* Transitions */
  --transition-fast: 0.15s ease-in-out;
  --transition-base: 0.3s ease-in-out;
  --transition-slow: 0.5s ease-in-out;
  
  /* Glassmorphism */
  --glass-bg: rgba(255, 255, 255, 0.1);
  --glass-border: rgba(255, 255, 255, 0.2);
  --glass-blur: blur(20px);
}

/* Professional animations */
@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes pulse {
  0% {
    transform: scale(1);
  }
  50% {
    transform: scale(1.05);
  }
  100% {
    transform: scale(1);
  }
}

/* Professional utility classes */
.glassmorphism {
  background: var(--glass-bg);
  backdrop-filter: var(--glass-blur);
  -webkit-backdrop-filter: var(--glass-blur);
  border: 1px solid var(--glass-border);
  border-radius: var(--radius-lg);
}

.hover-lift:hover {
  transform: translateY(-5px);
  box-shadow: var(--shadow-xl);
  transition: all var(--transition-base);
}
"""
    
    if ':root' not in css_code:
        css_code = css_variables + '\n\n' + css_code
    
    return css_code