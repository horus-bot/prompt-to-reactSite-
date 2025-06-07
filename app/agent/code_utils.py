import re

def extract_code_and_css(text: str):
    """Enhanced extraction with TypeScript and modern syntax support"""
    code_blocks = re.findall(r"```([a-zA-Z]*)\n([\s\S]*?)```", text)
    js_code, css_code = "", ""
    
    for lang, block in code_blocks:
        lang = lang.lower().strip()
        if lang in ["js", "jsx", "javascript", "typescript", "tsx", "ts", "react"]:
            js_code = block.strip()
        elif lang in ["css", "scss", "sass", "less"]:
            css_code = block.strip()
    
    if not js_code:
        js_match = re.search(r"```\n([\s\S]*?)```", text)
        if js_match:
            js_code = js_match.group(1).strip()
    
    return clean_imports(js_code), css_code

def extract_code(text: str) -> str:
    """Extract code from markdown blocks"""
    match = re.search(r"```(?:[a-zA-Z]+\n)?([\s\S]*?)```", text)
    if match:
        return match.group(1).strip()
    return text.strip()

def clean_imports(code: str) -> str:
    """Enhanced import cleaning with TypeScript support"""
    if not code:
        return ""
    
    # Fix React-specific issues
    code = code.replace(' class=', ' className=')
    code = code.replace('"class"', '"className"')
    code = code.replace("'class'", "'className'")
    
    # Remove problematic imports
    forbidden_imports = [
        "@headlessui/react", "@heroicons/react", "react-bootstrap", 
        "react-icons", "react-bootstrap-icons", "@fortawesome", 
        "font-awesome", "react-fontawesome", "antd", "material-ui",
        "@mui/material", "semantic-ui-react", "chakra-ui"
    ]
    
    lines = code.splitlines()
    filtered_lines = []
    
    for line in lines:
        skip_line = False
        for forbidden in forbidden_imports:
            if forbidden in line and "import" in line:
                skip_line = True
                break
        
        if not skip_line:
            filtered_lines.append(line)
    
    return "\n".join(filtered_lines)