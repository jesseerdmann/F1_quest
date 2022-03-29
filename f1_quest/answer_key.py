import csv
import json
import os

from datetime import datetime
from f1_quest.drivers import Driver, Drivers
from f1_quest.entries import Entries
from f1_quest.races import Races
from f1_quest.tables import Table
from f1_quest.teams import Teams
from f1_quest.util import urlify_name


F1_POINTS = {1: 25, 2: 18, 3: 15, 4: 12, 5: 10, 6: 8, 7: 6, 8: 4, 9: 2, 10: 1, 
             11: 0, 12: 0, 13: 0, 14: 0, 15: 0, 16: 0, 17: 0, 18: 0, 19: 0, 20: 0}
SPRINT_POINTS = {1: 8, 2: 7, 3: 6, 4: 5, 5: 4, 6: 3, 7: 2, 8: 1, 9: 0, 10: 0, 
             11: 0, 12: 0, 13: 0, 14: 0, 15: 0, 16: 0, 17: 0, 18: 0, 19: 0, 20: 0}


class QuestionSummary():
    def __init__(self, data_dir, race, short_name, question, desc=None, answer=None, score=None, 
        entry_var=None, entry_tb=None):
        self.short_name = short_name
        self.question = question
        self.desc = desc
        self.answer = answer
        self.score = score
        self.entry_var = entry_var
        self.entry_tb = entry_tb
        self.results_table = {}
        self.race = race

        self.results_table_path = os.path.join(data_dir, '_'.join([urlify_name(self.short_name), 'results_table.json']))
        if os.path.exists(self.results_table_path):
            results_table_pointer = open(self.results_table_path, 'r')
            self.results_table = json.loads(results_table_pointer.read())

    
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


    def write_results_table(self):
        if self.score is not None:
            for subject in self.score.get_ordered_subjects():
                if str(str(subject.subject)) not in self.results_table: 
                    self.results_table[str(subject.subject)] = {}
                self.results_table[str(subject.subject)][self.race.name] = subject.score
        elif self.answer is not None:
            for subject in self.answer.get_ordered_subjects():
                for entry in subject.matching_entries:
                    if str(entry) not in self.results_table: 
                        self.results_table[str(entry)] = {}
                    self.results_table[str(entry)][self.race.name] = subject.value
        with open(self.results_table_path, 'w') as result_table_out:
            result_table_out.write(json.dumps(self.results_table))
        return self.results_table



class AnswerKey():
    def __init__(self, data_dir='data', datetime=datetime.now(), 
        file_name='scoring_single_answer.csv'):
        self.teams = Teams(data_dir=data_dir)
        self.drivers = Drivers(data_dir=data_dir)
        self.entries = Entries  (data_dir=data_dir, drivers=self.drivers)
        self.races = Races(data_dir=data_dir)
        self.datetime = datetime
        self.questions = []

        # Read scoring_single_answer.csv
        self.single_answer_dict = {}
        file_path = os.path.join(data_dir, file_name)
        if not os.path.exists(file_path):
            raise Exception(f"{file_path} not found, exiting.")
        with open(file_path, newline='') as file_pointer:
            file_reader = csv.reader(file_pointer, delimiter=',', quotechar='\'')
            for row in file_reader:
                self.single_answer_dict[row[0]] = row[1]

        current_race = self.races.list_races_before(datetime)[-1]

        # This needs to happen after the scoring_single_answer because of SPA half points
        self.races.read_results(data_dir=data_dir, drivers=self.drivers, 
            teams=self.teams, datetime=datetime)

        answer, score = self.team_fifth()
        self.questions.append(QuestionSummary(data_dir, current_race, 'Q1: Team Fifth',
            'Q1: Which team will finish fifth in the championship?',
            desc='Tie Breaker: How many points will the fifth place team get?',
            answer=answer, score=score, entry_var='team_fifth_response',
            entry_tb='team_fifth_tiebreaker'))
        
        answer, score = self.avg_points_increase()
        self.questions.append(QuestionSummary(data_dir, current_race, 
            'Q2: Average Points Increase',
            'Q2: Which team will have the highest points per race increase over 2020?',
            answer=answer, score=score, entry_var='team_points_avg_response'))
        
        answer, score = self.driver_of_the_day()
        self.questions.append(QuestionSummary(data_dir, current_race,  
            'Q3: Driver of the Day',
            'Q3: Who will win the most official "Driver of the Day" awards?',
            answer=answer, score=score, entry_var='driver_of_the_day_response'))

        answer, score = self.driver_tenth()
        self.questions.append(QuestionSummary(data_dir, current_race, 
            'Q4: Driver Tenth',
            'Q4: Which driver will finish 10th in the Championship?',
            desc='Tie Breaker: How many points did that driver get?',
            answer=answer, score=score, entry_var='driver_tenth_response',
            entry_tb='driver_tenth_tiebreaker'))

        answer, score = self.podium_winners()
        self.questions.append(QuestionSummary(data_dir, current_race, 
            'Q5 : Podium Winners',
            'Q5: Check every driver that will have a podium finish during the season.',
            desc='+5 for every correct, -3 for every incorrect guess, -3 for every missed podium',
            answer=answer, score=score, entry_var='driver_podium_response'))

        answer, score = self.avg_laps()
        self.questions.append(QuestionSummary(data_dir, current_race, 
            'Q6: Fewest Average Laps',
            'Q6: Which driver will have the lowest average race laps per race started?',
            answer=answer, score=score, entry_var='drvier_lowest_laps_avg'))

        answer, score = self.six_after_six()
        self.questions.append(QuestionSummary(data_dir, current_race, 
            'Q7: Top Six After Six',
            'Q7: Who will be the top six drivers after the first six races?',
            desc='\n'.join(['Right driver, right place (+5)',
                'Right driver, one place out (+3)', 
                'Right driver, two places out (+2)',
                'Right driver, 3 or more places out (+1)']),
            answer=answer, score=score, entry_var='driver_six_after_six'))

        answer, score = self.uninterrupted_leader()
        self.questions.append(QuestionSummary(data_dir, current_race, 
            'Q8: Uninterrupted Leader',
            'Q8: At which race will the champion move to the top of the standings and never drop out of the top spot?',
            desc='At which race does the #2 driver take an unbroken position in the championship?',
            answer=answer, score=score, entry_var='driver_unbroken_lead_response',
            entry_tb='driver_unbroken_lead_tiebreaker'))

        answer, score = self.retirements()
        self.questions.append(QuestionSummary(data_dir, current_race, 
            'Q9: Retirements',
            'Q9: Pick three races, each retirement from the chosen races will cost you -5 points.',
            answer=answer, score=score, entry_var='driver_race_retirements_response'))

        answer, score = self.fewest_on_lead_lap()
        self.questions.append(QuestionSummary(data_dir, current_race, 
            'Q10: Fewest on Lead Lap',
            'Q10: What is the fewest number of drivers that will finish on the lead lap of any race?',
            answer=answer, score=score, entry_var='race_fewest_on_lead_lap_response'))

        answer, score = self.first_saudi_retirement()
        self.questions.append(QuestionSummary(data_dir, current_race, 
            'Q11: Retiring to Saudi Arabia',
            'Q11: Which driver that starts the race in Saudi Arabia will be the first one out?',
            desc='Tie breaker: What WDC position will that driver start the race in?\n\nTBD after Saudi Arabian GP is run',
            answer=answer, score=score, entry_var='saudi_first_retirement_response',
            entry_tb='saudi_first_retirement_tiebrekaer'))

        answer, score = self.q3_appearances()
        self.questions.append(QuestionSummary(data_dir, current_race, 
            'Q12: Q3 Appearances',
            'Q12: Which driver from the bottom 6 teams last year will have the most appearances in the final round of qualifying (Q3) over the season?',
            answer=answer, score=score, entry_var='driver_q3s'))
        
        qnum = 13
        for driver in self.drivers.list_all_drivers():
            if driver.started_season:
                answer, score = self.driver_points_by_race(driver.name, f"fantasy_{driver.last_name}")
                self.questions.append(QuestionSummary(data_dir, current_race, 
                    f"Q{qnum}: Fantasy {driver.last_name}",
                    f"Q{qnum}: Pick a race for {driver.first_name} {driver.last_name} and get the points based on their finishing position",
                    answer=answer, score=score, entry_var=f"fantasy_{driver.last_name}"))
                qnum = qnum + 1

        answer, score = self.unique_race_winners()
        self.questions.append(QuestionSummary(data_dir, current_race, 
            f"Q{qnum}: Unique Race Winners",
            f"Q{qnum}: Unique Race Winners.", 
            desc="How many different drivers will win a race this season?",
            answer=answer, score=score, entry_var='btn_unique_winners_response'))
        qnum = qnum + 1

        answer, score = self.unique_pole_sitters()
        self.questions.append(QuestionSummary(data_dir, current_race, 
            f"Q{qnum}: Unique Pole Sitters",
            f"Q{qnum}: Unique Pole Sitters", 
            desc="How many different drivers will win pole position?",
            answer=answer, score=score, entry_var='btn_unique_pole_sitters_response'))
        qnum = qnum + 1

        answer, score = self.unique_fastest_lap()
        self.questions.append(QuestionSummary(data_dir, current_race, 
            f"Q{qnum}: Unique Fastest Lappers",
            f"Q{qnum}: Unique Fastest Lappers", 
            desc="How many different drivers will finish with the fastest lap of the race?",
            answer=answer, score=score, entry_var='btn_unique_fastest_lap_response'))
        qnum = qnum + 1

        answer, score = self.mini_bingo()
        self.questions.append(QuestionSummary(data_dir, current_race, 
            f"Q{qnum}: Mini-Bingo", f"Q{qnum}: Mini-Bingo",
            desc='Correctly True: +5, Correctly False: +1, Incorrect: -3',
            answer=answer, score=score, entry_var=list(zip(['Pourchaire in 2022',
                'Yuki Gets a Podium', 'Haas Finishes Above 10th', 
                'All 20 Drivers Classified in One Race',
                'World Driver Championship Goes to Final Race', 
                'Schumacher Outscores a Driver That is Not a Teammate'], [
                'bingo_pourchaire_response',
                'bingo_yuki_response',
                'bingo_haas_response',
                'bingo_twenty_classifieds_response',
                'bingo_down_to_the_wire_response',
                'bingo_schumacher_response']))))


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
                    entry_tb_score = abs(entry.__dict__[tie_breaker_var] - tie_breaker)
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


    def team_fifth(self):
        '''
        Provide the answer key for the question "Which team will finish fifth
         in the championship?" and its tiebreaker, "How many points will the 
         fifth place team collect?"

        Returns:
        A dictionary mapping team names to point value if chosen, and the tiebreaker
        value
        '''
        team_points = self.teams.get_points_table()
        score_map = { 5: 25, 4: 18, 6: 18, 3: 15, 7: 15, 2: 12, 8: 12, 1: 10, 9: 10,
            10: 8 }
        team_points.add_entries(self.entries, 'team_fifth_response', 
                                'team_fifth_tiebreaker')
        team_points.show_values = False
        answer_key, tie_breaker = self.map_table_to_score(team_points, 
                                                          score_map, 
                                                          tie_breaker_pos=5)

        entry_table = self.tie_breaker_scoring("Final Scores", 
                                               score_map, team_points,
                                               tie_breaker, 
                                               'team_fifth_tiebreaker')

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


    def q3_appearances(self):
        """
        Answer the question "Which driver in the bottom six teams will have
         the most Q3 appearances?

        Returns:
        A dictionary mapping driver names to point value if chosen
        """
        q3s_table = self.teams.get_q3_appearances_table(self.drivers)
        q3s_table.add_entries(self.entries, 'driver_q3s')
        score_map = {1: 25, 2: 18, 3: 15, 4: 12, 5: 10, 6: 8, 7: 6, 8: 4,
            9: 2, 10: 1, 11: 0, 12: 0}
        answer_key, tie_breaker = self.map_table_to_score(q3s_table, 
            score_map, update_entry_score=True)
        return (q3s_table, None)


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


    def break_driver_tie(self, drivers):
        win_dict = {}
        for driver in drivers:
            if driver.subject.wins in win_dict:
                win_dict[driver.subject.wins].append(driver)
            else:
                win_dict[driver.subject.wins] = [driver]
        result = []
        for win_count in reversed(sorted(win_dict.keys())):
            result.append(win_dict[win_count])
        return result


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
            first_name = ''
            second_name = ''
            # Determine first
            first_drivers = race.post_race_driver_points.get_subjects_by_pos(1)
            # Use tie breaker
            if len(first_drivers) > 1:
                sorted_drivers = self.break_driver_tie(first_drivers)
                if len(sorted_drivers[0]) > 1:
                    first_name = "Tie: " + ", ".join(sorted_drivers[0])
                    second_name = "Tie: " + ", ".join(sorted_drivers[0])
                else:
                    first_name = sorted_drivers[0][0].subject.name
                    if len(sorted_drivers[1]) > 1:
                        second_name = "Tie: " + ", ".join(sorted_drivers[1])
                    else:
                        second_name = sorted_drivers[1][0].subject.name
            else:
                first_name = first_drivers[0].subject.name
                second_drivers = race.post_race_driver_points.get_subjects_by_pos(2)
                # Use tie breaker
                if len(second_drivers) > 1:
                    sorted_drivers = self.break_driver_tie(second_drivers)
                    if len(sorted_drivers[0]) > 1:
                        second_name = "Tie: " + ", ".join(sorted_drivers[0])
                    else:
                        second_name = sorted_drivers[0][0].subject.name
                else:
                    second_name = second_drivers[0].subject.name

            if places_dict[1]['driver'] != first_name:
                places_dict[1]['driver'] = first_name
                places_dict[1]['race'] = race
            if places_dict[2]['driver'] != second_name:
                places_dict[2]['driver'] = second_name
                places_dict[2]['race'] = race    

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
            else:
                sorting_dict[off_by][tie_breaker].append(entry)

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


    def driver_points_by_race(self, driver_short_name, entry_var):
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
        score_map = {1: 25, 2: 18, 3:15, 4: 12, 5: 10, 6: 8, 7: 6, 8: 4, 9: 2, 10: 1, 
                     20: -25, 19: -18, 18: -15, 17: -12, 16: -10, 15: -8, 14: -6, 13: -4, 12: -2, 11: -1}
        driver = self.drivers.get_driver_by_short_name(driver_short_name)
        if driver is None:
            raise Exception(f"No driver matches found for {driver_short_name}")

        for race, result in driver.races.items():
            if result.classification >= 0:
                race_dict[race] = score_map[result.classification]
        
        table = Table(f"{driver_short_name} Points", "Race", "Points", int, 
            show_values=False, sort=None)
        for race in self.races.list_races():
            if race.name in race_dict:
                table.add_subject(race_dict[race.name], race)
            else:
                table.add_subject(0, race)
        table.add_entries(self.entries, entry_var)

        scores = Table("Final Score", "Entry", "Points", int, 
            show_values=False, show_entries=False)
        for entry in self.entries.list_entries():
            entry_score = 0
            race_name = str(entry.__dict__[entry_var])
            race = self.races.get_race_by_str(race_name)
            if race.name in race_dict:
                entry_score = race_dict[race.name]
            scores.add_subject(entry_score, entry)
            entry.add_points(entry_score)
        
        return (table, scores)


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
        driver_order = json.loads(first_retirement)
        race = self.races.get_race_by_name('Saudi Arabia')
        # Race has not occurred yet
        if race is None or race.post_race_driver_points is None:
            return (None, None)
        wdc_pos = 16
        
        table = Table("First Retirement in Saudi Arabia", 'Driver', 'Retirement Position', int, 
            show_values=False, show_entries=True, sort="ascending")
        pos = 1
        driver_scores = {}
        for driver in driver_order:
            driver_scores[driver] = pos
            table.add_subject(pos, driver)
            pos += 1
        table.add_entries(self.entries, 'saudi_first_retirement_response',
                          'saudi_first_retirement_tiebreaker')
        
        entry_scores = {}
        for entry in self.entries.list_entries():
            entry_val = driver_scores[entry.saudi_first_retirement_response]
            if entry_val not in entry_scores:
                entry_scores[entry_val] = {}
            tie_breaker_val = abs(wdc_pos-entry.saudi_first_retirement_tiebreaker)
            if tie_breaker_val not in entry_scores[entry_val]:
                entry_scores[entry_val][tie_breaker_val] = [entry]
            else:
                 entry_scores[entry_val][tie_breaker_val].append(entry)
        
        score = Table(f"Final Scores: Correct Answer Nicholas Latifi (tiebreaker: {wdc_pos})", 
            'Entry', 'Points', int, show_values=False, show_entries=False, value_label="Tiebreaker Guess")
        pos = 1
        for entry_score in sorted(entry_scores.keys()):
            for tie_breaker in sorted(entry_scores[entry_score]):
                for entry in entry_scores[entry_score][tie_breaker]:
                    entry_row = score.add_subject(F1_POINTS[pos], entry)
                    entry.add_points(F1_POINTS[pos])
                    entry_row.value = entry.saudi_first_retirement_tiebreaker
                pos += len(entry_scores[entry_score][tie_breaker])
        
        return (table, score)


    def btn_subscore_table(self, table_name, correct_score, entry_var):
        entry_dict = {}
        for entry in self.entries.list_entries():
            entry_diff = abs(correct_score - entry.__dict__[entry_var])
            if entry_diff not in entry_dict:
                entry_dict[entry_diff] = [entry]
            else:
                entry_dict[entry_diff].append(entry)
        from pprint import pprint

        score = Table(f"{table_name} (Correct Answer: {correct_score})", 
            'Entry', 'Miss Amount', int, value_label="Score", sort='ascending',
            show_entries=False)
        pos = 1
        for entry_diff in sorted(entry_dict.keys()):
            for entry in entry_dict[entry_diff]:
                entry_row = score.add_subject(entry_diff, entry)
                entry.add_points(F1_POINTS[pos])
                entry_row.value = F1_POINTS[pos]
            pos += len(entry_dict[entry_diff])
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
        return (None, score)


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
        return (None, score)


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
        return (None, score)


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


    def yuki_gets_a_podium(self):
        """
        Answer the qeustion "Yuki Norris gets a podium."

        Returns:
        A TRUE or FALSE (Strings due to string repr from questionaire)
        """
        yuki = self.drivers.get_driver_by_short_name('Tsunoda, Yuki')
        if yuki is None:
            raise Exception('Yuki not found')
        answer = 'FALSE'
        if yuki.podiums > 0:
            answer = 'TRUE'
        score = self.mini_bingo_sub('Yuki Tsunoda gets a podium.', answer, 
            'bingo_yuki_response')
        return score


    def haas_above_tenth(self):
        """
        Answer the question "Haas do not finish 10th."

        Returns:
        A TRUE or FALSE (Strings due to string repr from questionaire)
        """
        table = self.teams.get_points_table()
        tenth = table.get_subjects_by_pos(10)
        answer = 'TRUE'
        for row in tenth:
            if row.subject.name == 'Haas':
                answer = 'FALSE'
        score = self.mini_bingo_sub('Haas do not finish 10th.', answer, 
            'bingo_haas_response')
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
        # Hacking answer in because it was true heading into the final race and it doesn't make 
        # sense to figure out how to recognize that it was true at this point.
        answer = 'TRUE'
        score = self.mini_bingo_sub('World Driver Championship goes all the way to the final race.', 
            answer, 'bingo_down_to_the_wire_response')
        return score


    def schumacher_outscores_someone(self):
        """
        Answer the question "Russell outscores a non-Haas driver."

        Returns:
        A TRUE or FALSE (Strings due to string repr from questionaire)
        """
        answer = 'FALSE'
        schumacher = self.drivers.get_driver_by_short_name("Schumacher, Mick")
        for driver in self.drivers.driver_list:
            if driver.team_name != 'Haas' and schumacher.points > \
                driver.points:
                answer = 'TRUE'
        score = self.mini_bingo_sub('Schumacher outscores a non-Haas driver.', 
            answer, 'bingo_schumacher_response')
        return score


    def mini_bingo(self):
        tables = []
        tables.append(self.pourchaire_seat())
        tables.append(self.yuki_gets_a_podium())
        tables.append(self.haas_above_tenth())
        tables.append(self.all_20_finished())
        tables.append(self.down_to_the_wire())
        tables.append(self.schumacher_outscores_someone())
        totals = {}
        for table in tables:
            for table_row in table.get_ordered_subjects():
                if table_row.subject in totals:
                    totals[table_row.subject] += table_row.value
                else:
                    totals[table_row.subject] = table_row.value
        score = Table("Mini-Bingo Totals", 'Entry', 'Points', int, 
            show_entries=False, show_values=False)
        for entry in self.entries.list_entries():
            entry_row = score.add_subject(totals[entry], entry)
            entry.add_points(entry_row.score)
        return(tables, score)
