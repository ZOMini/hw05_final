def year(request):
    from datetime import datetime
    year_now = datetime.strftime(datetime.now(), "%Y")
    return {'year': year_now}
