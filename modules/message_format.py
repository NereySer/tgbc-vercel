from jinja2 import Environment, FileSystemLoader
from datetime import datetime

templates = {}
env = None

def initTemplate(name: str):
    global templates, env

    if env is None:
        env = Environment(
            loader=FileSystemLoader('templates'),
            trim_blocks=True,
            lstrip_blocks=True
        )
    
    if name not in templates:
        templates[name] = env.get_template(f'{name}.j2')
    
    return templates[name]

def telegram(events, diff) -> str:
    template = initTemplate('telegram_message')
    
    return template.render(events=events, diff=diff, datetime=datetime)

def web(content, html:bool=True):
    template = initTemplate('raise.html' if html else 'raise')
    
    return template.render(content=content)
