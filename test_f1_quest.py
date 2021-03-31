from datetime import datetime
from f1_quest.answer_key import AnswerKey
from f1_quest.drivers import Driver, Drivers
from f1_quest.entries import Entries
from f1_quest.races import Races
from f1_quest.tables import Table
from f1_quest.teams import Teams


def test_tables():
    table = Table('Test Table', 'Entry', 'Score', int, False)
    table.add_entry(1, 'One')
    table.add_entry(2, 'Two')
    table.add_entry(3, 'Three')
    ordered_list = table.get_ordered_entries()
    assert(ordered_list[0].score == 1)

    three = table.get_position_of_entry('Three')
    assert(three == 3)

    two = table.get_entries_by_pos(2)
    assert(two[0].entry == 'Two')


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
    assert(len(lewis) == 1)
    assert(lewis[0].first_name == 'Lewis')

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
    pos_4 = team_standings.get_entries_by_pos(4, single_entry_only=True)
    assert(pos_4.score == 12)
    assert(pos_4.entry.name == "AlphaTauri")

    avg_points_standings = teams.get_average_point_change_table()
    pos_1 = avg_points_standings.get_entries_by_pos(1, single_entry_only=True)
    assert(pos_1.score == 9.235294117647058)
    assert(pos_1.entry.name == "Red Bull Racing")

    driver_standings = drivers.get_points_table()
    pos_10 = driver_standings.get_entries_by_pos(10, single_entry_only=True)
    assert(pos_10.score == 1)
    assert(pos_10.entry.name == "Giovinazzi, Antonio")
    
    lewis = drivers.get_driver_by_short_name("Hamilton, Lewis")[0]
    lewis_pos = driver_standings.get_position_of_entry(lewis)
    assert(lewis_pos == 1)

    driver_dis_standings = drivers.get_dis_points_table()
    pos_1 = driver_dis_standings.get_entries_by_pos(1)
    assert(pos_1[0].score == 0)
    assert(len(pos_1) == 20)

    driver_avg_laps = drivers.get_avg_laps_table()
    pos_1 = driver_avg_laps.get_entries_by_pos(1)
    assert(pos_1[0].score == 50.0)
    assert(len(pos_1) == 5)

    driver_podiums = drivers.get_podiums_table()
    pos_1 = driver_podiums.get_entries_by_pos(1)
    assert(pos_1[0].score == 1)
    assert(len(pos_1) == 3)

    driver_wins = drivers.get_winners_table()
    pos_1 = driver_wins.get_entries_by_pos(1)
    assert(pos_1[0].score == 1)
    assert(pos_1[0].entry.last_name == 'Hamilton')
    assert(len(pos_1) == 1)

    driver_qualy_win_pct = teams.get_teammate_qualy_table()
    pos_1 = driver_qualy_win_pct.get_entries_by_pos(1)
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
    pos_4 = team_standings.get_entries_by_pos(4, single_entry_only=True)
    assert(pos_4.score == 73)
    assert(pos_4.entry.name == "Ferrari")

    avg_points_standings = teams.get_average_point_change_table()
    pos_1 = avg_points_standings.get_entries_by_pos(1, single_entry_only=True)
    assert(pos_1.score == 7.521008403361343)
    assert(pos_1.entry.name == "Red Bull Racing")
    
    driver_standings = drivers.get_points_table()
    assert(driver_standings.get_entries_by_pos(10, 
        single_entry_only=True).score == 25)
    assert(driver_standings.get_entries_by_pos(10, 
        single_entry_only=True).entry.name == "Stroll, Lance")
    
    lewis = drivers.get_driver_by_short_name("Hamilton, Lewis")[0]
    lewis_pos = driver_standings.get_position_of_entry(lewis)
    assert(lewis_pos == 1)

    driver_dis_standings = drivers.get_dis_points_table()
    pos_1 = driver_dis_standings.get_entries_by_pos(1)
    assert(pos_1[0].score == 2)
    assert(len(pos_1) == 2)

    driver_avg_laps = drivers.get_avg_laps_table()
    pos_1 = driver_avg_laps.get_entries_by_pos(1)
    assert(pos_1[0].score == 63.714285714285715)
    assert(len(pos_1) == 1)
    assert(pos_1[0].entry.name == 'Raikkonen, Kimi')

    driver_podiums = drivers.get_podiums_table()
    pos_1 = driver_podiums.get_entries_by_pos(1)
    assert(pos_1[0].score == 7)
    assert(len(pos_1) == 1)
    assert(pos_1[0].entry.name == 'Hamilton, Lewis')

    driver_wins = drivers.get_winners_table()
    pos_1 = driver_wins.get_entries_by_pos(1)
    assert(pos_1[0].score == 4)
    assert(pos_1[0].entry.last_name == 'Hamilton')
    assert(len(pos_1) == 1)

    driver_qualy_win_pct = teams.get_teammate_qualy_table()
    pos_1 = driver_qualy_win_pct.get_entries_by_pos(1)
    assert(pos_1[0].score == 1.0)
    assert(len(pos_1) == 1)
    assert(pos_1[0].entry.name == 'Russell, George')

    
def test_final_race():
    teams = Teams(data_dir='test_data')
    drivers = Drivers(data_dir='test_data')
    races = Races(data_dir='test_data')
    after_all_races_date = datetime.strptime("12/13/2021", "%m/%d/%Y")
    races.read_results(data_dir='test_data', drivers=drivers, teams=teams, 
        datetime=after_all_races_date)

    team_standings = teams.get_points_table()
    pos_4 = team_standings.get_entries_by_pos(4, single_entry_only=True)
    assert(pos_4.score == 230)
    assert(pos_4.entry.name == "McLaren")

    avg_points_standings = teams.get_average_point_change_table()
    pos_1 = avg_points_standings.get_entries_by_pos(1, single_entry_only=True)
    assert(pos_1.score == 7.843989769820972)
    assert(pos_1.entry.name == "Red Bull Racing")

    driver_standings = drivers.get_points_table()
    assert(driver_standings.get_entries_by_pos(10, 
        single_entry_only=True).score == 89)
    assert(driver_standings.get_entries_by_pos(10, 
        single_entry_only=True).entry.name == "Norris, Lando")
    
    lewis = drivers.get_driver_by_short_name("Hamilton, Lewis")[0]
    lewis_pos = driver_standings.get_position_of_entry(lewis)
    assert(lewis_pos == 1)

    driver_dis_standings = drivers.get_dis_points_table()
    pos_1 = driver_dis_standings.get_entries_by_pos(1)
    assert(pos_1[0].score == 6)
    assert(len(pos_1) == 1)
    assert(pos_1[0].entry.name == "Mazepin, Nikita")

    driver_avg_laps = drivers.get_avg_laps_table()
    pos_1 = driver_avg_laps.get_entries_by_pos(1)
    assert(pos_1[0].score == 66.73913043478261)
    assert(len(pos_1) == 1)
    assert(pos_1[0].entry.name == 'Raikkonen, Kimi')

    driver_podiums = drivers.get_podiums_table()
    pos_1 = driver_podiums.get_entries_by_pos(1)
    assert(pos_1[0].score == 21)
    assert(len(pos_1) == 1)
    assert(pos_1[0].entry.name == 'Hamilton, Lewis')

    driver_wins = drivers.get_winners_table()
    pos_1 = driver_wins.get_entries_by_pos(1)
    assert(pos_1[0].score == 12)
    assert(pos_1[0].entry.last_name == 'Hamilton')
    assert(len(pos_1) == 1)

    driver_qualy_win_pct = teams.get_teammate_qualy_table()
    pos_1 = driver_qualy_win_pct.get_entries_by_pos(1)
    assert(pos_1[0].score == 0.9565217391304348)
    assert(len(pos_1) == 1)
    assert(pos_1[0].entry.name == 'Russell, George')

def test_answer_key():
    after_one_race_date = datetime.strptime("04/01/2021", "%m/%d/%Y")
    ak = AnswerKey(data_dir='test_data', datetime=after_one_race_date)
    
    team_fourth, tie_breaker = ak.team_fourth()
    assert(team_fourth['AlphaTauri'] == 25)
    assert(team_fourth['Aston Martin'] == 10)
    assert(team_fourth['Alpine'] == 10)
    assert(tie_breaker == 12)
    
    avg_points_increase, tie_breaker = ak.avg_points_increase()
    assert(avg_points_increase['AlphaTauri'] == 12)
    assert(avg_points_increase['Mercedes'] == 18)
    assert(tie_breaker is None)
    
    driver_of_the_day, tie_breaker = ak.driver_of_the_day()
    assert(driver_of_the_day['LeClerc, Charles'] == 25)
    assert(driver_of_the_day['Gasly, Pierre'] == 18)
    assert(driver_of_the_day['Alonso, Fernando'] == 18)
    assert(tie_breaker is None)
    
    driver_tenth, tie_breaker = ak.driver_tenth()
    assert(driver_tenth['LeClerc, Charles'] == 12)
    assert(driver_tenth['Russell, George'] == 18)
    assert(driver_tenth['Alonso, Fernando'] == 18)
    assert(tie_breaker == 1)

    teammate_qualy, tie_breaker = ak.teammate_qualy()
    assert(teammate_qualy['Alonso, Fernando'] == 25)
    assert(teammate_qualy['LeClerc, Charles'] == 25)
    assert(teammate_qualy['Russell, George'] == 25)
    assert(tie_breaker is None)

    podium_winners = ak.podium_winners()
    assert('Bottas, Veltteri' in podium_winners)
    assert('Russell, George' not in podium_winners)
    
    dis_points, tie_breaker = ak.dis_points()
    assert(dis_points['LeClerc, Charles'] == 25)
    assert(dis_points['Gasly, Pierre'] == 25)
    assert(dis_points['Alonso, Fernando'] == 25)
    assert(tie_breaker is None)
    
    avg_laps, tie_breaker = ak.avg_laps()
    assert(avg_laps['LeClerc, Charles'] == 0)
    assert(avg_laps['Gasly, Pierre'] == 0)
    assert(avg_laps['Alonso, Fernando'] == 25)
    assert(tie_breaker is None)

    six_after_six = ak.six_after_six()
    pos_3 = six_after_six.get_entries_by_pos(3, single_entry_only=True)
    assert(pos_3.score == 16)
    assert(pos_3.entry.name == "Bottas, Veltteri")

    unbroken_first, unbroken_second = ak.uninterrupted_leader()
    assert(unbroken_first['06/06/2021 07:00 AM: Azerbaijan @ Baku City Circuit'] == 8)
    assert(unbroken_second['07/18/2021 09:00 AM: Great Britain @ Silverstone Circuit'] == 1)

    retirements = ak.retirements()
    assert(retirements['03/28/2021 10:00 AM: Bahrain @ Bahrain International Circuit'] == -25)
    assert(retirements['10/24/2021 02:00 PM: United States @ Circuit of The Americas'] == 0)

    gasly_points = ak.gasly_points()
    assert(gasly_points['03/28/2021 10:00 AM: Bahrain @ Bahrain International Circuit'] == 12)
    assert('10/24/2021 02:00 PM: United States @ Circuit of The Americas' not in gasly_points)

    stroll_points = ak.stroll_points()
    assert(stroll_points['03/28/2021 10:00 AM: Bahrain @ Bahrain International Circuit'] == 0)
    assert('10/24/2021 02:00 PM: United States @ Circuit of The Americas' not in stroll_points)

    mazepin_points = ak.mazepin_points()
    assert(mazepin_points['03/28/2021 10:00 AM: Bahrain @ Bahrain International Circuit'] == 0)
    assert('10/24/2021 02:00 PM: United States @ Circuit of The Americas' not in mazepin_points)

    bottom_seven = ak.bottom_seven()
    assert(bottom_seven['Gasly, Pierre'] == 12)
    assert(bottom_seven['Latifi, Nicholas'] == 0)
    assert('Hamilton, Lewis' not in bottom_seven)

    safety_cars, tie_breaker = ak.safety_cars()
    assert(tie_breaker['03/28/2021 10:00 AM: Bahrain @ Bahrain International Circuit'] == 3)
    assert(tie_breaker['09/05/2021 08:00 AM: Netherlands @ Circuit Zandvoort'] == 0)
    assert(safety_cars == 3)
    assert('03/28/2021 10:00 AM: Bahrain @ Bahrain International Circuit' in tie_breaker)

    fewest_on_lead_lap = ak.fewest_on_lead_lap()
    assert(fewest_on_lead_lap == 6)

    softs_in_russia, tie_breaker = ak.russia_facts()
    assert(softs_in_russia == 5)
    assert(tie_breaker == 25)

    saudi_retirement = ak.first_saudi_retirement()
    assert(saudi_retirement[0] is None)
    assert(saudi_retirement[1] is None)

    num_winners = ak.unique_race_winners()
    assert(num_winners == 1)
    
    num_pole_sitters = ak.unique_pole_sitters()
    assert(num_pole_sitters == 1)
    
    num_fastest_lap_winners = ak.unique_fastest_lap()
    assert(num_fastest_lap_winners == 1)

    num_wet_compounds_used = ak.wet_compound_races()
    assert(num_wet_compounds_used == 3)

    in_season_leavings = ak.in_season_leavings()
    assert(in_season_leavings == 5)

    track_invasions = ak.track_invasions()
    assert(track_invasions == 1)

    total_drivers = ak.total_drivers()
    assert(total_drivers == 20)

    pourchaire_seat = ak.pourchaire_seat()
    assert(pourchaire_seat == 'TRUE')

    lando_podium = ak.lando_gets_a_podium()
    assert(lando_podium == 'FALSE')

    williams_above_tenth = ak.williams_above_tenth()
    assert(williams_above_tenth == 'TRUE')

    all_20_finished = ak.all_20_finished()
    assert(all_20_finished == 'FALSE')

    down_to_the_wire = ak.down_to_the_wire()
    assert(down_to_the_wire == 'TBD')


def test_entries():
    entries = Entries(data_dir='test_data')
    assert(len(entries.entries) == 9)
    assert('Jesse' in entries.entries)
    jesse = entries.entries['Jesse']
    assert(jesse.bingo_russell_response == 'TRUE')
