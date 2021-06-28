import csv
import os

from f1_quest.tables import Table


class DriverRaceResult():
    def __init__(self, race, points, dis_points, qpos, laps, fastest_lap=False, driver_of_the_day=False):
        self.race = race
        self.points = points
        self.dis_points = dis_points
        self.qpos = qpos
        self.laps = laps
        self.fastest_lap = fastest_lap
        self.driver_of_the_day = driver_of_the_day


class Driver:
    def __init__(self, first_name, last_name, team_name, started_season):
        self.first_name = first_name
        self.last_name = last_name
        self.team_name = team_name
        self.name = f"{self.last_name}, {self.first_name}"
        self.entry_rep = f"{self.first_name} {self.last_name}, {self.team_name}"
        self.started_season = started_season == 'yes'
        self.points = 0
        self.dis_points = 0
        self.races = {}
        self.podiums = 0
        self.poles = 0
        self.driver_of_the_day = 0
        self.fastest_laps = 0
        self.wins = 0


    def __str__(self):
        return self.entry_rep


    def __lt__(self, other):
        return self.name < other.name


    def __eq__(self, other):
        return self.name == other.name


    def add_race(self, race, points, dis_points, qpos, laps, fastest_lap=False,
        driver_of_the_day=False):

        if type(points) == str or points < 0:
            return self
        
        self.races[race] = DriverRaceResult(race=race, points=points, 
            dis_points=dis_points, qpos=qpos, laps=laps, 
            fastest_lap=fastest_lap, driver_of_the_day=driver_of_the_day)
        self.points += points
        self.dis_points += dis_points
        if qpos == 1:
            self.poles += 1
        if points >= 15:
            self.podiums += 1
        if points >= 25:
            self.wins += 1
        if driver_of_the_day:
            self.driver_of_the_day += 1
        if fastest_lap:
            self.fastest_laps += 1


    def get_avg_laps(self):
        races = 0
        total_laps = 0
        for race, race_result in  self.races.items():
            if race_result.laps >= 0:
                races += 1
                total_laps += race_result.laps
        return total_laps/races


    def qualy_win_pct(self, others):
        """
        Determine the win percentage in qualifying versus a list of drivers

        Keyword arguments:
        others -- a list of Driver objects

        Returns:
        The percentage of times the driver out qualified the others
        """
        other_best_pos_dict = {}
        qualy_count = 0
        for driver in others:
            for race_result in driver.races.values():
                if race_result.race not in other_best_pos_dict or \
                    (race_result.qpos > 0 and 
                     race_result.qpos < other_best_pos_dict[race_result.race]):
                    other_best_pos_dict[race_result.race] = race_result.qpos
        
        wins = 0
        for race_result in self.races.values():
            if race_result.race in other_best_pos_dict and race_result.qpos > 0 \
                and race_result.qpos < other_best_pos_dict[race_result.race]:
                wins += 1
            if race_result.qpos > 0 and other_best_pos_dict[race_result.race] > 0:
                qualy_count += 1
        return wins/qualy_count


class Drivers:
    def __init__(self, data_dir=os.getenv('F1_DATA', 'data'), file_name="drivers.csv"):
        """
        Parse a CSV into a list of Driver objects

        Keyword arguments:
        data_dir -- The directory to find the csv, will read $F1_DATA or default to data
        file_name -- The name of the csv in data_dir, defaults to drivers.csv
        """
        self.driver_list = []
        file_path = os.path.join(data_dir, file_name)
        if not os.path.exists(file_path):
            raise Exception(f"{file_path} not found, exiting.")
        header_row = True
        with open(file_path, newline='') as file_pointer:
            file_reader = csv.reader(file_pointer, delimiter=',', quotechar='"')
            for row in file_reader:
                if header_row:
                    header_row = False
                    continue
                self.driver_list.append(Driver(first_name=row[0], last_name=row[1], 
                    team_name=row[2], started_season=row[5]))


    def list_all_drivers(self):
        """
        Get a sorted list of all drivers that have driven this season

        Returns:
        A sorted list of drivers
        """
        return sorted(self.driver_list)


    
    def list_drivers_that_started_season(self):
        """
        Get a sorted list of all drivers that started the season as a full-time
        driver

        Returns:
        A sorted list of drivers that started the season as a full-time driver
        """
        driver_list = [driver for driver in self.driver_list if 
            driver.started_season]
        return sorted(driver_list)


    def list_teams(self):
        team_set = set()
        for driver in self.driver_list:
            team_set.add(driver.team_name)
        return sorted(team_set)


    def get_driver_by_name(self, first_name=None, last_name=None, team_name=None):
        """
        Will return a list of matching drivers

        Keyword arguments:
        first_name -- the expected first name of the driver to return
        last_name -- the expected last name of the driver to return
        team_name -- the expected team name of the driver to return

        Returns:
        A list of drivers match the provided names or an empty list
        """ 
        drivers = []
        for driver in self.driver_list:
            if first_name is not None and first_name != driver.first_name:
                continue
            if last_name is not None and last_name != driver.last_name:
                continue
            if team_name is not None and team_name != driver.team_name:
                continue
            drivers.append(driver)
        return drivers

    
    def get_driver_by_short_name(self, short_name):
        """
        Find drivers matching the provided short name

        Keyword arguments:
        short_name -- the name to be searched for

        Returns:
        A list of all driver objects with a matching short name
        """
        for driver in self.driver_list:
            if driver.name == short_name:
                return driver
        return None

    
    def get_driver_by_entry_rep(self, entry_rep):
        """
        Find drivers matching the provided entry rep

        Keyword arguments:
        entry_rep -- the rep to be searched for

        Returns:
        The driver objects with a matching entry rep
        """
        for driver in self.driver_list:
            if driver.entry_rep == entry_rep:
                return driver
        return None

    
    def get_points_table(self):
        """
        Build a table with all of the drivers based on points

        Returns:
        A populated table object with drivers and points
        """
        table = Table('Driver Standings', 'Driver', 'Points', int)
        for driver in self.driver_list:
            table.add_subject(driver.points, driver)
        return table

    
    def get_dis_points_table(self):
        """
        Build a table with all of the drivers based on discipline points

        Returns:
        A populated table object with drivers and discipline points
        """
        table = Table('Driver Standings', 'Driver', 'Discipline Points', int)
        for driver in self.driver_list:
            table.add_subject(driver.dis_points, driver)
        return table


    def get_avg_laps_table(self):
        """
        Build a table based on the drivers' avg number of laps, lowest on top

        Returns:
        A table object with drivers and average laps
        """
        table = Table('Driver Average Laps', 'Driver', 'Average Laps', float, 
            sort='ascending')
        for driver in self.driver_list:
            # table.add_subject(driver.laps/len(driver.races), driver)
            table.add_subject(driver.get_avg_laps(), driver)
        return table


    def get_podiums_table(self):
        """
        Build a table based on drivers' appearances on podiums

        Returns:
        A table object with drivers and podium finishes
        """
        table = Table('Podiums', 'Driver', 'Podium Finishes', int)
        for driver in self.driver_list:
            table.add_subject(driver.podiums, driver)
        return table

    
    def get_winners_table(self):
        """
        Build a table based on drivers' wins

        Returns:
        A table object with drivers and wins
        """
        table = Table('Winners', 'Driver', 'Wins', int)
        for driver in self.driver_list:
            table.add_subject(driver.wins, driver)
        return table


    def get_poles_table(self):
        """
        Build a table based on drivers' starts on pole

        Returns:
        A table object with drivers and starts on pole
        """
        table = Table('Pole Position', 'Driver', 'Starts on Pole', int)
        for driver in self.driver_list:
            table.add_subject(driver.poles, driver)
        return table


    def get_driver_of_the_day_table(self):
        """
        Build a table based on drivers' driver of the day wins

        Returns:
        A table object with drivers and driver of the day wins
        """
        table = Table('Driver of the Day', 'Driver', 'DotD Wins', int)
        for driver in self.driver_list:
            table.add_subject(driver.driver_of_the_day, driver)
        return table


    def get_fastest_laps_table(self):
        """
        Build a table based on drivers' fastest lap points

        Returns:
        A table object with drivers and fastest lap points
        """
        table = Table('Fastest Lap', 'Driver', 'Fastest Lap Wins', int)
        for driver in self.driver_list:
            table.add_subject(driver.fastest_laps, driver)
        return table
