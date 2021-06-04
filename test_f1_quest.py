import os
import shutil

from datetime import datetime
from f1_quest.answer_key import AnswerKey
from f1_quest.drivers import Driver, Drivers
from f1_quest.entries import Entries
from f1_quest.races import Races
from f1_quest.render import render_static_pages
from f1_quest.tables import Table
from f1_quest.teams import Teams


def test_tables():
    table = Table('Test Table', 'Entry', 'Score', int, sort='ascending')
    table.add_subject(1, 'One')
    table.add_subject(2, 'Two')
    table.add_subject(3, 'Three')
    ordered_list = table.get_ordered_subjects()
    assert(ordered_list[0].score == 1)

    three = table.get_position_of_subject('Three')
    assert(three == 3)

    two = table.get_subjects_by_pos(2)
    assert(two[0].subject == 'Two')


def test_teams():
    teams = Teams(data_dir='test_data')
    assert(len(teams.list_all_teams()) == 10)
    williams = teams.get_team_by_name('Williams')
    assert(williams.name == 'Williams')


def test_drivers():
    drivers = Drivers(data_dir='test_data')
    assert(len(drivers.driver_list) == 20)

    alonso = drivers.get_driver_by_name(last_name="Alonso")
    assert(len(alonso) == 1)
    assert(alonso[0].first_name == 'Fernando')

    lewis = drivers.get_driver_by_short_name("Hamilton, Lewis")
    assert(lewis.first_name == 'Lewis')

    williams = drivers.get_driver_by_name(team_name="Williams")
    assert(len(williams) >= 2)
    latifi_found = False
    russell_found = False
    for williams_driver in williams:
        if williams_driver.last_name == 'Latifi':
            latifi_found = True
        if williams_driver.last_name == 'Russell':
            russell_found = True
    assert(latifi_found and russell_found)

    team_names = drivers.list_teams()
    assert('Williams' in team_names)
    assert(len(team_names) == 10)

    drivers.driver_list.append(Driver(first_name="Jesse", last_name="Erdmann", team_name="Erdxotic Racing", started_season="no"))
    assert(len(drivers.list_all_drivers()) == 21)
    assert(len(drivers.list_drivers_that_started_season()) == 20)


def test_races():
    races = Races(data_dir='test_data')
    assert(len(races.list_races()) == 23)
    assert(len(races.list_races_before(datetime.strptime("05/01/2021", "%m/%d/%Y"))) == 2)
    assert(len(races.list_races_after(datetime.strptime("10/01/2021", "%m/%d/%Y"))) == 8)

    no_race = races.get_race_by_date(datetime.strptime("05/01/2021", "%m/%d/%Y"))
    assert(no_race is None)

    fourth_of_july = races.get_race_by_date(datetime.strptime("07/04/2021", "%m/%d/%Y"))
    assert(fourth_of_july.name == 'Austria')
    assert(fourth_of_july.laps == 100)

    bahrain = races.get_race_by_name('Bahrain')
    assert(bahrain.name == 'Bahrain')
    assert(bahrain.laps == 100)


def test_first_race():
    teams = Teams(data_dir='test_data')
    drivers = Drivers(data_dir='test_data')
    races = Races(data_dir='test_data')
    after_one_race_date = datetime.strptime("04/01/2021", "%m/%d/%Y")
    races.read_results(data_dir='test_data', drivers=drivers, teams=teams, 
        datetime=after_one_race_date)

    bahrain = races.get_race_by_name('Bahrain')
    assert(bahrain.retirements == 5)
    assert(bahrain.safety_cars == 3)

    team_standings = teams.get_points_table()
    pos_4 = team_standings.get_subjects_by_pos(4, single_subject_only=True)
    assert(pos_4.score == 12)
    assert(pos_4.subject.name == "AlphaTauri")

    avg_points_standings = teams.get_average_point_change_table()
    pos_1 = avg_points_standings.get_subjects_by_pos(1, single_subject_only=True)
    assert(pos_1.score == 9.235294117647058)
    assert(pos_1.subject.name == "Red Bull Racing")

    driver_standings = drivers.get_points_table()
    pos_10 = driver_standings.get_subjects_by_pos(10, single_subject_only=True)
    assert(pos_10.score == 1)
    assert(pos_10.subject.name == "Giovinazzi, Antonio")
    
    lewis = drivers.get_driver_by_short_name("Hamilton, Lewis")
    lewis_pos = driver_standings.get_position_of_subject(lewis)
    assert(lewis_pos == 1)

    driver_dis_standings = drivers.get_dis_points_table()
    pos_1 = driver_dis_standings.get_subjects_by_pos(1)
    assert(pos_1[0].score == 0)
    assert(len(pos_1) == 20)

    driver_avg_laps = drivers.get_avg_laps_table()
    pos_1 = driver_avg_laps.get_subjects_by_pos(1)
    assert(pos_1[0].score == 50.0)
    assert(len(pos_1) == 5)

    driver_podiums = drivers.get_podiums_table()
    pos_1 = driver_podiums.get_subjects_by_pos(1)
    assert(pos_1[0].score == 1)
    assert(len(pos_1) == 3)

    driver_wins = drivers.get_winners_table()
    pos_1 = driver_wins.get_subjects_by_pos(1)
    assert(pos_1[0].score == 1)
    assert(pos_1[0].subject.last_name == 'Hamilton')
    assert(len(pos_1) == 1)

    driver_qualy_win_pct = teams.get_teammate_qualy_table()
    pos_1 = driver_qualy_win_pct.get_subjects_by_pos(1)
    assert(pos_1[0].score == 1.0)
    assert(len(pos_1) == 10)

    
def test_seventh_race():
    teams = Teams(data_dir='test_data')
    drivers = Drivers(data_dir='test_data')
    races = Races(data_dir='test_data')
    after_seven_races_date = datetime.strptime("06/14/2021", "%m/%d/%Y")
    races.read_results(data_dir='test_data', drivers=drivers, teams=teams, 
        datetime=after_seven_races_date)

    team_standings = teams.get_points_table()
    pos_4 = team_standings.get_subjects_by_pos(4, single_subject_only=True)
    assert(pos_4.score == 73)
    assert(pos_4.subject.name == "Ferrari")

    avg_points_standings = teams.get_average_point_change_table()
    pos_1 = avg_points_standings.get_subjects_by_pos(1, single_subject_only=True)
    assert(pos_1.score == 7.521008403361343)
    assert(pos_1.subject.name == "Red Bull Racing")
    
    driver_standings = drivers.get_points_table()
    assert(driver_standings.get_subjects_by_pos(10, 
        single_subject_only=True).score == 25)
    assert(driver_standings.get_subjects_by_pos(10, 
        single_subject_only=True).subject.name == "Stroll, Lance")
    
    lewis = drivers.get_driver_by_short_name("Hamilton, Lewis")
    lewis_pos = driver_standings.get_position_of_subject(lewis)
    assert(lewis_pos == 1)

    driver_dis_standings = drivers.get_dis_points_table()
    pos_1 = driver_dis_standings.get_subjects_by_pos(1)
    assert(pos_1[0].score == 2)
    assert(len(pos_1) == 2)

    driver_avg_laps = drivers.get_avg_laps_table()
    pos_1 = driver_avg_laps.get_subjects_by_pos(1)
    assert(pos_1[0].score == 63.714285714285715)
    assert(len(pos_1) == 1)
    assert(pos_1[0].subject.name == 'Raikkonen, Kimi')

    driver_podiums = drivers.get_podiums_table()
    pos_1 = driver_podiums.get_subjects_by_pos(1)
    assert(pos_1[0].score == 7)
    assert(len(pos_1) == 1)
    assert(pos_1[0].subject.name == 'Hamilton, Lewis')

    driver_wins = drivers.get_winners_table()
    pos_1 = driver_wins.get_subjects_by_pos(1)
    assert(pos_1[0].score == 4)
    assert(pos_1[0].subject.last_name == 'Hamilton')
    assert(len(pos_1) == 1)

    driver_qualy_win_pct = teams.get_teammate_qualy_table()
    pos_1 = driver_qualy_win_pct.get_subjects_by_pos(1)
    assert(pos_1[0].score == 1.0)
    assert(len(pos_1) == 1)
    assert(pos_1[0].subject.name == 'Russell, George')

    
def test_final_race():
    teams = Teams(data_dir='test_data')
    drivers = Drivers(data_dir='test_data')
    races = Races(data_dir='test_data')
    after_all_races_date = datetime.strptime("12/13/2021", "%m/%d/%Y")
    races.read_results(data_dir='test_data', drivers=drivers, teams=teams, 
        datetime=after_all_races_date)

    team_standings = teams.get_points_table()
    pos_4 = team_standings.get_subjects_by_pos(4, single_subject_only=True)
    assert(pos_4.score == 230)
    assert(pos_4.subject.name == "McLaren")

    avg_points_standings = teams.get_average_point_change_table()
    pos_1 = avg_points_standings.get_subjects_by_pos(1, single_subject_only=True)
    assert(pos_1.score == 7.843989769820972)
    assert(pos_1.subject.name == "Red Bull Racing")

    driver_standings = drivers.get_points_table()
    assert(driver_standings.get_subjects_by_pos(10, 
        single_subject_only=True).score == 89)
    assert(driver_standings.get_subjects_by_pos(10, 
        single_subject_only=True).subject.name == "Norris, Lando")
    
    lewis = drivers.get_driver_by_short_name("Hamilton, Lewis")
    lewis_pos = driver_standings.get_position_of_subject(lewis)
    assert(lewis_pos == 1)

    driver_dis_standings = drivers.get_dis_points_table()
    pos_1 = driver_dis_standings.get_subjects_by_pos(1)
    assert(pos_1[0].score == 6)
    assert(len(pos_1) == 1)
    assert(pos_1[0].subject.name == "Mazepin, Nikita")

    driver_avg_laps = drivers.get_avg_laps_table()
    pos_1 = driver_avg_laps.get_subjects_by_pos(1)
    assert(pos_1[0].score == 66.73913043478261)
    assert(len(pos_1) == 1)
    assert(pos_1[0].subject.name == 'Raikkonen, Kimi')

    driver_podiums = drivers.get_podiums_table()
    pos_1 = driver_podiums.get_subjects_by_pos(1)
    assert(pos_1[0].score == 21)
    assert(len(pos_1) == 1)
    assert(pos_1[0].subject.name == 'Hamilton, Lewis')

    driver_wins = drivers.get_winners_table()
    pos_1 = driver_wins.get_subjects_by_pos(1)
    assert(pos_1[0].score == 12)
    assert(pos_1[0].subject.last_name == 'Hamilton')
    assert(len(pos_1) == 1)

    driver_qualy_win_pct = teams.get_teammate_qualy_table()
    pos_1 = driver_qualy_win_pct.get_subjects_by_pos(1)
    assert(pos_1[0].score == 0.9565217391304348)
    assert(len(pos_1) == 1)
    assert(pos_1[0].subject.name == 'Russell, George')

def test_answer_key():
    after_one_race_date = datetime.strptime("04/01/2021", "%m/%d/%Y")
    ak = AnswerKey(data_dir='test_data', datetime=after_one_race_date)
    
    answer, score = ak.team_fourth()
    fourth_team = answer.get_subjects_by_pos(4)
    assert(len(fourth_team) == 1)
    assert(fourth_team[0].subject.name == 'AlphaTauri')
    assert(fourth_team[0].score == 12)
    leader = score.get_subjects_by_pos(1)
    assert(len(leader) == 1)
    assert(leader[0].subject.entry_name == 'Douglas')
    assert(leader[0].score == 25)
    
    answer, score = ak.avg_points_increase()
    fifth_team = answer.get_subjects_by_pos(5)
    assert(len(fifth_team) == 1)
    assert(fifth_team[0].subject.name == 'Williams')
    assert(fifth_team[0].score == 2.0)
    assert(fifth_team[0].value == 10)
    assert(len(fifth_team[0].matching_entries) == 1)
    assert(fifth_team[0].matching_entries[0].entry_name == 'Moksha Gren')
    
    answer, score = ak.driver_of_the_day()
    second_pos = answer.get_subjects_by_pos(2)
    assert(len(second_pos) == 19)
    first_pos = answer.get_subjects_by_pos(1)
    assert(len(first_pos) == 1)
    assert(first_pos[0].subject.entry_rep == 'Charles LeClerc, Ferrari')
    assert(first_pos[0].score == 1)
    assert(first_pos[0].value == 25)
    assert(len(first_pos[0].matching_entries) == 0)
    
    answer, score = ak.driver_tenth()
    tenth_driver = answer.get_subjects_by_pos(10)
    assert(len(tenth_driver) == 1)
    assert(tenth_driver[0].subject.entry_rep == 'Antonio Giovinazzi, Alfa Romeo Racing')
    assert(tenth_driver[0].score == 1)
    assert(len(tenth_driver[0].matching_entries) == 1)
    assert(tenth_driver[0].matching_entries[0].entry_name == 'Jameson')

    answer, score = ak.teammate_qualy()
    first_pos = answer.get_subjects_by_pos(1)
    eleventh_pos = answer.get_subjects_by_pos(11)
    assert(len(first_pos) == 10)
    assert(len(eleventh_pos) == 10)
    assert(first_pos[0].score == 1.0)
    assert(first_pos[0].value == 25)
    assert(eleventh_pos[0].score == 0.0)
    assert(eleventh_pos[0].value == 0)

    answer, score = ak.podium_winners()
    first_pos = answer.get_subjects_by_pos(1)
    fourth_pos = answer.get_subjects_by_pos(4)
    assert(len(first_pos) == 3)
    assert(len(fourth_pos) == 17)
    assert(first_pos[0].score == 1)
    assert(first_pos[0].value == 5)
    assert(len(first_pos[0].matching_entries) == 9)
    assert(fourth_pos[0].score == 0)
    assert(fourth_pos[0].value == -3)
    top_score = score.get_subjects_by_pos(1)
    assert(len(top_score) == 1)
    assert(top_score[0].subject.entry_name == 'Stephen')
    assert(top_score[0].score == 15)
    
    answer, score = ak.dis_points()
    first_pos = answer.get_subjects_by_pos(1)
    assert(len(first_pos) == 20)
    assert(first_pos[0].score == 0)
    assert(first_pos[0].value == 25)
    
    answer, score = ak.avg_laps()
    first_pos = answer.get_subjects_by_pos(1)
    sixth_pos = answer.get_subjects_by_pos(6)
    assert(len(first_pos) == 5)
    assert(first_pos[0].score == 50.0)
    assert(first_pos[0].value == 25)
    assert(len(sixth_pos) == 5)
    assert(sixth_pos[0].score == 98.0)
    assert(sixth_pos[0].value == 8)

    answer, score = ak.six_after_six()
    third_pos = score.get_subjects_by_pos(3)
    assert(len(third_pos) == 1)
    assert(third_pos[0].score == 15)
    assert(third_pos[0].subject.entry_name == 'David')

    answer, score = ak.uninterrupted_leader()
    first_pos = score.get_subjects_by_pos(1)
    assert(len(first_pos) == 1)
    assert(first_pos[0].subject.entry_name == 'David')
    assert(first_pos[0].score == 25)

    answer, score = ak.retirements()
    first_pos = answer.get_subjects_by_pos(1)
    assert(len(first_pos) == 1)
    assert(first_pos[0].score == 5)
    assert(first_pos[0].value == -25)
    assert(str(first_pos[0].subject) == '03/28/2021 10:00 AM: Bahrain @ Bahrain International Circuit')
    assert(len(first_pos[0].matching_entries) == 1)
    assert(first_pos[0].matching_entries[0].entry_name == 'Douglas')

    answer, score = ak.gasly_points()
    first_pos = answer.get_subjects_by_pos(1)
    assert(len(first_pos) == 1)
    assert(first_pos[0].score == 12)
    assert(str(first_pos[0].subject) == '03/28/2021 10:00 AM: Bahrain @ Bahrain International Circuit')

    answer, score = ak.stroll_points()
    first_pos = answer.get_subjects_by_pos(1)
    assert(len(first_pos) == 23)
    assert(first_pos[0].score == 0)

    answer, score = ak.mazepin_points()
    first_pos = answer.get_subjects_by_pos(1)
    assert(len(first_pos) == 23)
    assert(first_pos[0].score == 0)

    answer, score = ak.bottom_seven()
    first_pos = answer.get_subjects_by_pos(1)
    assert(len(first_pos) == 1)
    assert(first_pos[0].subject.entry_rep == 'Pierre Gasly, AlphaTauri')
    assert(first_pos[0].score == 12)
    first_pos = score.get_subjects_by_pos(1)
    assert(len(first_pos) == 1)
    assert(first_pos[0].subject.entry_name == 'Jameson')
    assert(first_pos[0].score == 25)

    answer, score = ak.safety_cars()
    first_pos = answer.get_subjects_by_pos(1)
    assert(len(first_pos) == 1)
    assert(first_pos[0].score == 3)
    assert(str(first_pos[0].subject) == '03/28/2021 10:00 AM: Bahrain @ Bahrain International Circuit')

    answer, score = ak.fewest_on_lead_lap()
    first_pos = score.get_subjects_by_pos(1)
    assert(len(first_pos) == 1)
    assert(first_pos[0].subject.entry_name == 'Stephen')
    assert(first_pos[0].score == 25)
    assert(first_pos[0].value == 6)

    answer, score = ak.russia_facts()
    first_pos = score.get_subjects_by_pos(1)
    assert(len(first_pos) == 1)
    assert(first_pos[0].subject.entry_name == 'Jesse')
    assert(first_pos[0].score == 25)
    assert(first_pos[0].value == 5)

    answer, score = ak.first_saudi_retirement()
    assert(answer is None)
    assert(score is None)

    answer_value, score = ak.unique_race_winners()
    assert(answer_value == 1)
    
    answer_value, score = ak.unique_pole_sitters()
    assert(answer_value == 1)
    
    answer_value, score = ak.unique_fastest_lap()
    assert(answer_value == 1)

    answer_value, score = ak.wet_compound_races()
    assert(answer_value == 3)

    answer_value, score = ak.in_season_leavings()
    assert(answer_value == 5)

    answer_value, score = ak.track_invasions()
    assert(answer_value == 1)

    answer_value, score = ak.total_drivers()
    assert(answer_value == 20)

    answer, score = ak.by_the_numbers()
    first_pos = score.get_subjects_by_pos(1)
    assert(len(first_pos) == 1)
    assert(first_pos[0].subject.entry_name == 'Douglas')
    assert(first_pos[0].score == 25)
    assert(first_pos[0].value == 17)

    score = ak.pourchaire_seat()
    ninth_pos = score.get_subjects_by_pos(9)
    assert(len(ninth_pos) == 1)
    assert(ninth_pos[0].subject.entry_name == 'Moksha Gren')
    assert(ninth_pos[0].score == 'TRUE')
    assert(ninth_pos[0].value == 5)

    score = ak.lando_gets_a_podium()
    first_pos = score.get_subjects_by_pos(1)
    assert(len(first_pos) == 2)
    assert(first_pos[0].score == 'FALSE')
    assert(first_pos[0].value == 1)

    score = ak.williams_above_tenth()
    first_pos = score.get_subjects_by_pos(1)
    assert(len(first_pos) == 1)
    assert(first_pos[0].subject.entry_name == 'Jameson')
    assert(first_pos[0].score == 'FALSE')
    assert(first_pos[0].value == -3)

    score = ak.red_bull_driver_change()
    ninth_pos = score.get_subjects_by_pos(9)
    assert(len(ninth_pos) == 1)
    assert(ninth_pos[0].subject.entry_name == 'Douglas')
    assert(ninth_pos[0].score == 'TRUE')
    assert(ninth_pos[0].value == -3)

    score = ak.all_20_finished()
    first_pos = score.get_subjects_by_pos(1)
    assert(len(first_pos) == 4)
    assert(first_pos[0].score == 'FALSE')
    assert(first_pos[0].value == 1)

    score = ak.down_to_the_wire()
    ninth_pos = score.get_subjects_by_pos(9)
    assert(len(ninth_pos) == 1)
    assert(ninth_pos[0].subject.entry_name == 'Heidi')
    assert(ninth_pos[0].score == 'TRUE')
    assert(ninth_pos[0].value == 5)

    score = ak.russell_outscores_someone()
    first_pos = score.get_subjects_by_pos(1)
    assert(len(first_pos) == 1)
    assert(first_pos[0].subject.entry_name == 'Heidi')
    assert(first_pos[0].score == 'FALSE')
    assert(first_pos[0].value == -3)


def test_entries():
    entries = Entries(data_dir='test_data')
    assert(len(entries.entries) == 9)
    assert('Jesse' in entries.entries)
    jesse = entries.entries['Jesse']
    assert(jesse.bingo_russell_response == 'TRUE')
    assert('Max Verstappen, Red Bull Racing' in jesse.driver_podium_response)
    assert('Lando Norris, McLaren' in jesse.driver_podium_response)
    assert('Fernando Alonso, Alpine' in jesse.driver_podium_response)
    assert('07/04/2021 08:00 AM: Austria @ Red Bull Ring' in jesse.driver_race_retirements_response)
    assert('08/01/2021 08:00 AM: Hungary @ Hungaroring' in jesse.driver_race_retirements_response)
    assert('09/26/2021 07:00 AM: Russia @ Sochi Autodrom' in jesse.driver_race_retirements_response)
    assert('08/29/2021 09:00 AM: Belgium @ Circuit de Spa-Francorchamps' in jesse.driver_gasly_points_response)
    assert('Fernando Alonso, Alpine' in jesse.driver_pick_two_response)
    assert('Charles LeClerc, Ferrari' in jesse.driver_pick_two_response)


def test_render():
    after_one_race_date = datetime.strptime("04/01/2021", "%m/%d/%Y")
    render_static_pages(output_dir="test_data/out", data_dir="test_data/", datetime=after_one_race_date)
    assert(os.path.isdir("test_data/out"))
    assert(os.path.isfile("test_data/out/index.html"))
    assert(os.path.isdir("test_data/out/drivers"))
    assert(os.path.isdir("test_data/out/entries"))
    assert(os.path.isdir("test_data/out/races"))
    assert(os.path.isdir("test_data/out/results"))
    assert(os.path.isdir("test_data/out/teams"))
    assert(os.path.isfile("test_data/out/drivers/Carlos_Sainz_Ferrari.html"))
    shutil.rmtree("test_data/out")