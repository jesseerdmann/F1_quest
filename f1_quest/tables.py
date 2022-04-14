class TableRow():
    def __init__(self, score, subject, value=''):
        self.score = score
        self.subject = subject
        self.value = value
        self.matching_entries = []
        self.pos = None

    
    def __lt__(self, other):
        if self.score < other.score:
            return True
        elif self.score == other.score:
            return str(self.subject) < str(other.subject)
        return False


    def __eq__(self, other):
        return self.score == other.score and \
            str(self.subject) == str(other.subject)


    def __str__(self):
        string_val = f"{self.pos} {self.score} {str(self.subject)} {self.value} {len(self.matching_entries)} entries"
        return string_val


    def add_entry(self, entry):
        self.matching_entries.append(entry)

    def set_value(self, value):
        self.value = value


class Table():
    def __init__(self, name, subject_label, score_label, score_type, 
        show_values=True, show_entries=True, entry_label="Entries", 
        value_label="Value", sort='descending'):
        """
        Initialize the table.

        Keyword arguments:
        name -- the name of the table, e.g. "Driver standings"
        subject_label -- the subject type for display, e.g. "Driver"
        score_label -- the score name for display, e.g. "Points" or "Avg. Laps"
        score_type -- the Python type of the score, e.g. int or float
        show_values -- if True, print values
        show_entries -- if True, print entries
        sort -- sort scores in ascending or descending order, or None to not sort
        """
        self.name = name
        self.subjects = []
        self.entries = []
        self.entry_var = None
        self.subject_label = subject_label
        self.score_label = score_label
        self.score_type = score_type
        self.tie_breaker_var = None
        self.show_values = show_values
        self.show_entries = show_entries
        self.sort = sort
        self.entry_label = entry_label
        self.value_label = value_label
        self.max_row_length = len(subject_label)
        self.max_score_length = len(score_label)
            

    def __str__(self):
        string_list = [self.name]
        
        header_format_string = "{:3s} {:" + str(self.max_row_length) + \
            "s} {:" + str(self.max_score_length) + "s}"
        header_string = header_format_string.format('Pos', 
            self.subject_label, self.score_label)
        if self.show_values: # and self.tie_breaker_var is None:
            header_string += " " + self.value_label
        if self.show_entries:
            header_string += " " + self.entry_label
        string_list.append(header_string)
        score_type_str = 'd'
        if self.score_type == float:
            score_type_str = 'f'
        elif self.score_type == str:
            score_type_str = 's'
        value_string = ''
        if self.show_values: # and self.tie_breaker_var is None:
            value_string = ' {:5d}'
        base_format_string = '{:' + str(self.max_row_length) + 's} {:' + \
            str(self.max_score_length) + score_type_str + '}' + value_string
        
        format_string = '{:3d} ' + base_format_string
        
        for row in self.get_ordered_subjects():
            row_format_string = format_string
            if self.show_values: # and self.tie_breaker_var is None:
                row_string = row_format_string.format(row.pos, str(row.subject), row.score, row.value)
            else:
                row_string = row_format_string.format(row.pos, str(row.subject), row.score)
            if self.show_entries:
                entries_str = self.entries_string(row)
                row_string += entries_str
            
            string_list.append(row_string)
            prev_score = row.score
        return '\n'.join(string_list)


    def entries_string(self, row):
        entries_str = ' '
        first_row = True
        for entry in row.matching_entries:
            if not first_row:
                entries_str += ', '
            if self.show_entries:
                if self.tie_breaker_var is not None:
                    entries_str += f"{str(entry)} (TB: {entry.__dict__[self.tie_breaker_var]})"
                else:
                    entries_str += f"{str(entry)}"
            first_row = False
        return entries_str


    def add_subject(self, score, subject):
        """
        Add a new row to the row list, update max string length of the 
         score and the row for display purposes later.

        Keyword arguments:
        score -- the value that will be the primary sort criteria
        subject -- the object associated with the score
        """
        new_row = TableRow(score, subject)
        self.subjects.append(new_row)
        if len(str(score)) > self.max_score_length:
            self.max_score_length = len(str(score))
        if len(str(subject)) > self.max_row_length:
            self.max_row_length = len(str(subject))
        return new_row

    
    def get_ordered_subjects(self):
        """
        Return a list of sets by score

        Returns:
        A list of TableEntries
        """
        order = self.subjects
        if self.sort is not None:
            order = sorted(self.subjects)
            if self.sort == 'descending':
                order = reversed(order)
        
        pos = 1
        abs_pos = 1
        prev_score = None
        ordered_subjects = []
        for subject in order:
            if subject.score != prev_score:
                pos = abs_pos
            subject.pos = pos
            abs_pos += 1
            prev_score = subject.score
            ordered_subjects.append(subject)
        return ordered_subjects


    def get_subjects_by_pos(self, pos, single_subject_only=False):
        """
        Return subjects that match the requested position

        Keyword arguments:
        pos -- the desired position to report
        single_subjects_only -- rather than return all tied subjects at a position
         apply the secondary name sort and choose the specific subject

        Returns:
        By default, the list of subjects that match, alternatively a single subject
        """
        if pos > len(self.subjects):
            raise Exception(f"Position {pos} greater than number of subjects {len(self.subjects)}")
        curpos = 0
        abspos = 0
        subjects_at_pos = []
        prev_score = None
        ordered_subjects = self.get_ordered_subjects()
        if single_subject_only:
            return ordered_subjects[pos - 1]
        for subject in ordered_subjects:
            if prev_score is None or subject.score != prev_score:
                if abspos >= pos:
                    return subjects_at_pos
                curpos += 1
                subjects_at_pos = [subject]
            else:
                subjects_at_pos.append(subject)
            abspos += 1
            prev_score = subject.score
        # if all subjects were tied
        if abspos >= pos:
            return subjects_at_pos


    def get_position_of_subject(self, subject):
        """
        Given an subject return its position

        Keyword arguments:
        subject -- the subject of interest

        Returns:
        An integer represnting the subject's position in the table
        """
        pos = 0
        abs_pos = 0
        prev_subject = None
        for ordered_subject in self.get_ordered_subjects():
            # Manage for tied scores
            abs_pos += 1
            if prev_subject is None or prev_subject.score != ordered_subject.score:
                pos = abs_pos
            if subject == ordered_subject.subject:
                return pos
            prev_subject = ordered_subject 


    def add_entries(self, entries, entry_var, tie_breaker_var=None, 
        update_entry_score=False):
        """
        Add an Entries object and match them to the appropriate subject

        Keyword arguments:
        entries -- the Entries that will map to rows
        entry_var -- the variable in the Entry to match with 
        tie_breaker_var -- the varible in the Entry to break ties
        update_entry_score -- add the row value to the score
        """
        self.entries = entries
        self.entry_var = entry_var
        self.tie_breaker_var = tie_breaker_var
        
        for entry in self.entries.list_entries():
            for subject in self.subjects:
                entry_response = entry.__dict__[self.entry_var]
                if type(entry_response) == str and entry_response == str(subject.subject):
                    subject.add_entry(entry)
                    if update_entry_score:
                        entry.add_points(subject.value)
                    break
                elif type(entry_response) == list:
                    for response_item in entry_response:
                        if response_item == str(subject.subject):
                            subject.add_entry(entry)
                            if update_entry_score:
                                entry.add_points(subject.value)
                            break

            