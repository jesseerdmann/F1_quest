class TableRow():
    def __init__(self, score, subject):
        self.score = score
        self.subject = subject
        self.matching_entries = []

    
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
        return f"{self.score} {str(self.subject)}"


    def add_entry(self, entry):
        self.matching_entries.append(entry)


class Table():
    def __init__(self, name, subject_label, score_label, score_type, descending=True):
        """
        Initialize the table.

        Keyword arguments:
        name -- the name of the table, e.g. "Driver standings"
        subject_label -- the subject type for display, e.g. "Driver"
        score_label -- the score name for display, e.g. "Points" or "Avg. Laps"
        score_type -- the Python type of the score, e.g. int or float
        descending -- a bool to determine score order, ascending or descening
        """
        self.name = name
        self.subjects = []
        self.entries = []
        self.entry_var = None
        self.subject_label = subject_label
        self.score_label = score_label
        self.score_type = score_type
        self.tie_breaker_var = None
        self.descending = descending
        self.max_row_length = len(subject_label)
        self.max_score_length = len(score_label)
            

    def __str__(self):
        string_list = [self.name]
        pos = 1
        prev_score = None
        
        header_format_string = "{:3s} {:" + str(self.max_row_length) + \
            "s} {:" + str(self.max_score_length) + "s}"
        string_list.append(header_format_string.format('Pos', 
            self.subject_label, self.score_label) + " Entries")
        format_string = '{:3d} {:' + str(self.max_row_length) + \
            's} {:' + str(self.max_score_length) + 'd}'
        tie_format_string = '{:3s} {:' + str(self.max_row_length) + \
            's} {:' + str(self.max_score_length) + 'd}'
        if self.score_type == float:
            format_string = '{:3d} {:' + str(self.max_row_length) + \
                's} {:' + str(self.max_score_length) + 'f}'
            tie_format_string = '{:3s} {:' + str(self.max_row_length) + \
                's} {:' + str(self.max_score_length) + 'f}'

        for row in self.get_ordered_subjects():
            entries_str = ' '
            first_row = True
            for entry in row.matching_entries:
                if not first_row:
                    entries_str += ', '
                if self.tie_breaker_var is not None:
                    entries_str += f"{str(entry)} (TB: {entry.__dict__[self.tie_breaker_var]})"
                else:
                    entries_str += f"{str(entry)}"
                first_row = False
            if prev_score is not None and row.score == prev_score:
                string_list.append(tie_format_string.format('', str(row.subject), row.score) + entries_str)
            else:
                string_list.append(format_string.format(pos, str(row.subject), row.score) + entries_str)
            pos += 1
            prev_score = row.score

        return '\n'.join(string_list)

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

    
    def get_ordered_subjects(self):
        """
        Return a list of sets by score

        Returns:
        A list of TableEntries
        """
        order = sorted(self.subjects)
        if self.descending:
            order = reversed(order)
        return list(order)


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


    def add_entries(self, entries, entry_var, tie_breaker_var=None):
        """
        Add an Entries object and match them to the appropriate subject

        Keyword arguments:
        entries -- the Entries that will map to rows
        entry_var -- the variable in the Entry to match with 
        tie_breaker_var -- the varible in the Entry to break ties
        """
        self.entries = entries
        self.entry_var = entry_var
        self.tie_breaker_var = tie_breaker_var
        
        for entry in self.entries.list_entries():
            for subject in self.subjects:
                if entry.__dict__[self.entry_var] == str(subject.subject):
                    subject.add_entry(entry)
                    break

            