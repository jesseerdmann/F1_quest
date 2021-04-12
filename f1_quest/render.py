from f1_quest.answer_key import AnswerKey
from jinja2 import Environment, FileSystemLoader


def render_static_pages(base_url="https://jesseerdmann.github.io/F1_quest"):
    ak = AnswerKey()
    file_loader = FileSystemLoader('f1_quest/templates')
    env = Environment(loader=file_loader)

    index = env.get_template('index.html')

    with open('docs/index.html', 'w') as out:
        out.write(index.render(overall_table=ak.get_overall_standings(), 
            base_url=base_url, questions=ak.questions,
            entries=ak.entries, drivers=ak.drivers,
            races=ak.races, teams=ak.teams))

    result = env.get_template('result.html')
    for question in ak.questions:
        with open(f"docs/results/{question.short_name.replace(':', '').replace(' ', '_')}.html", 'w') as out:
            out.write(result.render(question=question, 
                base_url=base_url, questions=ak.questions,
                entries=ak.entries, drivers=ak.drivers,
                races=ak.races, teams=ak.teams))
