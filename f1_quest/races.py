import csv
import os

from datetime import datetime
from f1_quest.util import get_type_val


class Race():
    def __init__(self, datetime, name, circuit, laps):
        self.datetime = datetime
        self.name = name
        self.circuit = circuit
        self.retirements = 0
        self.safety_cars = 0
        self.laps = laps
        self.post_race_driver_points = None


    def __lt__(self, other):
        return self.datetime < other.datetime


    def __eq__(self, other):
        return self.datetime == other.datetime

    
    def __str__(self):
        return f"{self.datetime.strftime('%m/%d/%Y %I:%M %p')}: {self.name} @ {self.circuit}"

    
    def add_results(self, retirements, safety_cars):
        self.retirements = retirements
        self.safety_cars = safety_cars



class Races:
    def __init__(self, data_dir=os.getenv('F1_DATA', 'data'), file_name="races.csv"):
        """
        Parse a CSV into a list of Race objects

        Keyword arguments:
        data_dir -- The directory to find the csv, will read $F1_DATA or default to data
        race_file_name -- The name of the csv in data_dir, defaults to races.csv
        results_file_name -- The name of the csv in data_dir, defaults to race_results.csv
        """
        self.race_list = []
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
                self.race_list.append(Race(datetime=datetime.strptime(
                    f"{row[0]} {row[1]}", '%B %d, %Y %I:%M %p'), name=row[2], 
                    circuit=row[3], laps=int(row[5])))

    
    def list_races(self):
        """
        Return a sorted list of races by datetime

        Returns:
        Sorted list of Race objects by datetime
        """
        return sorted(self.race_list)


    def list_races_before(self, datetime=datetime.now()):
        """
        List the races before a specified time

        Keyword arguments:
        datetime -- the time to compare races to, defaults to datetime.now()

        Returns:
        Sorted list of Race objects before the specfied time 
        """
        return sorted([race for race in self.race_list if race.datetime < datetime])


    def list_races_after(self, datetime=datetime.now()):
        """
        List the races after a specified time

        Keyword arguments:
        datetime -- the time to compare races to, defaults to datetime.now()

        Returns:
        Sorted list of Race objects after the specfied time 
        """
        return sorted([race for race in self.race_list if race.datetime > datetime])

    
    def get_race_by_date(self, date=datetime.now()):
        """
        Return a specfic race with a given date

        Keyword arguments:
        date -- a date object for the desired day, defaults to datetime.now()

        Returns:
        A corresponding race object or None
        """
        for race in self.race_list:
            if date.date() == race.datetime.date():
                return race
        return None

    
    def get_race_by_str(self, string):
        """
        Return a specific race given its full __str__() representation

        Keyword arguments:
        string -- the desired race's string repr

        Returns:
        The Race object that matches or None
        """
        for race in self.race_list:
            if race.__str__() == string:
                return race
        return None


    def get_race_by_name(self, name):
        """
        Return a specific race given its GP name

        Keyword arguments:
        name -- the desired race's GP name

        Returns:
        The Race object that matches or None
        """
        for race in self.race_list:
            if race.name == name:
                return race
        return None


    def read_results(self, drivers, teams, 
        data_dir=os.getenv('F1_DATA', 'data'), file_name="race_results.csv",
        datetime=datetime.now()):
        file_path = os.path.join(data_dir, file_name)

        # Ensure teams have the correct list of drivers
        teams.add_drivers(drivers)

        if not os.path.exists(file_path):
            raise Exception(f"{file_path} not found, exiting.")
        self.header_row = None
        with open(file_path, newline='') as file_pointer:
            file_reader = csv.reader(file_pointer, delimiter=',', quotechar='"')
            for row in file_reader:
                if self.header_row is None:
                    self.header_row = {}
                    for header, idx in zip(row, range(0, len(row))):
                        self.header_row[header] = idx
                    continue
                race = self.get_race_by_str(row[0])
                # Only read races that have completed
                if race.datetime > datetime:
                    continue
                retirements = get_type_val(row, self.header_row, 
                    'Retirements', int)
                safety_cars = get_type_val(row, self.header_row, 
                    'Safety Cars', int)
                race.add_results(retirements=retirements, 
                    safety_cars=safety_cars)
                for team in teams.list_all_teams():
                    team_fps = get_type_val(row, self.header_row, 
                        ' '.join([team.name, 'FPS']), float)
                    team.add_race(row[0], team_fps)
                for driver in drivers.list_all_drivers():
                    driver_of_the_day = driver.name == get_type_val(row, 
                        self.header_row, 'Driver of the Day')
                    fastest_lap_winner = driver.name == get_type_val(row,
                        self.header_row, 'Fastest Lap Winner')
                    points = get_type_val(row, self.header_row, 
                        ' '.join([driver.name, 'Pts']), int)
                    dis_points = get_type_val(row, self.header_row, 
                        ' '.join([driver.name, 'Dis Pts']), int)
                    qpos = get_type_val(row, self.header_row, 
                        ' '.join([driver.name, 'QPos']), int)
                    laps = get_type_val(row, self.header_row, 
                        ' '.join([driver.name, 'Laps']), int)
                    driver.add_race(race=row[0], points=points, 
                        dis_points=dis_points, qpos=qpos, laps=laps, 
                        driver_of_the_day=driver_of_the_day,
                        fastest_lap=fastest_lap_winner)
                
                # Get post-race driver points
                race.post_race_driver_points = drivers.get_points_table()
