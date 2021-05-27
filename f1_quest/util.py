def get_type_val(row, header_row, header_name, type=str):
    if header_name not in header_row:
        raise Exception(f"{header_name} not found in headers")
    header_idx = header_row[header_name]
    if header_idx >= len(row):
        raise Exception(f"{header_idx} not found in row")
    val = row[header_idx]
    if val is not None and len(val) > 0:
        return type(val)
    return val


def urlify_name(name):
    return name.replace(', ', '_').replace('/', '_').replace(' @ ', '_').replace('M:', 'M_').replace(': ', '_').replace(':', '_').replace(' ', '_')
