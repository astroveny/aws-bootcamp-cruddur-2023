from datetime import datetime, timedelta, timezone
from aws_xray_sdk.core import xray_recorder
from time import sleep


class UserActivities:
  def run(user_handle):
    model = {
      'errors': None,
      'data': None
    }
    sleep(0.003)
  # XRAY start segment
    userseg = xray_recorder.current_segment()
    #XRAY call segment user ID
    userseg.set_user("U12345")
  # XRAY start subsegment 
    subuserseg = xray_recorder.begin_subsegment('start_time') 
    sleep(0.001)
    now = datetime.now(timezone.utc).astimezone()

    if user_handle == None or len(user_handle) < 1:
      model['errors'] = ['blank_user_handle']
    else:
      now = datetime.now()
      results = {
        'uuid': '248959df-3079-4947-b847-9e0892d1bab4',
        'handle':  'Buzz Lightyear',
        'message': 'To infinity and beyond!',
        'created_at': (now - timedelta(days=1)).isoformat(),
        'expires_at': (now + timedelta(days=31)).isoformat()
      }
      model['data'] = results
    
    #get keys & value
    rkeys = list(results.keys())
    rvalues = list(results.values())
    
    #XRAY call subsegment annotation & metadata 
    subuserseg.put_annotation(rkeys[3],rvalues[3])
    subuserseg.put_metadata(rkeys[1],rvalues[1])
    xray_recorder.end_subsegment()
    # end Segment
    #xray_recorder.end_segment()

    return model