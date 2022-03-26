import csv
import os


class Entry():
    def __init__(self, row, drivers):
        self.score = 0
        self.timestamp = row[0]
        self.entry_name = row[1]
        self.color = row[50]
        self.email = row[51]
        self.team_fifth_response = row[2]
        self.team_fifth_tiebreaker = int(row[3])
        self.team_points_avg_response = row[4]
        self.driver_of_the_day_response = row[5]
        self.driver_tenth_response = row[6]
        self.driver_tenth_tiebreaker = int(row[7])
        self.driver_q3s = row[8]   

        # Reconstitute drivers after splitting on the comma
        driver_split = row[9].split(', ')
        self.driver_podium_response = []
        for i in range(0, len(driver_split), 2):
            self.driver_podium_response.append(', '.join([driver_split[i], driver_split[i+1]]))
        
        self.drvier_lowest_laps_avg = row[10]
        self.driver_six_after_six = [row[11], row[12], row[13], row[14], 
            row[15], row[16]]
        self.driver_unbroken_lead_response = row[17]
        self.driver_unbroken_lead_tiebreaker = row[18]
        self.driver_race_retirements_response = row[19].split(', ')

        self.race_fewest_on_lead_lap_response = int(row[20])
        self.saudi_first_retirement_response = row[21]
        self.saudi_first_retirement_tiebreaker = int(row[22])
        self.btn_unique_winners_response = int(row[23])
        self.btn_unique_pole_sitters_response = int(row[24])
        self.btn_unique_fastest_lap_response = int(row[25])
        self.bingo_pourchaire_response = row[26]
        self.bingo_yuki_response = row[27]
        self.bingo_haas_response = row[28]
        self.bingo_twenty_classifieds_response = row[29]
        self.bingo_down_to_the_wire_response = row[30]
        self.bingo_schumacher_response = row[31]

        # Get fantasy driver races
        index = 32
        #self.fantasy_drivers = {}
        for driver in drivers.list_all_drivers():
            if driver.started_season:
                self.__dict__[f"fantasy_{driver.last_name}"] = row[index]
                index += 1


    def __str__(self):
        return self.entry_name


    def __lt__(self, other):
        return self.entry_name < other.entry_name


    def add_points(self, points):
        self.score += points
        

class Entries():
    def __init__(self, drivers, data_dir=os.getenv('F1_DATA', 'data'), file_name="entries.csv"):
        self.entries = {}
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
                self.entries[row[1]] = Entry(row, drivers)


    def list_entries(self):
        return sorted(self.entries.values())
    
