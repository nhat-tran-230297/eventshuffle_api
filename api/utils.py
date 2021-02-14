from datetime import datetime

def is_date_valid(date_format):
    try:
        date = datetime.strptime(date_format, '%Y-%m-%d')
        if date.strftime('%Y-%m-%d') != date_format:
            return False
        
        return True
        
    except ValueError:
        return False


def has_dates_duplicate(dates: list) -> bool:
    return len(dates) == len(set(dates))
