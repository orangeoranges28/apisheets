from datetime import datetime, timedelta
thing = datetime.strftime(datetime.now()-timedelta(hours=6),"%H:%M")

print(thing)