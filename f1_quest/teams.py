import csv
import os

from f1_quest.tables import Table
from f1_quest.util import get_type_val

class TeamRaceResult():
    def __init__(self, race):
        self.race = race


class Team():
    def __init__(self, name, points_2020):
        self.drivers = {}
        self.race_results = {}
        self.points_2020 = points_2020
        self.races_2020 = 17
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
                points_2020 = get_type_val(row, self.header_row, 'Points 2020',
                    int)
                self.team_dict[name] = Team(name=name, points_2020=points_2020)


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
            table.add_entry(team.get_points(), team)

        return table


    def get_average_point_change_table(self):
        """
        Build a table on team points improvement over 2020

        Returns:
        A table of teams based on their points/race change from 2020
        """
        table = Table('Team Improvement from 2020', 'Team', 'Average Points Difference', float)
        for team in self.team_dict.values():
            avg_2020 = team.points_2020 / team.races_2020
            avg = team.get_points() / len(team.race_results.keys())
            table.add_entry(avg - avg_2020, team)
        return table

    def get_teammate_qualy_table(self):
        """
        Build a table based on a driver out qualifying their teammate

        Returns:
        A table of drivers based on their qualy wins over their teammate
        """
        table = Table('Qualy Wins over Teammate', 'Driver', 'Win Average', float)
        for team in self.team_dict.values():
            for driver in team.drivers.values():
                teammates = []
                for driver2 in team.drivers.values():
                    if driver != driver2:
                        teammates.append(driver2)
                table.add_entry(driver.qualy_win_pct(teammates), driver)
        return table