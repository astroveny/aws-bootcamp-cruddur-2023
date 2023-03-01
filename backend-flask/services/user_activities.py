from datetime import datetime, timedelta, timezone
from aws_xray_sdk.core import xray_recorder
class UserActivities:
  def run(user_handle):
    model = {
      'errors': None,
      'data': None
    }
# XRAY new segment
    userseg = xray_recorder.current_segment()
    
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
    
    #get metadata
    rkey = list(results.keys())[1]
    rvalue = list(results.values())[1]
    #XRAY call segment user ID
    userseg.set_user("U12345")
    #XRAY call segment metadata
    userseg.put_metadata(rkey,rvalue)
    return model