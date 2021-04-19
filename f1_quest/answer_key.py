import csv
import os

from datetime import datetime
from f1_quest.drivers import Driver, Drivers
from f1_quest.entries import Entries
from f1_quest.races import Races
from f1_quest.tables import Table
from f1_quest.teams import Teams


F1_POINTS = {1: 25, 2: 18, 3: 15, 4: 12, 5: 10, 6: 8, 7: 6, 8: 4, 9: 2, 10: 1}


class QuestionSummary():
    def __init__(self, short_name, question, desc=None, answer=None, score=None, 
        entry_var=None, entry_tb=None):
        self.short_name = short_name
        self.question = question
        self.desc = desc
        self.answer = answer
        self.score = score
        self.entry_var = entry_var
        self.entry_tb = entry_tb

    
    def __str__(self):
        strings = [self.question]
        if self.desc is not None:
            strings.append(self.desc)
        if self.answer is not None:
            if type(self.answer) == list:
                for answer in self.answer:
                    strings.append('')
                    strings.append(str(answer))
            else:
                strings.append('')
                strings.append(str(self.answer))
        if self.score is not None:
            strings.append('')
            strings.append(str(self.score))
        return '\n'.join(strings)



class AnswerKey():
    def __init__(self, data_dir='data', datetime=datetime.now(), 
        file_name='scoring_single_answer.csv'):
        self.teams = Teams(data_dir=data_dir)
        self.drivers = Drivers(data_dir=data_dir)
        self.entries = Entries  (data_dir=data_dir)
        self.races = Races(data_dir=data_dir)
        self.races.read_results(data_dir=data_dir, drivers=self.drivers, 
            teams=self.teams, datetime=datetime)
        self.datetime = datetime
        self.questions = []

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

        answer, score = self.team_fourth()
        self.questions.append(QuestionSummary('Q1: Team Fourth',
            'Q1: Which team will finish fourth in the championship?',
            desc='Tie Breaker: How many points will the 4th place team get?',
            answer=answer, score=score, entry_var='team_fourth_response',
            entry_tb='team_fourth_tiebreaker'))
        
        answer, score = self.avg_points_increase()
        self.questions.append(QuestionSummary('Q2: Average Points Increase',
            'Q2: Which team will have the highest points per race increase over 2020?',
            answer=answer, score=score, entry_var='team_points_avg_response'))
        
        self.questions.append(QuestionSummary('Q3: Fastest Pit Stop',
            'Q3: Which team will win the DHL Fastest Pit Stop?',
            desc='No data available and everyone voted for Red Bull, so good work everyone!',
            entry_var='team_fps_response'))

        answer, score = self.driver_of_the_day()
        self.questions.append(QuestionSummary('Q4: Driver of the Day',
            'Q4: Who will win the most official "Driver of the Day" awards?',
            answer=answer, score=score, entry_var='driver_of_the_day_response'))

        answer, score = self.driver_tenth()
        self.questions.append(QuestionSummary('Q5: Driver Tenth',
            'Q5: Which driver will finish 10th in the Championship?',
            desc='Tie Breaker: How many points did that driver get?',
            answer=answer, score=score, entry_var='driver_tenth_response',
            entry_tb='driver_tenth_tiebreaker'))

        answer, score = self.teammate_qualy()
        self.questions.append(QuestionSummary('Q6: Qualy Dominance',
            'Q6: Which driver will be most dominant over their teammate in qualifying?',
            answer=answer, score=score, entry_var='driver_qualy_dominance'))

        answer, score = self.podium_winners()
        self.questions.append(QuestionSummary('Q7: Podium Winners',
            'Q7: Check every driver that will have a podium finish during the season.',
            desc='+5 for every correct, -3 for every incorrect guess, -3 for every missed podium',
            answer=answer, score=score, entry_var='driver_podium_response'))
        
        answer, score = self.dis_points()
        self.questions.append(QuestionSummary('Q8: Disciplinary Points',
            'Q8: Which driver will have the most penalty points?',
            answer=answer, score=score, entry_var='driver_penalty_points'))

        answer, score = self.avg_laps()
        self.questions.append(QuestionSummary('Q9: Fewest Average Laps',
            'Q9: Which driver will have the lowest average race laps per race started?',
            answer=answer, score=score, entry_var='drvier_lowest_laps_avg'))

        answer, score = self.six_after_six()
        self.questions.append(QuestionSummary('Q10: Top Six After Six',
            'Q10: Who will be the top six drivers after the first six races?',
            desc='\n'.join(['Right driver, right place (+5)',
                'Right driver, one place out (+3)', 
                'Right driver, two places out (+2)',
                'Right driver, 3 or more places out (+1)']),
            answer=answer, score=score, entry_var='driver_six_after_six'))

        answer, score = self.uninterrupted_leader()
        self.questions.append(QuestionSummary('Q11: Uninterrupted Leader',
            'Q11: At which race will the champion move to the top of the standings and never drop out of the top spot?',
            desc='At which race does the #2 driver take an unbroken position in the championship?',
            answer=answer, score=score, entry_var='driver_unbroken_lead_response',
            entry_tb='driver_unbroken_lead_tiebreaker'))

        answer, score = self.retirements()
        self.questions.append(QuestionSummary('Q12: Retirements',
            'Q12: Pick three races, each retirement from the chosen races will cost you -5 points.',
            answer=answer, score=score, entry_var='driver_race_retirements_response'))

        answer, score = self.gasly_points()
        self.questions.append(QuestionSummary('Q13: Gasly Points',
            'Q13: Pick two races, get the points scored by Pierre Gasly for those races.',
            answer=answer, score=score, entry_var='driver_gasly_points_response'))

        answer, score = self.stroll_points()
        self.questions.append(QuestionSummary('Q14: Stroll Points',
            'Q14: Pick two races, get the points scored by Lance Stroll for those races.',
            answer=answer, score=score, entry_var='driver_stroll_points_response'))

        answer, score = self.mazepin_points()
        self.questions.append(QuestionSummary('Q15: Mazepin Points',
            'Q15: Pick two races, SUBTRACT Nikita Mazepin\'s points for those races',
            answer=answer, score=score, entry_var='driver_mazepin_points_response'))

        answer, score = self.bottom_seven()
        self.questions.append(QuestionSummary('Q16: Two from the Bottom Seven',
            'Q16: Pick two drivers who are not currently teammates from the bottom seven teams in 2020.',
            answer=answer, score=score, entry_var='driver_pick_two_response'))

        answer, score = self.safety_cars()
        self.questions.append(QuestionSummary('Q17: Safety Cars',
            'Q17: How many safety and virtual safety cars will be called in 2021?',
            desc='Tie breaker: Which race will have the most safety cars of all types?',
            answer=answer, score=score, entry_var='race_safety_cars_response',
            entry_tb='race_safety_cars_tiebreaker'))

        answer, score = self.fewest_on_lead_lap()
        self.questions.append(QuestionSummary('Q18: Fewest on Lead Lap',
            'Q18: What is the fewest number of drivers that will finish on the lead lap of any race?',
            answer=answer, score=score, entry_var='race_fewest_on_lead_lap_response'))

        answer, score = self.russia_facts()
        self.questions.append(QuestionSummary('Q19: Soft on Russia',
            'Q19: How many drivers will take on soft tires in the last 5 laps in Russia?',
            desc="Tie breaker: How many laps will the winner have done on soft tires?",
            answer=answer, score=score, entry_var='russia_stop_for_softs_response',
            entry_tb='russia_stop_for_softs_tiebreaker'))

        answer, score = self.first_saudi_retirement()
        self.questions.append(QuestionSummary('Q20: Retiring to Saudi Arabia',
            'Q20: Which driver that starts the race in Saudi Arabia will be the first one out?',
            desc='Tie breaker: What WDC position will that driver start the race in?\n\nTBD after Saudi Arabian GP is run',
            answer=answer, score=score, entry_var='saudi_first_retirement_response',
            entry_tb='saudi_first_retirement_tiebrekaer'))

        answer, score = self.by_the_numbers()
        self.questions.append(QuestionSummary('Q21: By The Numbers',
            'Q21: By the numbers.', 
            desc="Sum the numbers in the following tables and be closest to the total",
            answer=answer, score=score, entry_var=list(zip(['Number of Winners',
                'Number of Pole Sitters', 'Number of Fastest Lap Winners',
                'Number of Races with Wet Compounds Used', 'Number ofDrivers Confirmed to Leave in Season',
                'Number of Animal Track Invasions'], [
                'btn_unique_winners_response',
                'btn_unique_pole_sitters_response', 
                'btn_unique_fastest_lap_response',
                'btn_wet_compound_races_response', 
                'btn_driver_departure_confirmed_response',
                'btn_animal_invasions_response'])),
            entry_tb='btn_total_drivers_tiebreaker'))

        answer, score = self.mini_bingo()
        self.questions.append(QuestionSummary('Q22: Mini-Bingo',
            'Q22: Mini-Bingo',
            desc='Correctly True: +5, Correctly False: +1, Incorrect: -3',
            answer=answer, score=score, entry_var=list(zip(['Pourchaire in 2022',
                'Norris Gets a Podium', 'Williams Finishes Above 10th', 
                'Red Bull Changes Drivers in Season', 
                'All 20 Drivers Classified in One Race',
                'World Driver Championship Goes to Final Race', 
                'Russell Outscores a Driver That is Not a Teammate'], [
                'bingo_pourchaire_response',
                'bingo_norris_response',
                'bingo_williams_response',
                'bingo_red_bull_response',
                'bingo_twenty_classifieds_response',
                'bingo_down_to_the_wire_response',
                'bingo_russell_response']))))


    def __str__(self):
        """
        This aggressively long method pulls together all of the questions and 
         answers as a string to be printed for aiding manual scoring of entries
        """
        strings = ['F1 Questionnaire Answer Key', '', 
            'This is a snapshot of where things stand if the season were to end today. Expect changes each week!', 
            '']

        score = self.get_overall_standings()
        strings.append(str(score))
        strings.append('')

        for question in self.questions:
            strings.append(str(question))
            strings.append('')
        return '\n'.join(strings)


    def get_overall_standings(self):
        score = Table("Overall Standings", "Entry", "Points", int, 
            show_values=False, show_entries=False)
        for entry in self.entries.list_entries():
            score.add_subject(entry.score, entry)
        return score
        
    def map_table_to_score(self, table, score_map, tie_breaker_pos=None, 
        update_entry_score=False):
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
        update_entry_score -- Add value to entry

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
            rows = table.get_subjects_by_pos(pos)
            for row in rows:
                '''
                If a tie_breaker_pos is set, return the score of the tie
                breaking position from the table
                '''
                if tie_breaker_pos is not None and pos == tie_breaker_pos \
                    and tie_breaker is None:
                    tie_breaker = row.score                    
                if str(row.subject) not in answer_key:
                    answer_key[str(row.subject)] = pts
                    if tie_breaker_pos is None:
                        row.set_value(pts)
                        if update_entry_score:
                            for entry in row.matching_entries:
                                entry.add_points(pts)

        return (answer_key, tie_breaker)

    
    def tie_breaker_scoring(self, table_name, score_map, source_table, 
        tie_breaker, tie_breaker_var):
        """
        Take a table of entries, score map and tie breaker variable name and 
         return a table that breaks ties where it can to score the entries in 
         the score_table

        Keyword arguments:
        table_name -- The name to display at the top of the table
        score_map -- A dictionary mapping the table position to point value
        source_table -- The table with entries attached to their row
        tie_breaker -- The value to compare the entries guess against
        tie_breaker_var -- The name of the variable in the Entry to use as the 
         tie breaker

        Returns:
        A Table with the entries as subjects and scored values as the score
        """
        entry_table = Table(table_name, "Entry", "Points", int, 
            show_values=False, show_entries=False)

        # Group entries by score in the score map
        score_dict = {}
        entry_placed_dict = {}
        for pos, pts in score_map.items():
            rows = source_table.get_subjects_by_pos(pos)
            for row in rows:
                for entry in row.matching_entries:
                    if entry.entry_name in entry_placed_dict:
                        continue
                    entry_placed_dict[entry.entry_name] = True
                    entry_tb_score = abs(entry.__dict__[tie_breaker_var]) - tie_breaker
                    if pts not in score_dict:
                        score_dict[pts] = {}
                    if entry_tb_score not in score_dict[pts]:
                        score_dict[pts][entry_tb_score] = [entry]
                    else:
                        score_dict[pts][entry_tb_score].append(entry)

        # Score grouped entries by tie breaker value
        entry_pos = 1
        abs_pos = 1
        for score in reversed(sorted(score_dict.keys())): 
            for tb_score in sorted(score_dict[score].keys()):
                for entry in score_dict[score][tb_score]:
                    entry_table.add_subject(F1_POINTS[entry_pos], entry)
                    entry.add_points(F1_POINTS[entry_pos])
                    abs_pos += 1
                entry_pos = abs_pos
        return entry_table


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
        team_points.add_entries(self.entries, 'team_fourth_response', 
                                'team_fourth_tiebreaker')
        team_points.show_values = False
        answer_key, tie_breaker = self.map_table_to_score(team_points, 
                                                          score_map, 
                                                          tie_breaker_pos=4)

        entry_table = self.tie_breaker_scoring("Final Scores", 
                                               score_map, team_points,
                                               tie_breaker, 
                                               'team_fourth_tiebreaker')

        return (team_points, entry_table)


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
        avg_points_increase_table.add_entries(self.entries, 
            'team_points_avg_response')
        answer_key, tie_breaker = self.map_table_to_score(
            avg_points_increase_table, score_map, update_entry_score=True)
        return (avg_points_increase_table, None)


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
        driver_of_the_day_table.add_entries(self.entries, 'driver_of_the_day_response')
        answer_key, tie_breaker = self.map_table_to_score(
            driver_of_the_day_table, score_map, update_entry_score=True)
        return(driver_of_the_day_table, None)


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
        driver_points_table.add_entries(self.entries, 'driver_tenth_response', 'driver_tenth_tiebreaker')
        driver_points_table.show_values = False
        answer_key, tie_breaker = self.map_table_to_score(driver_points_table, score_map, 
            tie_breaker_pos=10)

        entry_table = self.tie_breaker_scoring("Final Scores", 
                                               score_map, driver_points_table,
                                               tie_breaker, 
                                               'driver_tenth_tiebreaker')
        return (driver_points_table, entry_table)


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
        teammate_qualy_table.add_entries(self.entries, 
            'driver_qualy_dominance')
        answer_key, tie_breaker =  self.map_table_to_score(
            teammate_qualy_table, score_map, update_entry_score=True)
        return (teammate_qualy_table, None)


    def podium_winners(self):
        """
        Answer the question "Check every driver that will have a podium finish 
         during the season."
        
        Returns:
        A list of driver names that have appeared on the podium
        """
        podium_winners = [driver.entry_rep for driver in self.drivers.list_all_drivers() if driver.podiums > 0]
        podium_winners_table = Table('Podium Winners', 'Driver', 'Podium Finishes', int)
        for driver in self.drivers.list_all_drivers():
            podium_winners_table.add_subject(driver.podiums, driver)
        score_map = {}
        for i in range(1, len(podium_winners)+1):
            score_map[i] = 5
        for i in range(len(podium_winners)+1, len(self.drivers.list_all_drivers())+1):
            score_map[i] = -3
        podium_winners_table.add_entries(self.entries, 'driver_podium_response')
        answer_key, tie_breaker = self.map_table_to_score(podium_winners_table, score_map)

        score_table = Table('Final Scores', 'Entry', 'Points', int, 
            show_values=False, show_entries=False)
        for entry in self.entries.list_entries():
            entry_points = 0
            drivers_counted = 0
            for driver in entry.driver_podium_response:
                # Add five for each correct pick
                if driver in podium_winners:
                    entry_points += 5
                # Subtract 3 for each incorrect pick
                else:
                    entry_points -= 3
            for driver in podium_winners:
                # Subtract 3 for each missed podium winner
                if driver not in entry.driver_podium_response:
                    driver_obj = self.drivers.get_driver_by_entry_rep(driver)
                    if driver_obj.started_season:
                        entry_points -= 3
            
            score_table.add_subject(entry_points, entry)
            entry.add_points(entry_points)
            
        return (podium_winners_table, score_table)


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
        dis_points_table.add_entries(self.entries, 'driver_penalty_points')
        answer_key, tie_breaker = self.map_table_to_score(dis_points_table, 
            score_map, update_entry_score=True)
        return (dis_points_table, None)
        

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
        average_laps_table.add_entries(self.entries, 'drvier_lowest_laps_avg')
        answer_key, tie_breaker = self.map_table_to_score(average_laps_table, 
            score_map, update_entry_score=True)
        return (average_laps_table, None)


    def six_after_six(self):
        """
        Answer the question "Who will be the top six drivers after the first 
         six races?"

        Returns:
        The table representing the points standings after the first six races
        """
        completed_races = self.races.list_races_before(self.datetime)
        points_table = completed_races[-1].post_race_driver_points
        if len(completed_races) >= 6:
            points_table = completed_races[5].post_race_driver_points
        points_table.show_values = False
        points_table.show_entries = False

        # Lists of drivers by position
        results = [points_table.get_subjects_by_pos(1),
                   points_table.get_subjects_by_pos(2),
                   points_table.get_subjects_by_pos(3),
                   points_table.get_subjects_by_pos(4),
                   points_table.get_subjects_by_pos(5),
                   points_table.get_subjects_by_pos(6)]
        # Score dictionaries by position
        scores = [{1:5, 2:3, 3:2, 4:1, 5:1, 6:1},
                  {1:3, 2:5, 3:3, 4:2, 5:1, 6:1},
                  {1:2, 2:3, 3:5, 4:3, 5:2, 6:1},
                  {1:1, 2:2, 3:3, 4:5, 5:3, 6:2},
                  {1:1, 2:1, 3:2, 4:3, 5:5, 6:3},
                  {1:1, 2:1, 3:1, 4:2, 5:3, 6:5}]
        # Build the map that will allow lookup of score by predicted driver and position
        drivers_placed = []
        driver_values = {}
        for driver_list, scores in zip(results, scores):
            for driver in driver_list:
                # In case of ties
                if driver.subject.entry_rep in drivers_placed:
                    continue
                drivers_placed.append(driver.subject.entry_rep)
                driver_values[driver.subject.entry_rep] = scores

        score_table = Table("Final Scores", "Entry", "Points", int, 
            show_values=False, entry_label="Picks")
        for entry in self.entries.list_entries():
            entry_score = 0
            for pos in range(6):
                if entry.driver_six_after_six[pos] in driver_values:
                    entry_score += driver_values[entry.driver_six_after_six[pos]][pos+1]
            entry_row = score_table.add_subject(entry_score, entry)
            entry.add_points(entry_score)
            entry_row.matching_entries = entry.driver_six_after_six
        return (points_table, score_table)


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
                drivers = race.post_race_driver_points.get_subjects_by_pos(pos)
                if len(drivers) > 1:
                    pos_dict['driver'] = None
                    pos_dict['race'] = None
                elif drivers[0].subject.name != pos_dict['driver']:
                    pos_dict['driver'] = drivers[0].subject.name
                    pos_dict['race'] = race

        """
        Once the race is determined, build a dictionary of race to distance 
        from correct answer for each position
        """
        #points_list = [18, 15, 12, 10, 8, 6, 4, 2, 1]
        for pos, pos_dict in places_dict.items():
            pos_dict['values'] = {str(pos_dict['race']): 0}
            before = self.races.list_races_before(pos_dict['race'].datetime)
            after = self.races.list_races_after(pos_dict['race'].datetime)
            before_count = len(before) #min(len(before), len(points_list))
            after_count = len(after) #min(len(after), len(points_list))
            for race, points in zip(list(reversed(before))[0:before_count+1], 
                range(1, before_count+1)): #points_list[0:before_count]):
                pos_dict['values'][str(race)] = points
            for race, points in zip(after[0:after_count+1], 
                range(1, after_count+1)): #points_list[0:after_count]):
                pos_dict['values'][str(race)] = points

        table = Table('Uninterupted Leader', 'Race', 'Position Locked', str, 
            show_values=False, sort=None)
        for race in self.races.list_races():
            vals = []
            if places_dict[1]['race'] == race:
                vals.append('Leader')
            if places_dict[2]['race'] == race:
                vals.append('Second')
            table.add_subject(', '.join(vals), race)
        table.add_entries(self.entries, 'driver_unbroken_lead_response', 
            'driver_unbroken_lead_tiebreaker')

        # Build a dictionary of entries by distance from leader and second
        sorting_dict = {}
        for entry in self.entries.list_entries():
            off_by = places_dict[1]['values'][entry.driver_unbroken_lead_response]
            tie_breaker = places_dict[2]['values'][entry.driver_unbroken_lead_tiebreaker]
            if off_by not in sorting_dict:
                sorting_dict[off_by] = {}
            if tie_breaker not in sorting_dict[off_by]:
                sorting_dict[off_by][tie_breaker] = [entry]

        # Assign scores based on distance from answer for leader and second
        scores_assigned = 1
        scoring = Table('Final Scores', 'Entry', 'Points', int, 
            show_values=False, show_entries=False)
        for off_by in sorted(sorting_dict.keys()):
            for tie_breaker in sorted(sorting_dict[off_by].keys()):
                for entry in sorting_dict[off_by][tie_breaker]:
                    scoring.add_subject(F1_POINTS[scores_assigned], entry)
                    entry.add_points(F1_POINTS[scores_assigned])
                scores_assigned += len(sorting_dict[off_by][tie_breaker])
        return (table, scoring)


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

        table = Table('Retirements', 'Race', 'Retirements', int, sort=None)
        for race in self.races.list_races():
            race_row = table.add_subject(race.retirements, race)
            race_row.value = race_dict[str(race)]
        table.add_entries(self.entries, 'driver_race_retirements_response')

        scores = Table('Final Score', 'Entry', 'Points', int, show_values=False, 
            show_entries=False)
        for entry in self.entries.list_entries():
            entry_score = 0
            for race in entry.driver_race_retirements_response:
                if type(race_dict[race]) == int:
                    entry_score += race_dict[race]
            scores.add_subject(entry_score, entry)
            entry.add_points(entry_score)
        return (table, scores)


    def driver_points_by_race(self, driver_short_name, entry_var, mult=1):
        """
        Build a dicitonary of races to points scored by the provided driver

        Keyword Arguments:
        driver_short_name -- The driver's name in 'last, first' form
        entry_var -- The name of the variable in entry to use
        mult -- a multplier for the driver's points if applicable

        Returns:
        A dictionary mapping a race to the drivers points for that race
        """
        race_dict = {}
        driver = self.drivers.get_driver_by_short_name(driver_short_name)
        if driver is None:
            raise Exception(f"No driver matches found for {driver_short_name}")

        for race, result in driver.races.items():
            race_dict[race] = result.points * mult
        
        table = Table(f"{driver_short_name} Points", "Race", "Points", int, 
            show_values=False, sort=None)
        for race in self.races.list_races():
            if str(race) in race_dict:
                table.add_subject(race_dict[str(race)], race)
            else:
                table.add_subject(0, race)
        table.add_entries(self.entries, entry_var)

        scores = Table("Final Score", "Entry", "Points", int, 
            show_values=False, show_entries=False)
        for entry in self.entries.list_entries():
            entry_score = 0
            for race in entry.__dict__[entry_var]:
                if str(race) in race_dict:
                    entry_score += race_dict[str(race)]
            scores.add_subject(entry_score, entry)
            entry.add_points(entry_score)
        
        return (table, scores)


    def gasly_points(self):
        """
        Answer the question "Pick two races, get the points scored by Pierre 
         Gasly for those races."

        Returns:
        A dictionary mapping a race to Pierre Gasly's points for that race
        """
        return self.driver_points_by_race("Gasly, Pierre", "driver_gasly_points_response")


    def stroll_points(self):
        """
        Answer the question "Pick two races, get the points scored by Lance 
         Stroll for those races."

        Returns:
        A dictionary mapping a race to Lance Stroll's points for that race
        """
        return self.driver_points_by_race("Stroll, Lance", "driver_stroll_points_response")


    def mazepin_points(self):
        """
        Answer the question "Pick two races, SUBTRACT Nikita Mazepin's points 
         for those races"

        Returns:
        A dictionary mapping a race to Nikita Mazepin's points for that race
        """
        return self.driver_points_by_race("Mazepin, Nikita", "driver_mazepin_points_response", -1)


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
        table = Table('Bottom seven driver points', 'Driver', 'Points', int, show_values=False)
        for driver in self.drivers.driver_list:
            if driver.team_name in teams:
                driver_points_dict[str(driver)] = driver.points
                table.add_subject(driver.points, driver)
        table.add_entries(self.entries, 'driver_pick_two_response')

        entry_scores = {}
        for entry in self.entries.list_entries():
            entry_score = 0
            for driver in entry.driver_pick_two_response:
                entry_score += driver_points_dict[str(driver)]
            if entry_score not in entry_scores:
                entry_scores[entry_score] = [entry]
            else:
                entry_scores[entry_score].append(entry)
        
        scores = Table("Final Score", "Entry", "Points", int, 
            show_values=False, show_entries=False)
        pos = 1
        for score in reversed(sorted(entry_scores.keys())):
            for entry in entry_scores[score]:
                scores.add_subject(F1_POINTS[pos], entry)
                entry.add_points(F1_POINTS[pos])
            pos += len(entry_scores[score])
        return (table, scores)


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
        table = Table('Total Safety Cars', 'Race', 'Saftey Cars', int, 
            show_values=False)
        for race in self.races.race_list:
            if type(race.safety_cars) == int:
                total_safety_cars += race.safety_cars
                table.add_subject(race.safety_cars, race)
                safety_car_dict[str(race)] = race.safety_cars
        table.add_entries(self.entries, 'race_safety_cars_tiebreaker')

        entry_scores = {}
        for entry in self.entries.list_entries():
            entry_val = abs(total_safety_cars - entry.race_safety_cars_response)
            if entry_val not in entry_scores:
                entry_scores[entry_val] = {}
            tie_breaker_val = safety_car_dict[str(entry.race_safety_cars_tiebreaker)]
            if tie_breaker_val not in entry_scores[entry_val]:
                entry_scores[entry_val][tie_breaker_val] = [entry]
            else:
                 entry_scores[entry_val][tie_breaker_val].append(entry)
        
        score = Table(f"Final Scores: Correct Answer {total_safety_cars}", 
            'Entry', 'Points', int, show_entries=False, value_label="Guess")
        pos = 1
        
        for entry_score in sorted(entry_scores.keys()):
            for tie_breaker in reversed(sorted(entry_scores[entry_score])):
                for entry in entry_scores[entry_score][tie_breaker]:
                    entry_row = score.add_subject(F1_POINTS[pos], entry)
                    entry.add_points(F1_POINTS[pos])
                    entry_row.value = entry.race_safety_cars_response
                pos += len(entry_scores[entry_score][tie_breaker])
        
        return (table, score)


    def fewest_on_lead_lap(self):
        """
        Answer the qeustion "What is the fewest number of drivers that will 
         finish on the lead lap of any race?"
        
        Returns:
        An integer representing the lowest number of cars on the lead lap of
         a race
        """
        fewest_on_lead_lap = 21
        table = Table("Fewest on lead lap", 'Race', 'On Lead Lap', int, 
            show_values=False, show_entries=False, sort=None)
        for race in self.races.list_races_before(self.datetime):
            drivers_on_lead_lap = 0
            for driver in self.drivers.driver_list:
                if str(race) in driver.races:
                    driver_race_result = driver.races[str(race)]
                    if driver_race_result.laps == race.laps:
                        drivers_on_lead_lap += 1
            table.add_subject(drivers_on_lead_lap, race)
            if drivers_on_lead_lap < fewest_on_lead_lap:
                fewest_on_lead_lap = drivers_on_lead_lap
        
        entry_scores = {}
        for entry in self.entries.list_entries():
            entry_val = abs(fewest_on_lead_lap - entry.race_fewest_on_lead_lap_response)
            if entry_val not in entry_scores:
                entry_scores[entry_val] = [entry]
            else:
                entry_scores[entry_val].append(entry)
        
        score = Table(f"Final Scores: Correct Answer {fewest_on_lead_lap}", 
            'Entry', 'Points', int, show_entries=False, value_label="Guess")
        pos = 1
        for entry_score in sorted(entry_scores.keys()):
            for entry in entry_scores[entry_score]:
                entry_row = score.add_subject(F1_POINTS[pos], entry)
                entry.add_points(F1_POINTS[pos])
                entry_row.value = entry.race_fewest_on_lead_lap_response
            pos += len(entry_scores[entry_score])
        
        return (table, score)


    def russia_facts(self):
        """
        Answer the questions "How many drivers will take on soft tires in the 
         last 5 laps in Russia" and the tie breaker "What will be the total 
         number of laps run on softs by the race winner in Russia?"

        Returns:
        A set of two integers, the number of drivers that pitted for softs at 
         the end and the total number of laps on soft for the winner in Russia
        """
        # TODO: Map Entries
        pitted = self.single_answer_dict['Pitted for Softs in last five laps at Russia']
        winner_laps = self.single_answer_dict['Total laps on softs for winner at Russia']
        entry_dict = {}
        for entry in self.entries.list_entries():
            pitted_diff = abs(pitted - entry.russia_stop_for_softs_response)
            if pitted_diff not in entry_dict:
                entry_dict[pitted_diff] = {}
            winner_laps_diff = abs(winner_laps - entry.russia_stop_for_softs_tiebreaker)
            if winner_laps_diff not in entry_dict[pitted_diff]:
                entry_dict[pitted_diff][winner_laps_diff] = [entry]
            else:
                entry_dict[pitted_diff][winner_laps_diff].append(entry)

        score = Table(f"Final Scores: Correct Answer {pitted}, Tie Breaker {winner_laps}", 
            'Entry', 'Points', int, show_values=True, value_label="Guess")
        pos = 1
        for entry_score in sorted(entry_dict.keys()):
            for tie_breaker_score in sorted(entry_dict[entry_score].keys()):
                for entry in entry_dict[entry_score][tie_breaker_score]:
                    entry_row = score.add_subject(F1_POINTS[pos], entry)
                    entry.add_points(F1_POINTS[pos])
                    entry_row.value = entry.russia_stop_for_softs_response
                pos += len(entry_dict[entry_score][tie_breaker_score])
        score.add_entries(self.entries, 'entry_name', tie_breaker_var='russia_stop_for_softs_tiebreaker')
        return (None, score)


    def first_saudi_retirement(self):
        """
        Answer the question "Which driver that starts the race in Saudi Arabia 
         will be the first one out?" and the tie breaker "What WDC position 
         will that driver start the race in?"

        Returns:
        A set with the name of the first driver out of Saudi Arabia and the 
         position the driver occupies before the race
        """
        # TODO: Map Entries
        first_retirement = self.single_answer_dict['First retirement at Saudi Arabia']
        # Race has not occurred yet
        if first_retirement is None or len(first_retirement) == 0:
            return (None, None)
        driver = self.drivers.get_driver_by_short_name(first_retirement)
        previous_race = self.races.get_race_by_name('Australia')
        # Race has not occurred yet
        if previous_race is None or previous_race.post_race_driver_points is None:
            return (None, None)
        wdc_pos = previous_race.post_race_driver_points.get_position_of_entry(driver)
        return (first_retirement, wdc_pos)


    def btn_subscore_table(self, table_name, correct_score, entry_var):
        entry_dict = {}
        for entry in self.entries.list_entries():
            entry_diff = abs(correct_score - entry.__dict__[entry_var])
            if entry_diff not in entry_dict:
                entry_dict[entry_diff] = [entry]
            else:
                entry_dict[entry_diff].append(entry)

        score = Table(f"By The Numbers, {table_name} (Correct Answer: {correct_score})", 
            'Entry', 'Guess', int, value_label="Difference", sort='ascending',
            show_entries=False)
        for entry_diff in sorted(entry_dict.keys()):
            for entry in entry_dict[entry_diff]:
                entry_row = score.add_subject(entry.__dict__[entry_var], entry)
                entry_row.value = entry_diff
        return score

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
        score = self.btn_subscore_table('Unique Race Winners', len(winners), 
            'btn_unique_winners_response')
        return (len(winners), score)


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
        score = self.btn_subscore_table('Unique Pole Sitters', len(pole_sitters), 
            'btn_unique_pole_sitters_response')
        return (len(pole_sitters), score)


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
        score = self.btn_subscore_table('Unique Fastest Lap Winners', 
            len(fastest_lap_winners), 'btn_unique_fastest_lap_response')
        return (len(fastest_lap_winners), score)


    def wet_compound_races(self):
        """
        Answer the question "In how many races will the wet tire compound be used?"

        Returns:
        The number of races a wet compound was used
        """
        wet_tire_races = self.single_answer_dict['How many races have wet compound used']
        score = self.btn_subscore_table('Races With Wet Compounds Used', 
            wet_tire_races, 'btn_wet_compound_races_response')
        return (wet_tire_races, score)


    def in_season_leavings(self):
        """
        Answer the qeustion "How many drivers will be confirmed to leave F1 or 
         change teams DURING the season?"

        Returns:
        The number of drivers confirmed to change teams or leave F1 during the 
         season
        """
        confirmed_leavers = self.single_answer_dict['How many drivers confirmed to leave']
        score = self.btn_subscore_table('Drivers Confirmed to Leave During Season', 
            confirmed_leavers, 'btn_driver_departure_confirmed_response')
        return (confirmed_leavers, score)


    def track_invasions(self):
        """
        Answer the question "How many races will have track invasions by 
         animals?"

        Returns:
        The number of track invasions and 
        """
        track_invasions = self.single_answer_dict['How many races with animal invasions']
        score = self.btn_subscore_table('Animal Track Invasions', 
            track_invasions, 'btn_animal_invasions_response')
        return (track_invasions, score)


    def total_drivers(self):
        """
        Answer the qustion "How many total drivers this season?" This is the 
         tie breaker for the "By the Numbers" section

        Returns:
        Total number of drivers for the season
        """
        total_drivers = len(self.drivers.driver_list)
        score = self.btn_subscore_table('Tie Breaker: Total Drivers', 
            total_drivers, 'btn_total_drivers_tiebreaker')
        return (total_drivers, score)

    
    def by_the_numbers(self):
        race_winners, rw_table = self.unique_race_winners()
        pole_sitters, ps_table = self.unique_pole_sitters()
        fastest_lappers, fl_table = self.unique_fastest_lap()
        wet_tires, wt_table = self.wet_compound_races()
        confirmed_leavers, cl_table = self.in_season_leavings()
        animal_invasions, ai_table = self.track_invasions()
        total_drivers, td_table = self.total_drivers()

        correct_sum = race_winners + pole_sitters + fastest_lappers + wet_tires \
            + confirmed_leavers + animal_invasions
        
        entry_dict = {}
        for entry in self.entries.list_entries():
            entry_sum = entry.btn_unique_winners_response + \
                entry.btn_unique_pole_sitters_response + \
                entry.btn_unique_fastest_lap_response + \
                entry.btn_wet_compound_races_response + \
                entry.btn_driver_departure_confirmed_response + \
                entry.btn_animal_invasions_response
            entry_diff = abs(correct_sum - entry_sum)
            entry_tie_breaker = entry.btn_total_drivers_tiebreaker
            entry_tb_diff = abs(total_drivers - entry_tie_breaker)
            if entry_diff not in entry_dict:
                entry_dict[entry_diff] = {}
            if entry_tb_diff not in entry_dict[entry_diff]:
                entry_dict[entry_diff][entry_tb_diff] = [entry]
            else:
                entry_dict[entry_diff][entry_tb_diff].append(entry)

        score = Table(f"By The Numbers Final Scores: Correct Sum {correct_sum}, Tie Breaker (Total Drivers) {total_drivers}", 
            'Entry', 'Points', int, show_values=True, value_label="Guess")
        pos = 1
        for entry_score in sorted(entry_dict.keys()):
            for tie_breaker_score in sorted(entry_dict[entry_score].keys()):
                for entry in entry_dict[entry_score][tie_breaker_score]:
                    entry_row = score.add_subject(F1_POINTS[pos], entry)
                    entry.add_points(F1_POINTS[pos])
                    entry_sum = entry.btn_unique_winners_response + \
                        entry.btn_unique_pole_sitters_response + \
                        entry.btn_unique_fastest_lap_response + \
                        entry.btn_wet_compound_races_response + \
                        entry.btn_driver_departure_confirmed_response + \
                        entry.btn_animal_invasions_response
                    entry_row.value = entry_sum
                pos += len(entry_dict[entry_score][tie_breaker_score])
        score.add_entries(self.entries, 'entry_name', tie_breaker_var='btn_total_drivers_tiebreaker')
        return([rw_table, ps_table, fl_table, wt_table, cl_table, ai_table, td_table], score)


    def mini_bingo_sub(self, table_name, correct_answer, entry_var):
        correct_val = 1
        incorrect_val = -3
        if correct_answer == 'TRUE':
            correct_val = 5

        score = Table(f"Mini Bingo, {table_name} Correct Answer {correct_answer}", 
            'Entry', 'Guess', str, value_label="Points", sort='ascending',
            show_entries=False)
        for entry in self.entries.list_entries():
            entry_row = score.add_subject(entry.__dict__[entry_var], entry)
            if entry.__dict__[entry_var] == correct_answer:
                entry_row.value = correct_val
            else:
                entry_row.value = incorrect_val
            entry.add_points(entry_row.value)
        return score

    def pourchaire_seat(self):
        """
        Answer the question "Theo Pourchaire gets a 2022 F1 seat."

        Returns:
        A TRUE or FALSE (Strings due to string repr from questionaire)
        """
        answer = self.single_answer_dict['Does Theo Pourchaire have a 2022 seat']
        score = self.mini_bingo_sub('Theo Pourchaire gets a 2022 F1 seat.', answer, 
            'bingo_pourchaire_response')
        return score


    def lando_gets_a_podium(self):
        """
        Answer the qeustion "Lando Norris gets a podium."

        Returns:
        A TRUE or FALSE (Strings due to string repr from questionaire)
        """
        lando = self.drivers.get_driver_by_short_name('Norris, Lando')
        if lando is None:
            raise Exception('Lando not found')
        answer = 'FALSE'
        if lando.podiums > 0:
            answer = 'TRUE'
        score = self.mini_bingo_sub('Lando Norris gets a podium.', answer, 
            'bingo_norris_response')
        return score


    def williams_above_tenth(self):
        """
        Answer the question "Williams do not finish 10th."

        Returns:
        A TRUE or FALSE (Strings due to string repr from questionaire)
        """
        table = self.teams.get_points_table()
        tenth = table.get_subjects_by_pos(10)
        answer = 'TRUE'
        for row in tenth:
            if row.subject.name == 'Williams':
                answer = 'FALSE'
        score = self.mini_bingo_sub('Williams do not finish 10th.', answer, 
            'bingo_williams_response')
        return score


    def red_bull_driver_change(self):
        """
        Answer the qeustion "Red Bull changes drivers mid-season"

        Returns:
        A TRUE or FALSE (Strings due to string repr from questionaire)
        """
        answer = self.single_answer_dict['Has Red Bull changed drivers']
        score = self.mini_bingo_sub('Red Bull changes drivers mid-season', answer, 
            'bingo_red_bull_response')
        return score


    def all_20_finished(self):
        """
        Answer the question "At least one race has 20 classified finishers."

        Returns:
        A TRUE or FALSE (Strings due to string repr from questionaire)
        """
        answer = 'FALSE'
        for race in self.races.list_races_before(self.datetime):
            if race.retirements == 0:
                answer = 'TRUE'
        score = self.mini_bingo_sub('At least one race has 20 classified finishers.', answer, 
            'bingo_twenty_classifieds_response')
        return score


    def down_to_the_wire(self):
        """
        Answer the question "World Driver Championship goes all the way to the 
         final race."
        
        Returns:
        A TRUE or FALSE (Strings due to string repr from questionaire)
        """
        answer = 'FALSE'
        next_to_last = self.races.list_races_before(self.datetime)[-1]
        first = next_to_last.post_race_driver_points.get_subjects_by_pos(1)
        if len(first) > 1:
            answer = 'TRUE'
        second = next_to_last.post_race_driver_points.get_subjects_by_pos(2)
        remaining_races = self.races.list_races_after(self.datetime)
        if first[0].score - second[0].score <= (26 * len(remaining_races)):
            answer = 'TRUE'
        score = self.mini_bingo_sub('World Driver Championship goes all the way to the final race.', 
            answer, 'bingo_down_to_the_wire_response')
        return score


    def russell_outscores_someone(self):
        """
        Answer the question "Russell outscores a non-Williams driver."

        Returns:
        A TRUE or FALSE (Strings due to string repr from questionaire)
        """
        answer = 'FALSE'
        russell = self.drivers.get_driver_by_short_name("Russell, George")
        for driver in self.drivers.driver_list:
            if driver.team_name != 'Williams' and russell.points > \
                driver.points:
                answer = 'TRUE'
        score = self.mini_bingo_sub('Russell outscores a non-Williams driver.', 
            answer, 'bingo_russell_response')
        return score


    def mini_bingo(self):
        tables = []
        tables.append(self.pourchaire_seat())
        tables.append(self.lando_gets_a_podium())
        tables.append(self.williams_above_tenth())
        tables.append(self.red_bull_driver_change())
        tables.append(self.all_20_finished())
        tables.append(self.down_to_the_wire())
        tables.append(self.russell_outscores_someone())
        return(tables, None)
