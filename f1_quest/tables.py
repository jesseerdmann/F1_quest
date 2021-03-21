class TableEntry():
    def __init__(self, score, entry):
        self.score = score
        self.entry = entry

    
    def __lt__(self, other):
        if self.score < other.score:
            return True
        elif self.score == other.score:
            return str(self.entry) < str(other.entry)
        return False


    def __eq__(self, other):
        return self.score == other.score and \
            str(self.entry) == str(other.entry)


    def __str__(self):
        return f"{self.score} {str(self.entry)}"


class Table():
    def __init__(self, name, entry_label, score_label, score_type, descending=True):
        """
        Initialize the table.

        Keyword arguments:
        name -- the name of the table, e.g. "Driver standings"
        entry_label -- the entry type for display, e.g. "Driver"
        score_label -- the score name for display, e.g. "Points" or "Avg. Laps"
        score_type -- the Python type of the score, e.g. int or float
        descending -- a bool to determine score order, ascending or descening
        """
        self.name = name
        self.entries = []
        self.entry_label = entry_label
        self.score_label = score_label
        self.score_type = score_type
        self.descending = descending
        self.max_entry_length = len(entry_label)
        self.max_score_length = len(score_label)
            

    def __str__(self):
        string_list = [self.name]
        pos = 1
        prev_score = None
        
        header_format_string = "{:3s} {:" + str(self.max_entry_length) + \
            "s} {:" + str(self.max_score_length) + "s}"
        string_list.append(header_format_string.format('Pos', self.entry_label,
            self.score_label))
        format_string = '{:3d} {:' + str(self.max_entry_length) + \
            's} {:' + str(self.max_score_length) + 'd}'
        tie_format_string = '{:3s} {:' + str(self.max_entry_length) + \
            's} {:' + str(self.max_score_length) + 'd}'
        if self.score_type == float:
            format_string = '{:3d} {:' + str(self.max_entry_length) + \
                's} {:' + str(self.max_score_length) + 'f}'
            tie_format_string = '{:3s} {:' + str(self.max_entry_length) + \
                's} {:' + str(self.max_score_length) + 'f}'

        for entry in self.get_ordered_entries():
            if prev_score is not None and entry.score == prev_score:
                string_list.append(tie_format_string.format('', str(entry.entry), entry.score))
            else:
                string_list.append(format_string.format(pos, str(entry.entry), entry.score))
            pos += 1
            prev_score = entry.score

        return '\n'.join(string_list)

    def add_entry(self, score, entry):
        """
        Add a new entry to the entry list, update max string length of the 
         score and the entry for display purposes later.

        Keyword arguments:
        score -- the value that will be the primary sort criteria
        entry -- the object associated with the score
        """
        self.entries.append(TableEntry(score, entry))
        if len(str(score)) > self.max_score_length:
            self.max_score_length = len(str(score))
        if len(str(entry)) > self.max_entry_length:
            self.max_entry_length = len(str(entry))

    
    def get_ordered_entries(self):
        """
        Return a list of sets by score

        Returns:
        A list of TableEntries
        """
        order = sorted(self.entries)
        if self.descending:
            order = reversed(order)
        return list(order)


    def get_entries_by_pos(self, pos, single_entry_only=False):
        """
        Return entries that match the requested position

        Keyword arguments:
        pos -- the desired position to report
        single_entry_only -- rather than return all tied entries at a position
         apply the secondary name sort and choose the specific entry

        Returns:
        By default, the list of entries that match, alternatively a single entry
        """
        if pos > len(self.entries):
            raise Exception(f"Position {pos} greater than number of entries {len(self.entries)}")
        curpos = 0
        abspos = 0
        entries_at_pos = []
        prev_score = None
        ordered_entries = self.get_ordered_entries()
        if single_entry_only:
            return ordered_entries[pos - 1]
        for entry in ordered_entries:
            if prev_score is None or entry.score != prev_score:
                if abspos >= pos:
                    return entries_at_pos
                curpos += 1
                entries_at_pos = [entry]
            else:
                entries_at_pos.append(entry)
            abspos += 1
            prev_score = entry.score
        # if all entries were tied
        if abspos >= pos:
            return entries_at_pos


    def get_position_of_entry(self, entry):
        """
        Given an entry return its position

        Keyword arguments:
        entry -- the entry of interest

        Returns:
        An integer represnting the entries position in the table
        """
        pos = 0
        abs_pos = 0
        prev_entry = None
        for ordered_entry in self.get_ordered_entries():
            # Manage for tied scores
            abs_pos += 1
            if prev_entry is None or prev_entry.score != ordered_entry.score:
                pos = abs_pos
            if entry == ordered_entry.entry:
                return pos
            prev_entry = ordered_entry 
            