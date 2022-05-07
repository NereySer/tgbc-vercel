from jinja2 import Template
from datetime import datetime

templates = {}

def initTemplate(name: str):
    global templates
    
    if name not in templates:
        j2 = open(f'templates/{name}.j2').read()
        
        templates[name] = Template(j2, trim_blocks=True, lstrip_blocks=True)
    
    return templates[name]

def telegram(events, diff) -> str:
    template = initTemplate('telegram_message')
    
    return template.render(events=events, diff=diff, datetime=datetime)

def web(content, html:bool=True):
    template = initTemplate('raise.html' if html else 'raise')
    
    return template.render(content=content)
