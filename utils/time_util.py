import arrow


def get_prc_arrow(datetime_str):
    return arrow.get(datetime_str).to('Asia/Shanghai')


def get_utc_str(arrow_time):
    return arrow_time.format('YYYY-MM-DDTHH:mm:ssZ')


def get_today_arrow():
    return arrow.get(arrow.now().format("YYYY-MM-DD")).replace(tzinfo='Asia/Shanghai')


def get_days_offset(arrow1, arrow2):
    return (arrow1 - arrow2).days
