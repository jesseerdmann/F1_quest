import csv
import os

from datetime import datetime
from f1_quest.drivers import Driver, Drivers
from f1_quest.races import Races
from f1_quest.tables import Table
from f1_quest.teams import Teams


class AnswerKey():
    def __init__(self, data_dir='data', datetime=datetime.now(), 
        file_name='scoring_single_answer.csv'):
        self.teams = Teams(data_dir=data_dir)
        self.drivers = Drivers(data_dir=data_dir)
        self.races = Races(data_dir=data_dir)
        self.races.read_results(data_dir=data_dir, drivers=self.drivers, 
            teams=self.teams, datetime=datetime)
        self.datetime = datetime

        # Read scoring_single_answer.csv
        self.single_answer_dict = {}
        # These entries need to be read as strings
        int_answers = ["Pitted for Softs in last five laps at Russia", 
            "Total laps on softs for winner at Russia", 
            "How many races have wet compound used", 
            "How many drivers confirmed to leave",
            "How many races with animal invasions"]
        file_path = os.path.join(data_dir, file_name)
        if not os.path.exists(file_path):
            raise Exception(f"{file_path} not found, exiting.")
        with open(file_path, newline='') as file_pointer:
            file_reader = csv.reader(file_pointer, delimiter=',', quotechar='"')
            for row in file_reader:
                if row[0] in int_answers:
                    self.single_answer_dict[row[0]] = int(row[1])
                else:
                    self.single_answer_dict[row[0]] = row[1]


    def __str__(self):
        """
        This aggressively long method pulls together all of the questions and 
         answers as a string to be printed for aiding manual scoring of entries
        """
        strings = ['F1 Questionaire Answer Key', '']
        strings.append('Q1: Which team will finish fourth in the championship?')
        scoring, tie_breaker = self.team_fourth()
        strings.append("{:30s} {:5s}".format("Answer", "Value"))
        for team, value in scoring.items():
            strings.append("{:30s} {:5d}".format(team, value))
        strings.append('')
        strings.append('Tie Breaker: How many points will the fourth place team collect?')
        strings.append(str(tie_breaker))
        strings.append('')
        strings.append('Q2: Which team will have the highest points per race increase over 2020?')
        scoring, tie_breaker = self.avg_points_increase()
        strings.append("{:30s} {:5s}".format("Answer", "Value"))
        for team, value in scoring.items():
            strings.append("{:30s} {:5d}".format(team, value))
        strings.append('')
        strings.append('Q3: Which team will win the DHL Fastest Pit Stop?')
        strings.append('Everyone gets 25... good job!')
        strings.append('')
        strings.append('Q4: Who will win the most official "Driver of the Day" awards?')
        scoring, tie_breaker = self.driver_of_the_day()
        strings.append("{:30s} {:5s}".format("Answer", "Value"))
        for driver, value in scoring.items():
            strings.append("{:30s} {:5d}".format(driver, value))
        strings.append('')
        strings.append('Q5: Which driver will finish 10th in the Championship?')
        scoring, tie_breaker = self.driver_tenth()
        strings.append("{:30s} {:5s}".format("Answer", "Value"))
        for driver, value in scoring.items():
            strings.append("{:30s} {:5d}".format(driver, value))
        strings.append('')
        strings.append('Tie Breaker: How many points will that driver get?')
        strings.append(str(tie_breaker))
        strings.append('')
        strings.append('Q6: Which driver will be most dominant over their teammate in qualifying?')
        scoring, tie_breaker = self.teammate_qualy()
        strings.append("{:30s} {:5s}".format("Answer", "Value"))
        for driver, value in scoring.items():
            strings.append("{:30s} {:5d}".format(driver, value))
        strings.append('')
        strings.append('Q7: Check every driver that will have a podium finish during the season.')
        driver_podiums = self.podium_winners()
        strings.append('Drivers that won at least one podium:')
        for driver in driver_podiums:
            strings.append(driver)
        strings.append('')
        strings.append('Q8: Which driver will have the most penalty points?')
        scoring, tie_breaker = self.dis_points()
        strings.append("{:30s} {:5s}".format("Answer", "Value"))
        for driver, value in scoring.items():
            strings.append("{:30s} {:5d}".format(driver, value))
        strings.append('')
        strings.append('Q9: Which driver will have the lowest average race laps per race started?')
        scoring, tie_breaker = self.avg_laps()
        strings.append("{:30s} {:5s}".format("Answer", "Value"))
        for driver, value in scoring.items():
            strings.append("{:30s} {:5d}".format(driver, value))
        strings.append('')
        strings.append('Q10: Who will be the top six drivers after the first six races?')
        six_after_six_table = self.six_after_six()
        strings.append("Points table after six races:")
        strings.append(str(six_after_six_table))
        strings.append('')
        strings.append('Q11: At which race will the champion move to the top of the standings and never drop out of the top spot?')
        scoring, tie_breaker = self.uninterrupted_leader()
        strings.append("{:65s} {:5s}".format("Answer", "Value"))
        for race, value in scoring.items():
            strings.append("{:65s} {:5d}".format(race, value))
        strings.append('')
        strings.append('Tie Breaker: Same question but for second place')
        strings.append("{:65s} {:5s}".format("Answer", "Value"))
        for race, value in tie_breaker.items():
            strings.append("{:65s} {:5d}".format(race, value))
        strings.append('')
        strings.append('Q12: Pick three races, each retirement from the chosen races will cost you -5 points.')
        retirements = self.retirements()
        strings.append("{:65s} {:5s}".format("Answer", "Value"))
        for race, value in retirements.items():
            strings.append("{:65s} {:5d}".format(race, value))
        strings.append('')
        strings.append('Q13: Pick two races, get the points scored by Pierre Gasly for those races.')
        gasly_points = self.gasly_points()
        strings.append("{:65s} {:5s}".format("Answer", "Value"))
        for race, value in gasly_points.items():
            strings.append("{:65s} {:5d}".format(race, value))
        strings.append('')
        strings.append('Q14: Pick two races, get the points scored by Lance Stroll for those races.')
        stroll_points = self.stroll_points()
        strings.append("{:65s} {:5s}".format("Answer", "Value"))
        for race, value in stroll_points.items():
            strings.append("{:65s} {:5d}".format(race, value))
        strings.append('')
        strings.append('Q15: Pick two races, SUBTRACT Nikita Mazepin\'s points for those races')
        mazepin_points = self.mazepin_points()
        strings.append("{:65s} {:5s}".format("Answer", "Value"))
        for race, value in mazepin_points.items():
            strings.append("{:65s} {:5d}".format(race, value))
        strings.append('')
        strings.append('Q16: Pick two drivers who are not currently teammates from the bottom seven teams in 2020.')
        bottom_seven = self.bottom_seven()
        strings.append("{:65s} {:5s}".format("Answer", "Value"))
        for race, value in bottom_seven.items():
            strings.append("{:65s} {:5d}".format(race, value))
        strings.append('')
        strings.append('Q17: How many safety and virtual safety cars will be called in 2021?')
        scoring, tie_breaker = self.safety_cars()
        strings.append('Tie breaker: Which race will have the most safety cars of all types?')
        strings.append(str(scoring))
        strings.append("{:65s} {:5s}".format("Answer", "Value"))
        for driver, value in tie_breaker.items():
            strings.append("{:65s} {:5d}".format(driver, value))
        strings.append('')
        strings.append('Q18: What is the fewest number of drivers that will finish on the lead lap of any race?')
        strings.append(str(self.fewest_on_lead_lap()))
        strings.append('')
        strings.append('Q19: How many drivers will take on soft tires in the last 5 laps in Russia')
        scoring, tie_breaker = self.russia_facts()
        strings.append(str(scoring))
        strings.append('Tie breaker: What will be the total number of laps run on softs by the race winner in Russia?')
        strings.append(str(tie_breaker))
        strings.append('')
        strings.append('Q20: Which driver that starts the race in Saudi Arabia will be the first one out?')
        scoring, tie_breaker = self.first_saudi_retirement()
        strings.append(str(scoring))
        strings.append('Tie breaker: What WDC position will that driver start the race in?')
        strings.append(str(tie_breaker))
        strings.append('')
        strings.append('Q21: By the numbers.')
        strings.append('How many unique race winners will there be?')
        strings.append(str(self.unique_race_winners()))
        strings.append('How many unique pole sitters will there be?')
        strings.append(str(self.unique_pole_sitters()))
        strings.append('How many unique drivers will win the fastest lap?')
        strings.append(str(self.unique_fastest_lap()))
        strings.append('In how many races will the wet tire compound be used?')
        strings.append(str(self.wet_compound_races()))
        strings.append('How many drivers will be confirmed to leave F1 or change teams DURING the season?')
        strings.append(str(self.in_season_leavings()))
        strings.append('How many races will have track invasions by animals?')
        strings.append(str(self.track_invasions()))
        strings.append('Tie breaker: How many total drivers this season?')
        strings.append(str(self.total_drivers()))
        strings.append('')
        strings.append('Q22: Mini-Bingo')
        strings.append('Theo Pourchaire gets a 2022 F1 seat.')
        strings.append(self.pourchaire_seat())
        strings.append('Lando Norris gets a podium.')
        strings.append(self.lando_gets_a_podium())
        strings.append('Williams do not finish 10th.')
        strings.append(self.williams_above_tenth())
        strings.append('Red Bull changes drivers mid-season')
        strings.append(self.red_bull_driver_change())
        strings.append('At least one race has 20 classified finishers.')
        strings.append(self.all_20_finished())
        strings.append('World Driver Championship goes all the way to the final race.')
        strings.append(self.down_to_the_wire())
        strings.append('Russell outscores a non-Williams driver.')
        strings.append(self.russell_outscores_someone())

        return '\n'.join(strings)
        
    def map_table_to_score(self, table, score_map, tie_breaker_pos=None):
        """
        Use the table and the score map to return a dictionary that maps the 
         table entry name to the points having selected the answer is worth.
         Include a tie breaker value if the relevant position is passed.

        Keyword arguments:
        table -- The Table object representing the standings for the question
        score_map -- A dictionary with the table position as the key and the 
         point value for selecting the entry at that position
        tie_breaker_pos -- The position to return the score from the table of 
         to use in breaking ties when evaluating entries.

        Returns:
        A set with a dictionary as the first element that uses the entry name 
         from the table as the key and the points that answer is worth as the 
         value. If a tie breaker position is defined, the second element of the
         set is the score of that entry in the table, otherwise it is None.
        """
        answer_key = {}
        tie_breaker = None

        '''
        If a team is tied for a position it will be returned at multiple
        positions, so we add teams to a set as they are added to the key 
        and check the set before adding it to the key
        '''
        for pos, pts in score_map.items():
            entries = table.get_entries_by_pos(pos)
            for entry in entries:
                '''
                If a tie_breaker_pos is set, return the score of the tie
                breaking position from the table
                '''
                if tie_breaker_pos is not None and pos == tie_breaker_pos \
                    and tie_breaker is None:
                    tie_breaker = entry.score
                if entry.entry.name not in answer_key:
                    answer_key[entry.entry.name] = pts

        return (answer_key, tie_breaker)

    def team_fourth(self):
        '''
        Provide the answer key for the question "Which team will finish fourth
         in the championship?" and its tiebreaker, "How many points will the 
         fourth place team collect?"

        Returns:
        A dictionary mapping team names to point value if chosen, and the tiebreaker
        value
        '''
        team_points = self.teams.get_points_table()
        score_map = { 4: 25, 3: 18, 5: 18, 2: 15, 6: 15, 1: 12, 7: 12, 8: 10,
            9: 8, 10: 6 }
        return self.map_table_to_score(team_points, score_map, tie_breaker_pos=4)


    def avg_points_increase(self):
        """
        Answer the question "Which team will have the highest points per race 
        increase over 2020?"

        Returns:
        A dictionary mapping team names to point value if chosen
        """
        avg_points_increase_table = self.teams.get_average_point_change_table()
        score_map = {1: 25, 2: 18, 3: 15, 4: 12, 5: 10, 6: 8, 7: 6, 8: 4, 
            9: 2, 10: 1}
        return self.map_table_to_score(avg_points_increase_table, score_map)


    def driver_of_the_day(self):
        """
        Answer the question "Who will win the most official 'Driver of the Day'
         awards?"

        Returns:
        A dictionary mapping driver names to point value if chosen
        """
        driver_of_the_day_table = self.drivers.get_driver_of_the_day_table()
        score_map = {1: 25, 2: 18, 3: 15, 4: 12, 5: 10, 6: 8, 7: 6, 8: 4, 
            9: 2, 10: 1, 11: 0, 12: 0, 13: 0, 14: 0, 15: 0, 16: 0, 17: 0, 
            18: 0, 19: 0, 20: 0}
        return self.map_table_to_score(driver_of_the_day_table, score_map)


    def driver_tenth(self):
        """
        Answer the qeustion "Which driver will finish 10th in the Championship"
         and the tie breaker "How many points will that driver get?"
        
        Returns:
        A dictionary mapping driver names to point value if chosen, and the 
        tiebreaker value
        """
        driver_points_table = self.drivers.get_points_table()
        score_map = {10: 25, 9: 18, 11: 18, 8: 15, 12: 15, 7: 12, 13: 12, 
            6: 10, 14: 10, 5: 8, 15: 8, 4: 6, 16: 6, 3: 4, 17: 4, 2: 2, 18: 2, 
            1: 1, 19: 1, 20: 0} 
        return self.map_table_to_score(driver_points_table, score_map, 
            tie_breaker_pos=10)


    def teammate_qualy(self):
        """
        Answer the question "Which driver will be most dominant over their 
         teammate in qualifying?"

        Returns:
        A dictionary mapping driver names to point value if chosen
        """
        teammate_qualy_table = self.teams.get_teammate_qualy_table()
        score_map = {1: 25, 2: 18, 3: 15, 4: 12, 5: 10, 6: 8, 7: 6, 8: 4, 
            9: 2, 10: 1, 11: 0, 12: 0, 13: 0, 14: 0, 15: 0, 16: 0, 17: 0, 
            18: 0, 19: 0, 20: 0}
        return self.map_table_to_score(teammate_qualy_table, score_map)


    def podium_winners(self):
        """
        Answer the question "Check every driver that will have a podium finish 
         during the season."
        
        Returns:
        A list of driver names that have appeared on the podium
        """
        return [driver.name for driver in self.drivers.list_all_drivers() if driver.podiums > 0]


    def dis_points(self):
        """
        Answer the question "Which driver will have the most penalty points?"

        Returns:
        A dictionary mapping driver names to point value if chosen
        """
        dis_points_table = self.drivers.get_dis_points_table()
        score_map = {1: 25, 2: 18, 3: 15, 4: 12, 5: 10, 6: 8, 7: 6, 8: 4, 
            9: 2, 10: 1, 11: 0, 12: 0, 13: 0, 14: 0, 15: 0, 16: 0, 17: 0, 
            18: 0, 19: 0, 20: 0}
        return self.map_table_to_score(dis_points_table, score_map)
        

    def avg_laps(self):
        """
        Answer the question "Which driver will have the lowest average race 
         laps per race started?"

        Returns:
        A dictionary mapping driver names to point value if chosen
        """
        average_laps_table = self.drivers.get_avg_laps_table()
        score_map = {1: 25, 2: 18, 3: 15, 4: 12, 5: 10, 6: 8, 7: 6, 8: 4, 
            9: 2, 10: 1, 11: 0, 12: 0, 13: 0, 14: 0, 15: 0, 16: 0, 17: 0, 
            18: 0, 19: 0, 20: 0}
        return self.map_table_to_score(average_laps_table, score_map)


    def six_after_six(self):
        """
        Answer the question "Who will be the top six drivers after the first 
         six races?"

        Returns:
        The table representing the points standings after the first six races
        """
        completed_races = self.races.list_races_before(self.datetime)
        if len(completed_races) >= 6:
            return completed_races[5].post_race_driver_points
        return completed_races[-1].post_race_driver_points


    def uninterrupted_leader(self):
        """
        Answer the question "At which race will the champion move to the top of
         the standings and never drop out of the top spot?" as well as the tie
         breaker "Same question, but for the second place finisher?"

        Returns:
        A set with the race at which the current leader became the leader and
         the race at which the second place driver became second place
        """
        completed_races = self.races.list_races_before(self.datetime)
        places_dict = {
            1: {
                'driver': None,
                'race': None
            },
            2: {
                'driver': None,
                'race': None
            }
        }
        for race in completed_races:
            for pos, pos_dict in places_dict.items():
                drivers = race.post_race_driver_points.get_entries_by_pos(pos)
                if len(drivers) > 1:
                    pos_dict['driver'] = None
                    pos_dict['race'] = None
                elif drivers[0].entry.name != pos_dict['driver']:
                    pos_dict['driver'] = drivers[0].entry.name
                    pos_dict['race'] = race

        """
        Once the race is determined, build a dictionary of race to points
         such that one away gets 18 points, two away gets 15, etc 
        """
        points_list = [18, 15, 12, 10, 8, 6, 4, 2, 1]
        for pos, pos_dict in places_dict.items():
            pos_dict['values'] = {str(pos_dict['race']): 25}
            before = self.races.list_races_before(pos_dict['race'].datetime)
            after = self.races.list_races_after(pos_dict['race'].datetime)
            before_count = min(len(before), len(points_list))
            after_count = min(len(after), len(points_list))
            for race, points in zip(list(reversed(before))[0:before_count], points_list[0:before_count]):
                pos_dict['values'][str(race)] = points
            for race, points in zip(after[0:after_count], points_list[0:after_count]):
                pos_dict['values'][str(race)] = points
        return (places_dict[1]['values'], places_dict[2]['values'])


    def retirements(self):
        """
        Answer the question "Pick three races, each retirement from the chosen 
         races will cost you -5 points."

        Returns:
        A dictionary mapping a race to the number of retirements it had
        """
        race_dict = {}
        for race in self.races.race_list:
            race_dict[str(race)] = race.retirements * -5
        return race_dict


    def driver_points_by_race(self, driver_short_name, mult=1):
        """
        Build a dicitonary of races to points scored by the provided driver

        Keyword Arguments:
        driver_short_name -- The driver's name in 'last, first' form
        mult -- a multplier for the driver's points if applicable

        Returns:
        A dictionary mapping a race to the drivers points for that race
        """
        race_dict = {}
        driver = self.drivers.get_driver_by_short_name(driver_short_name)
        if len(driver) > 1:
            raise Exception(f"Too many driver matches found for {driver_short_name}")
        elif len(driver) == 0:
            raise Exception(f"No driver matches found for {driver_short_name}")
        driver = driver[0]
        for race, result in driver.races.items():
            race_dict[race] = result.points * mult
        return race_dict


    def gasly_points(self):
        """
        Answer the question "Pick two races, get the points scored by Pierre 
         Gasly for those races."

        Returns:
        A dictionary mapping a race to Pierre Gasly's points for that race
        """
        return self.driver_points_by_race("Gasly, Pierre")


    def stroll_points(self):
        """
        Answer the question "Pick two races, get the points scored by Lance 
         Stroll for those races."

        Returns:
        A dictionary mapping a race to Lance Stroll's points for that race
        """
        return self.driver_points_by_race("Stroll, Lance")


    def mazepin_points(self):
        """
        Answer the question "Pick two races, SUBTRACT Nikita Mazepin's points 
         for those races"

        Returns:
        A dictionary mapping a race to Nikita Mazepin's points for that race
        """
        return self.driver_points_by_race("Mazepin, Nikita", -1)


    def bottom_seven(self):
        """
        Answer the question "Pick two drivers who are not currently teammates 
         from the bottom seven teams in 2020. (Combined Championship points 
         used to rank against fellow players. Points scored by F1 system)"
         In this case that means returning a driver points dictionary for 
         drivers in those bottom seven teams of 2020.

        Returns:
        A dictionary mapping drivers to points from the bottom seven teams of 
         2020
        """
        teams = ["Aston Martin", "Alpine", "Ferrari", "AlphaTauri", 
            "Alfa Romeo Racing", "Haas F1 Team", "Williams"]
        driver_points_dict = {}
        for driver in self.drivers.driver_list:
            if driver.team_name in teams:
                driver_points_dict[str(driver)] = driver.points
        return driver_points_dict


    def safety_cars(self):
        """
        Answer the qeustion "How many safety and virtual safety cars will be 
         called in 2021?" and the tie breaker "Which race will have the most 
         safety cars of all types?"

        Returns:
        A dictionary mapping races to safety cars and a list of races that 
         tied for the most safety cars
        """
        safety_car_dict = {}
        total_safety_cars = 0
        for race in self.races.race_list:
            total_safety_cars += race.safety_cars
            if race.safety_cars in safety_car_dict:
                safety_car_dict[race.safety_cars].append(str(race))
            else:
                safety_car_dict[race.safety_cars] = [str(race)]

        race_safety_car_dict = {}
        for safety_cars in reversed(sorted(safety_car_dict.keys())):
            for race in safety_car_dict[safety_cars]:
                race_safety_car_dict[race] = safety_cars
        return (total_safety_cars, race_safety_car_dict)


    def fewest_on_lead_lap(self):
        """
        Answer the qeustion "What is the fewest number of drivers that will 
         finish on the lead lap of any race?"
        
        Returns:
        An integer representing the lowest number of cars on the lead lap of
         a race
        """
        fewest_on_lead_lap = 21
        for race in self.races.list_races_before(self.datetime):
            drivers_on_lead_lap = 0
            for driver in self.drivers.driver_list:
                if str(race) in driver.races:
                    driver_race_result = driver.races[str(race)]
                    if driver_race_result.laps == race.laps:
                        drivers_on_lead_lap += 1
            if drivers_on_lead_lap < fewest_on_lead_lap:
                fewest_on_lead_lap = drivers_on_lead_lap
        return fewest_on_lead_lap


    def russia_facts(self):
        """
        Answer the questions "How many drivers will take on soft tires in the 
         last 5 laps in Russia" and the tie breaker "What will be the total 
         number of laps run on softs by the race winner in Russia?"

        Returns:
        A set of two integers, the number of drivers that pitted for softs at 
         the end and the total number of laps on soft for the winner in Russia
        """
        return (
            self.single_answer_dict['Pitted for Softs in last five laps at Russia'],
            self.single_answer_dict['Total laps on softs for winner at Russia']    
        )


    def first_saudi_retirement(self):
        """
        Answer the question "Which driver that starts the race in Saudi Arabia 
         will be the first one out?" and the tie breaker "What WDC position 
         will that driver start the race in?"

        Returns:
        A set with the name of the first driver out of Saudi Arabia and the 
         position the driver occupies before the race
        """
        first_retirement = self.single_answer_dict['First retirement at Saudi Arabia']
        # Race has not occurred yet
        if first_retirement is None or len(first_retirement) == 0:
            return (None, None)
        driver = self.drivers.get_driver_by_short_name(first_retirement)
        previous_race = self.races.get_race_by_name('Australia')
        # Race has not occurred yet
        if previous_race is None or previous_race.post_race_driver_points is None:
            return (None, None)
        wdc_pos = previous_race.post_race_driver_points.get_position_of_entry(driver[0])
        return (first_retirement, wdc_pos)


    def unique_race_winners(self):
        """
        Answer the question "How many unique race winners will there be?"

        Returns:
        An integer representing the number of unique winners over the season
        """
        winners = set()
        for driver in self.drivers.driver_list:
            if driver.wins > 0:
                winners.add(str(driver))
        return len(winners)


    def unique_pole_sitters(self):
        """
        Answer the question "How many unique pole sitters will there be?"

        Returns:
        An integer representing the number of unique pole sitters over the year
        """
        pole_sitters = set()
        for driver in self.drivers.driver_list:
            if driver.poles > 0:
                pole_sitters.add(str(driver))
        return len(pole_sitters)


    def unique_fastest_lap(self):
        """
        Answer the question "How many unique drivers will win the fastest lap?"

        Returns:
        An integer representing the number of unique fastest lap winners
        """
        fastest_lap_winners = set()
        for driver in self.drivers.driver_list:
            if driver.fastest_laps > 0:
                fastest_lap_winners.add(str(driver))
        return len(fastest_lap_winners)


    def wet_compound_races(self):
        """
        Answer the question "In how many races will the wet tire compound be used?"

        Returns:
        The number of races a wet compound was used
        """
        return self.single_answer_dict['How many races have wet compound used']


    def in_season_leavings(self):
        """
        Answer the qeustion "How many drivers will be confirmed to leave F1 or 
         change teams DURING the season?"

        Returns:
        The number of drivers confirmed to change teams or leave F1 during the 
         season
        """
        return self.single_answer_dict['How many drivers confirmed to leave']


    def track_invasions(self):
        """
        Answer the question "How many races will have track invasions by 
         animals?"

        Returns:
        The number of track invasions and 
        """
        return self.single_answer_dict['How many races with animal invasions']


    def total_drivers(self):
        """
        Answer the qustion "How many total drivers this season?" This is the 
         tie breaker for the "By the Numbers" section

        Returns:
        Total number of drivers for the season
        """
        return len(self.drivers.driver_list)


    def pourchaire_seat(self):
        """
        Answer the question "Theo Pourchaire gets a 2022 F1 seat."

        Returns:
        A TRUE or FALSE (Strings due to string repr from questionaire)
        """
        return self.single_answer_dict['Does Theo Pourchaire have a 2022 seat']


    def lando_gets_a_podium(self):
        """
        Answer the qeustion "Lando Norris gets a podium."

        Returns:
        A TRUE or FALSE (Strings due to string repr from questionaire)
        """
        lando = self.drivers.get_driver_by_short_name('Norris, Lando')
        if len(lando) == 0 or len(lando) > 1:
            raise Exception('Too many or to few Landos found')
        if lando[0].podiums > 0:
            return 'TRUE'
        return 'FALSE'


    def williams_above_tenth(self):
        """
        Answer the question "Williams do not finish 10th."

        Returns:
        A TRUE or FALSE (Strings due to string repr from questionaire)
        """
        table = self.teams.get_points_table()
        tenth = table.get_entries_by_pos(10)
        for entry in tenth:
            if entry.entry.name == 'Williams':
                return 'FALSE'
        return 'TRUE'


    def red_bull_driver_change(self):
        """
        Answer the qeustion "Red Bull changes drivers mid-season"

        Returns:
        A TRUE or FALSE (Strings due to string repr from questionaire)
        """
        return self.single_answer_dict['Has Red Bull changed drivers']


    def all_20_finished(self):
        """
        Answer the question "At least one race has 20 classified finishers."

        Returns:
        A TRUE or FALSE (Strings due to string repr from questionaire)
        """
        for race in self.races.list_races_before(self.datetime):
            if race.retirements == 0:
                return "TRUE"
        return "FALSE"


    def down_to_the_wire(self):
        """
        Answer the question "World Driver Championship goes all the way to the 
         final race."
        
        Returns:
        A TRUE, FALSE, or TBD if answer unknown as of yet (Strings due to 
         string repr from questionaire)
        """
        next_to_last = self.races.list_races()[-1]
        if next_to_last is None or next_to_last.post_race_driver_points is None:
            return 'TBD'
        first = next_to_last.post_race_driver_points.get_entries_by_pos(1)
        if len(first) > 1:
            return 'TRUE'
        second = next_to_last.post_race_driver_points.get_entries_by_pos(2)
        if first[0].score - second[0].score <= 26:
            return 'TRUE'
        return 'FALSE'


    def russell_outscores_someone(self):
        """
        Answer the question "Russell outscores a non-Williams driver."

        Returns:
        A TRUE or FALSE (Strings due to string repr from questionaire)
        """
        russell = self.drivers.get_driver_by_short_name("Russell, George")
        russell_points = russell[0].points
        if russell_points == 0:
            return 'FALSE'
        for driver in self.drivers.driver_list:
            if driver.team_name != 'Williams' and russell_points > \
                driver.points:
                return 'TRUE'
        return 'FALSE'

