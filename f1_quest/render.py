import os

from datetime import datetime
from f1_quest.answer_key import AnswerKey
from jinja2 import Environment, FileSystemLoader


def render_static_pages(base_url="https://jesseerdmann.github.io/F1_quest", 
    data_dir='data', datetime=datetime.now(), output_dir='docs'):
    ak = AnswerKey(datetime=datetime)
    file_loader = FileSystemLoader('f1_quest/templates')
    env = Environment(loader=file_loader)

    index = env.get_template('index.html')
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    if not os.path.isdir(output_dir):
        raise Exception(f"{output_dir} is not a directory")
    with open(os.path.join(output_dir, 'index.html'), 'w') as out:
        out.write(index.render(overall_table=ak.get_overall_standings(), 
            base_url=base_url, questions=ak.questions,
            entries=ak.entries, drivers=ak.drivers,
            races=ak.races, teams=ak.teams))

    result = env.get_template('result.html')
    output_subdir = os.path.join(output_dir, "results")
    if not os.path.exists(output_subdir):
        os.makedirs(output_subdir)
    if not os.path.isdir(output_subdir):
        raise Exception(f"{output_subdir} is not a directory")
    for question in ak.questions:
        with open(os.path.join(output_subdir, 
            f"{question.short_name.replace(':', '').replace(' ', '_')}.html"), 'w') as out:
            out.write(result.render(question=question, 
                base_url=base_url, questions=ak.questions,
                entries=ak.entries, drivers=ak.drivers,
                races=ak.races, teams=ak.teams))

    entry_template = env.get_template('entry.html')
    output_subdir = os.path.join(output_dir, "entries")
    if not os.path.exists(output_subdir):
        os.makedirs(output_subdir)
    if not os.path.isdir(output_subdir):
        raise Exception(f"{output_subdir} is not a directory")
    for entry in ak.entries.list_entries():
        with open(os.path.join(output_dir, "entries", 
            f"{entry.entry_name.replace(' ', '_')}.html"), 'w') as out:
            out.write(entry_template.render(entry=entry, 
                base_url=base_url, questions=ak.questions,
                entries=ak.entries, drivers=ak.drivers,
                races=ak.races, teams=ak.teams))

    driver_template = env.get_template('driver.html')
    output_subdir = os.path.join(output_dir, "drivers")
    if not os.path.exists(output_subdir):
        os.makedirs(output_subdir)
    if not os.path.isdir(output_subdir):
        raise Exception(f"{output_subdir} is not a directory")
    for driver in ak.drivers.list_all_drivers():
        with open(os.path.join(output_dir, "drivers", 
            f"{str(driver).replace(', ', '_').replace(' ', '_')}.html"), 'w') as out:
            out.write(driver_template.render(driver=driver, 
                base_url=base_url, questions=ak.questions,
                entries=ak.entries, drivers=ak.drivers,
                races=ak.races, teams=ak.teams))

    team_template = env.get_template('team.html')
    output_subdir = os.path.join(output_dir, "teams")
    if not os.path.exists(output_subdir):
        os.makedirs(output_subdir)
    if not os.path.isdir(output_subdir):
        raise Exception(f"{output_subdir} is not a directory")
    for team in ak.teams.list_all_teams():
        with open(os.path.join(output_dir, "teams", 
            f"{team.name.replace(' ', '_')}.html"), 'w') as out:
            out.write(team_template.render(team=team, 
                base_url=base_url, questions=ak.questions,
                entries=ak.entries, drivers=ak.drivers,
                races=ak.races, teams=ak.teams))

    race_template = env.get_template('race.html')
    output_subdir = os.path.join(output_dir, "races")
    if not os.path.exists(output_subdir):
        os.makedirs(output_subdir)
    if not os.path.isdir(output_subdir):
        raise Exception(f"{output_subdir} is not a directory")
    for race in ak.races.list_races():
        with open(os.path.join(output_dir, "races", 
            f"{str(race).replace(' @ ', '_').replace(':', '_').replace('/', '_').replace(' ', '_')}.html"), 'w') as out:
            out.write(race_template.render(race=race, 
                base_url=base_url, questions=ak.questions,
                entries=ak.entries, drivers=ak.drivers,
                races=ak.races, teams=ak.teams))