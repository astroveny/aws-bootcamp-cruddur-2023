from datetime import datetime, timedelta, timezone
from lib.db import pool 

class HomeActivities:
  def run(cognito_user_id=None):
    # cloudwatch logging - remove logging from run()
    #logger.info("To-CW: Home Activities" )
    now = datetime.now(timezone.utc).astimezone()
    
    sql= """
    Select * FROM activities
    """
    with pool.connection() as conn:
       with conn.cursor() as cur:
         cur.execute(sql)
         # this will return a tuple
         # the first field being the data
         json = cur.fetchone()
       return json[0]
    return results