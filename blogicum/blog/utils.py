def get_full_name(first_name, last_name):
    trimmed_first_name = first_name.strip()
    trimmed_last_name = last_name.strip()

    if len(trimmed_first_name) == 0 and len(trimmed_last_name) == 0:
        return None

    return f'{trimmed_first_name} {trimmed_last_name}'
