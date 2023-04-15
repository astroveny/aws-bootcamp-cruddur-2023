from datetime import datetime, timedelta, timezone
from aws_xray_sdk.core import xray_recorder
from time import sleep
from lib.db import db


class UserActivities:
  def run(user_handle):
    model = {
      'errors': None,
      'data': None
    }
    sleep(0.003)
    # double ## are removed temp <<<<<<<
  # XRAY start segment
    ##userseg = xray_recorder.current_segment()
    #XRAY call segment user ID
    ##userseg.set_user("U12345")
  # XRAY start subsegment 
    ##subuserseg = xray_recorder.begin_subsegment('start_time') 
    ##sleep(0.001)
    ##now = datetime.now(timezone.utc).astimezone()

    if user_handle == None or len(user_handle) < 1:
      model['errors'] = ['blank_user_handle']
    else:
      print("else:")
      sql = db.template('users','show')
      results = db.query_object_json(sql,{'handle': user_handle})
      model['data'] = results
    
    #get keys & value
    rkeys = list(results.keys())
    rvalues = list(results.values())
    
    # double ## are removed temp <<<<<<
    #XRAY call subsegment annotation & metadata 
    ##subuserseg.put_annotation(rkeys[3],rvalues[3])
    ##subuserseg.put_metadata(rkeys[1],rvalues[1])
    ##xray_recorder.end_subsegment()
    # end Segment
    #xray_recorder.end_segment()

    return model