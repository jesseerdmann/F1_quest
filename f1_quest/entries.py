import csv
import os


class Entry():
    def __init__(self, row):
        self.score = 0
        self.timestamp = row[0]
        self.entry_name = row[1]
        self.team_fourth_response = row[2]
        self.team_fourth_tiebreaker = row[3]
        self.team_points_avg_response = row[4]
        self.team_fps_response = row[5]
        self.driver_of_the_day_response = row[6]
        self.driver_tenth_response = row[7]
        self.driver_tenth_tiebreaker = row[8]
        self.driver_qualy_dominance = row[9]
        self.driver_podium_response = row[10]
        self.driver_penalty_points = row[11]
        self.drvier_lowest_laps_avg = row[12]
        self.driver_six_after_six = [row[13], row[14], row[15], row[16], 
            row[17], row[18]]
        self.driver_unbroken_lead_response = row[19]
        self.driver_unbroken_lead_tiebreaker = row[20]
        self.driver_race_retirements_response = row[21]
        self.driver_gasly_ponts_response = row[22]
        self.driver_stroll_points_response = row[23]
        self.driver_mazepin_poines_response = row[24]
        self.driver_pick_two_response = row[25]
        self.race_safety_cars_response = row[26]
        self.race_safety_cars_tiebreaker = row[27]
        self.race_fewest_on_lead_lap_response = row[28]
        self.russia_stop_for_softs_response = row[29]
        self.russia_stop_for_softs_tiebreaker = row[30]
        self.saudi_first_retirement_response = row[31]
        self.saudi_first_retirement_tiebrekaer = row[32]
        self.btn_unique_winners_response = row[33]
        self.btn_unique_pole_sitters_response = row[34]
        self.btn_unique_fastest_lap_response = row[35]
        self.btn_wet_compound_races_response = row[36]
        self.btn_driver_departure_confirmed_response = row[37]
        self.btn_animal_invasions_response = row[38]
        self.btn_total_drivers_tiebreaker = row[39]
        self.bingo_pourchaire_response = row[40]
        self.bingo_norris_response = row[41]
        self.bingo_williams_response = row[42]
        self.bingo_red_bull_response = row[43]
        self.bingo_twenty_classifieds_response = row[44]
        self.bingo_down_to_the_wire_response = row[45]
        self.bingo_russell_response = row[46]


    def __str__(self):
        return self.entry_name


class Entries():
    def __init__(self, data_dir=os.getenv('F1_DATA', 'data'), file_name="entries.csv"):
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
                self.entries[row[1]] = Entry(row)

    def list_entries(self):
        return self.entries.values()


    
