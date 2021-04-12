from f1_quest.answer_key import AnswerKey
from jinja2 import Environment, FileSystemLoader


def render_static_pages(base_url="https://jesseerdmann.github.io/F1_quest"):
    ak = AnswerKey()
    file_loader = FileSystemLoader('f1_quest/templates')
    env = Environment(loader=file_loader)

    index = env.get_template('index.html')

    with open('site/index.html', 'w') as out:
        out.write(index.render(overall_table=ak.get_overall_standings(), 
            base_url=base_url))