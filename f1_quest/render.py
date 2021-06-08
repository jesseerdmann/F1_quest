import json
import os

from datetime import datetime
from f1_quest.answer_key import AnswerKey
from f1_quest.util import urlify_name
from jinja2 import Environment, FileSystemLoader


def table_to_series(ak, race_list, results_table):
    series_list = []
    min_y = 1000
    max_y = 0
    for entry in results_table:
        entry_obj = {'name': entry, 'values': [], 'color': ak.entries.entries[entry].color}
        for race in race_list:
            entry_obj['values'].append({'race': race, 'points': results_table[entry][race]})
            if results_table[entry][race] < min_y:
                min_y = results_table[entry][race]
            if results_table[entry][race] > max_y:
                max_y = results_table[entry][race]
        series_list.append(entry_obj)
    return (min_y, max_y, series_list)


def render_static_pages(base_url="https://jesseerdmann.github.io/F1_quest", 
    data_dir='data', datetime=datetime.now(), output_dir='docs'):
    ak = AnswerKey(datetime=datetime, data_dir=data_dir)
    file_loader = FileSystemLoader('f1_quest/templates')
    env = Environment(loader=file_loader)
    race_list = [race.name for race in ak.races.list_races_before(datetime)]

    index = env.get_template('index.html')
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    if not os.path.isdir(output_dir):
        raise Exception(f"{output_dir} is not a directory")
    results_table = {}
    results_table_path = os.path.join(data_dir, 'overall_results_table.json')
    if os.path.exists(results_table_path):
        results_table_pointer = open(results_table_path, 'r')
        results_table = json.loads(results_table_pointer.read())
    curr_race = ak.races.list_races_before(datetime)[-1]
    for subject in ak.get_overall_standings().get_ordered_subjects():
        if str(subject.subject) not in results_table:
            results_table[str(subject.subject)] = {}
        results_table[str(subject.subject)][curr_race.name] = subject.score
    with open(results_table_path, 'w') as results_table_out:
        results_table_out.write(json.dumps(results_table))
    (min_y, max_y, series_list) = table_to_series(ak, race_list, results_table)
    with open(os.path.join(output_dir, 'index.html'), 'w') as out:
        out.write(index.render(overall_table=ak.get_overall_standings(), 
            base_url=base_url, questions=ak.questions,
            entries=ak.entries, drivers=ak.drivers,
            races=ak.races, teams=ak.teams, race_list=json.dumps(race_list), 
            series_list=json.dumps(series_list), 
            results_table=json.dumps(results_table), min_y=min_y, max_y=max_y))
    

    result = env.get_template('result.html')
    output_subdir = os.path.join(output_dir, "results")
    if not os.path.exists(output_subdir):
        os.makedirs(output_subdir)
    if not os.path.isdir(output_subdir):
        raise Exception(f"{output_subdir} is not a directory")
    for question in ak.questions:
        results_table = question.write_results_table()
        (min_y, max_y, series_list) = table_to_series(ak, race_list, results_table)
        with open(os.path.join(output_subdir, 
            f"{urlify_name(question.short_name)}.html"), 'w') as out:
            out.write(result.render(question=question, 
                base_url=base_url, questions=ak.questions,
                entries=ak.entries, drivers=ak.drivers,
                races=ak.races, teams=ak.teams, race_list=json.dumps(race_list), 
                series_list=json.dumps(series_list), 
                results_table=json.dumps(results_table), min_y=min_y, 
                max_y=max_y))

    entry_template = env.get_template('entry.html')
    output_subdir = os.path.join(output_dir, "entries")
    if not os.path.exists(output_subdir):
        os.makedirs(output_subdir)
    if not os.path.isdir(output_subdir):
        raise Exception(f"{output_subdir} is not a directory")
    for entry in ak.entries.list_entries():
        with open(os.path.join(output_dir, "entries", 
            f"{urlify_name(entry.entry_name)}.html"), 'w') as out:
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
            f"{urlify_name(str(driver))}.html"), 'w') as out:
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
            f"{urlify_name(team.name)}.html"), 'w') as out:
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
            f"{urlify_name(str(race))}.html"), 'w') as out:
            out.write(race_template.render(race=race, 
                base_url=base_url, questions=ak.questions,
                entries=ak.entries, drivers=ak.drivers,
                races=ak.races, teams=ak.teams))