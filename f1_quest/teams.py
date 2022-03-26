import csv
import os

from f1_quest.tables import Table
from f1_quest.util import get_type_val

class TeamRaceResult():
    def __init__(self, race):
        self.race = race


class Team():
    def __init__(self, name, points_last_year):
        self.drivers = {}
        self.race_results = {}
        self.points_last_year = points_last_year
        self.races_last_year = 22
        self.name = name


    def __str__(self):
        return self.name


    def __lt__(self, other):
        return self.name < other.name


    def __eq__(self, other):
        return self.name == other.name


    def add_driver(self, driver):
        self.drivers[driver.name] = driver


    def add_race(self, race):
        self.race_results[race] = TeamRaceResult(race)


    def get_points(self):
        """
        Add the points of drivers in the team

        Returns:
        The teams total points
        """
        points = 0
        for driver in self.drivers.values():
            points += driver.points
        return points


class Teams():
    def __init__(self, data_dir=os.getenv('F1_DATA', 'data'), file_name="teams.csv"):
        """
        Parse a CSV into a list of Driver objects

        Keyword arguments:
        data_dir -- The directory to find the csv, will read $F1_DATA or default to data
        file_name -- The name of the csv in data_dir, defaults to drivers.csv
        """
        self.team_dict = {}
        file_path = os.path.join(data_dir, file_name)
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
                name = row[0]
                points_last_year = get_type_val(row, self.header_row, 'Points 2021',
                    float)
                self.team_dict[name] = Team(name=name, points_last_year=points_last_year)


    def add_drivers(self, drivers):
        """
        Iterate through the drivers then assign them by team_name

        Keyword arguments:
        drivers -- The Drivers object with all of the drivers
        """
        for driver in drivers.list_all_drivers():
            team = self.get_team_by_name(driver.team_name)
            team.add_driver(driver)

    
    def get_team_by_name(self, name):
        """
        Find the team with the corresponding name

        Keyword arguments:
        name -- the name of the desired team

        Returns:
        The Team object or None
        """
        if name in self.team_dict:
            return self.team_dict[name]
        else:
            return None


    def list_all_teams(self):
        """
        Return an ordered list of the teams

        Returns:
        An alphabetized list of the teams
        """
        team_list = []
        for team in sorted(self.team_dict.keys()):
            team_list.append(self.team_dict[team])
        return team_list


    def get_points_table(self):
        """
        Return a table of teams sorted by points. Must be calculated from 
         the team's driver's points.

        Returns:
        A table where the entries are teams by points
        """
        team_points = {}
        # Sum points from drivers
        table = Table('Team Points', 'Team', 'Points', int)
        for team_name, team in self.team_dict.items():
            table.add_subject(team.get_points(), team)

        return table


    def get_q3_appearances_table(self, drivers):
        """
        Build a table based on the drivers' Q3 appearances if in the bottom
        six teams last season

        Returns:
        A table object with drivers and Q3 appearances
        """
        table = Table('Driver Q3 appearances', 'Driver', 'Q3 Appearances', int)
        for team in self.list_all_teams():
            if team.name in ['Alfa Romeo Racing', 'Alpine', 'AlphaTauri', 'Aston Martin', 'Haas F1 Team', 'Williams']:
                for driver_name in team.drivers:
                    driver = drivers.get_driver_by_short_name(driver_name)
                    if driver.started_season:
                        table.add_subject(driver.q3s, driver)
        return table


    def get_average_point_change_table(self):
        """
        Build a table on team points improvement over last year

        Returns:
        A table of teams based on their points/race change from Last Year
        """
        table = Table('Team Improvement from Last Year', 'Team', 'Average Points Difference', float)
        for team in self.team_dict.values():
            avg_last_year = team.points_last_year / team.races_last_year
            avg = team.get_points() / len(team.race_results.keys())
            table.add_subject(avg - avg_last_year, team)
        return table