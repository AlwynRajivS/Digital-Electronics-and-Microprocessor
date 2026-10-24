import os

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
templates_dir = os.path.join(base_dir, 'templates')

with open(os.path.join(templates_dir, 'login.html'), 'r', encoding='utf-8') as f:
    login_html = f.read()

with open(os.path.join(templates_dir, 'index.html'), 'r', encoding='utf-8') as f:
    index_html = f.read()

# Replace Jinja tags for static root version
static_login = login_html.replace('{% if error %}', '<!--').replace('{% endif %}', '-->')
static_login = static_login.replace('href="/static/css/style.css"', 'href="static/css/style.css"')
with open(os.path.join(base_dir, 'login.html'), 'w', encoding='utf-8') as f:
    f.write(static_login)

static_index = index_html.replace("{{ user.avatar if user else 'S' }}", 'S')
static_index = static_index.replace("{{ user.full_name if user else 'SABARIAYYAN P' }}", 'SABARIAYYAN P')
static_index = static_index.replace("{{ user.section if user else 'Section B' }}", 'Section B')
static_index = static_index.replace('href="/static/css/style.css"', 'href="static/css/style.css"')
static_index = static_index.replace('src="/static/js/app.js"', 'src="static/js/app.js"')
with open(os.path.join(base_dir, 'index.html'), 'w', encoding='utf-8') as f:
    f.write(static_index)

print('SUCCESS: Created root login.html and index.html for instant VS Code / Live Server execution!')
