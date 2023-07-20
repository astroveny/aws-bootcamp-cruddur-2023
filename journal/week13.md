# Week 13 

## Refactoring part 2



## Refactor Frontend App 

### Activity Message Reply

#### Update ActivityContent.js

Change Reply behviour and layout

- Edit `frontend-react-js/src/components/ActivityContent.js`
- Here is the full updated [code](https://github.com/astroveny/aws-bootcamp-cruddur-2023/blob/60eb4d0d7d1aac7b9d3e70271f9e72f98cbd7f0d/frontend-react-js/src/components/ActivityContent.js)

#### Update ActivityContent.css

- Edit `frontend-react-js/src/components/ActivityContent.css`
- Here is the full updated [code](https://github.com/astroveny/aws-bootcamp-cruddur-2023/blob/60eb4d0d7d1aac7b9d3e70271f9e72f98cbd7f0d/frontend-react-js/src/components/ActivityContent.css)


#### Update Activity Actions

Change the activity actions to prevent triggering the event default  

- Update the following files
    - `frontend-react-js/src/components/ActivityActionLike.js`
    - `frontend-react-js/src/components/ActivityActionReply.js`
    - `frontend-react-js/src/components/ActivityActionRepost.js`
    - `frontend-react-js/src/components/ActivityActionShare.js`

- Add the following to the function under `const onclick`  
`event.preventDefault()`
- Add `return false` at the end of the `const onclick`


#### Update ActivityItem.js

Change activity item behviour and layout

- Edit `frontend-react-js/src/components/ActivityItem.js`
- Here is the full updated [code](https://github.com/astroveny/aws-bootcamp-cruddur-2023/blob/60eb4d0d7d1aac7b9d3e70271f9e72f98cbd7f0d/frontend-react-js/src/components/ActivityItem.js)

#### Update ActivityItem.css

Change activity item behviour and layout

- Edit `frontend-react-js/src/components/ActivityItem.css`
- Add the following code 
```css
a.activity_item {
  text-decoration: none;
}
a.activity_item:hover {
  background: rgba(255,255,255,0.15);
}
```

---

### Activity Show and Reply


#### Create ActivityShowPage.js

- Create a new file `frontend-react-js/src/pages/ActivityShowPage.js`
- Here is the full [code](https://github.com/astroveny/aws-bootcamp-cruddur-2023/blob/60eb4d0d7d1aac7b9d3e70271f9e72f98cbd7f0d/frontend-react-js/src/pages/ActivityShowPage.js)
- Edit `frontend-react-js/src/App.js`
  - Import ActivityShowPage   
  `import ActivityShowPage from './pages/ActivityShowPage';`
  - Add a route path to `const router`
  ```js
  {
      path: "/@:handle/status/:activity_uuid",
      element: <ActivityShowPage />
    },
  ```

#### Update Backend Routes

- Edit `backend-flask/routes/users.py`
- Add the following route
```python
 @app.route("/api/activities/@<string:handle>/status/<string:activity_uuid>", methods=['GET'])
  def data_show_activity(handle,activity_uuid):
    data = ShowActivity.run(activity_uuid)
    return data, 200 
```
- Here is the full updated [code]()
- Edit `backend-flask/routes/activities.py`
- Remove the following route
```python
from services.show_activity import *

  @app.route("/api/activities/<string:activity_uuid>", methods=['GET'])
  @xray_recorder.capture('activities_show')
  def data_show_activity(activity_uuid):
    data = ShowActivity.run(activity_uuid=activity_uuid)
    return data, 200
```

#### Update show_activity.py

- Edit `backend-flask/services/show_activity.py`
- Replace the content with the following code
```python
from datetime import datetime, timedelta, timezone
from lib.db import db
class ShowActivities:
  def run(activity_uuid):
    sql = db.template('activities','show')
    results = db.query_object_json(sql,{
      'uuid': activity_uuid
    })
    return results
```

>> Note: restart the backend app to view the changes! 

#### Create Replies.js

- Create a new file `frontend-react-js/src/components/Replies.js`
- Here is the full [code](https://github.com/astroveny/aws-bootcamp-cruddur-2023/blob/60eb4d0d7d1aac7b9d3e70271f9e72f98cbd7f0d/frontend-react-js/src/components/Replies.js)



#### Refactor Pages Auth get url

- Edit `frontend-react-js/src/pages/MessageGroupsPage.js`
  
  - Replace the following under `const loadData` inside `const url`
  ```js
  get(url,null,function(data){
      setMessageGroups(data)
  ```
    
    - With this code
    ```js
    get(url,{
        auth: true,
        success: function(data){
          setMessageGroups(data)
        }
    ```
- Edit `frontend-react-js/src/pages/NotificationsFeedPage.js`
  
 - Replace the following under `const loadData` inside `const url`
  ```js
  get(url,null,function(data){
      setActivities(data)
  ```
    
    - With this code
    ```js
    get(url,{
        auth: true,
        success: function(data){
          setActivities(data)
        }
    ```
- Edit `frontend-react-js/src/pages/UserFeedPage.js`
  
 - Replace the following under `const loadData` inside `const url`
  ```js
  get(url,null,function(data){
      console.log('setprofile',data.profile)
      setProfile(data.profile)
      setActivities(data.activities)
  ```
    
    - With this code
    ```js
    get(url,{
        auth: false,
        success: function(data){
          console.log('setprofile',data.profile)
          setProfile(data.profile)
          setActivities(data.activities)
        }
    ```
- Edit `frontend-react-js/src/pages/HomeFeedPage.js`
  
 - Replace the following under `const loadData` inside `const url`
  ```js
  get(url,null,function(data){
      setActivities(data)
  ```
    
    - With this code
    ```js
    get(url,{
        auth: true,
        success: function(data){
          setActivities(data)
        }
    ```
      
  - Remove this code
  ```js
  setActivities={setActivities} 
  activities={activities} 
  ```

- Edit `frontend-react-js/src/pages/MessageGroupNewPage.js`
  
 - Replace the following under `const loadUserShortData` inside `const url`
  ```js
  get(url,null,function(data){
      console.log('other user:',data)
      setOtherUser(data)
  ```
    
    - With this code
    ```js
    get(url,{
        auth: true,
        success: function(data){
          console.log('other user:',data)
          setOtherUser(data)
        }
    ```
  - Replace the following under `const loadMessageGroupsData` inside `const url`
  ```js
  get(url,null,function(data){
      setMessageGroups(data)
  ```
    
    - With this code
    ```js
    get(url,{
        auth: true,
        success: function(data){
          setMessageGroups(data)
        }
    ```


#### Refactor Pages Auth post url

- Edit `frontend-react-js/src/components/MessageForm.js`
  
 - Replace the following under `const onsubmit` inside `const url`
  ```js
  post(url,payload_data,setErrors,function(){
      console.log('data:',data)
      if (data.message_group_uuid) {
        console.log('redirect to message group')
        window.location.href = `/messages/${data.message_group_uuid}`
      } else {
        props.setMessages(current => [...current,data]);
  ```
    
    - With this code
    ```js
    post(url,payload_data,{
      auth: true,
      setErrors: setErrors,
      success: function(){
        console.log('data:',data)
        if (data.message_group_uuid) {
          console.log('redirect to message group')
          window.location.href = `/messages/${data.message_group_uuid}`
        } else {
          props.setMessages(current => [...current,data]);
        }
    ```

- Edit `frontend-react-js/src/components/ActivityForm.js`
  
 - Replace the following under `const onsubmit` inside `const payload_data`
  ```js
  post(url,payload_data,setErrors,function(data){
      // add activity to the feed
      props.setActivities(current => [data,...current]);
      // reset and close the form
      setCount(0)
      setMessage('')
      setTtl('7-days')
      props.setPopped(false)
  ```
    
    - With this code
    ```js
    post(url,payload_data,{
        auth: true,
        setErrors: setErrors,
        success: function(data){
          // add activity to the feed
          props.setActivities(current => [data,...current]);
          // reset and close the form
          setCount(0)
          setMessage('')
          setTtl('7-days')
          props.setPopped(false)
        }
    ```

- Edit `frontend-react-js/src/components/ReplyForm.js`
  
 - Replace the following under `const onsubmit` inside `const payload_data`
 ```js
 post(url,payload_data,setErrors,function(data){
      // add activity to the feed
      let activities_deep_copy = JSON.parse(JSON.stringify(props.activities))
      let found_activity = activities_deep_copy.find(function (element) {
        return element.uuid ===  props.activity.uuid;
      });
      found_activity.replies.push(data)
      props.setActivities(activities_deep_copy);
      // reset and close the form
      setCount(0)
      setMessage('')
      props.setPopped(false)
 ```
   
  - With this code
  ```js
  post(url,payload_data,{
      auth: true,
      setErrors: setErrors,
      success: function(data){
        // add activity to the feed
        //let activities_deep_copy = JSON.parse(JSON.stringify(props.activities))
        //let found_activity = activities_deep_copy.find(function (element) {
        //  return element.uuid ===  props.activity.uuid;
        //});
        //found_activity.replies.push(data)
        //props.setActivities(activities_deep_copy);

        // reset and close the form
        setCount(0)
        setMessage('')
        props.setPopped(false)
      }
  ```

#### Refactor Pages Auth put url

- Edit `frontend-react-js/src/components/ProfileForm.js`
  
 - Replace the following under `const onsubmit` inside `const payload_data`
 ```js
 put(url,payload_data,setErrors,function(data){
      setBio(null)
      setDisplayName(null)
      props.setPopped(false)
 ```
   
  - With this code
  ```js
  put(url,payload_data,{
      auth: true,
      setErrors: setErrors,
      success: function(data){
        setBio(null)
        setDisplayName(null)
        props.setPopped(false)
      }
  ```

#### Update Requests.js

- Edit `frontend-react-js/src/lib/Requests.js`
- Here is the updated [code]

---
---


## Implement Message Button 


### Update ActivityItem.js

Change the behaviour of the activity item, 

- Edit `frontend-react-js/src/components/ActivityItem.js`
- Add the following to the function ActivityItem
```python
const navigate = useNavigate()
  const click = (event) => {
    event.preventDefault()
    const url = `/@${props.activity.handle}/status/${props.activity.uuid}`
    navigate(url)
    return false;
  }

  let expanded_meta;
  if (props.expanded === true) {
    //1:56 PM · May 23, 2023
  }

  const attrs = {}
  let item
  if (props.expanded === true) {
    attrs.className = 'activity_item expanded'
  } else {
    attrs.className = 'activity_item clickable'
    attrs.onClick = click
  }
```
- Here is the full updated [code]()

### Update ActivityItem.css

- Edit `frontend-react-js/src/components/ActivityItem.css`
- Replace this code
  ```css
  a.activity_item {
  text-decoration: none;
  }
  a.activity_item:hover {
    background: rgba(255,255,255,0.15);
  }
  ```
    
    - With this code
    ```css
    .activity_item.clickable:hover {
      cursor: pointer;
    }
    .activity_item.clickable:hover {
      background: rgba(255,255,255,0.15);
    }
    ```

### Update ActivityShowPage.js

Chnage the page title from Home to Crud

- Edit `frontend-react-js/src/pages/ActivityShowPage.js`
- Replace `<div className='title'>Home</div>`
- With this `<div className='title'>Crud</div>`


---
---

## Add The Timezones Fixes

### Create DateTimeFormats.js

- Create a new file `frontend-react-js/src/lib/DateTimeFormats.js`
- Here is the updated [code]()

### Update MessageItem.js

- Edit `frontend-react-js/src/components/MessageItem.js`
- Here is the updated [code]()

### Update MessageGroupItem.js

- Edit `frontend-react-js/src/components/MessageGroupItem.js`
- Here is the updated [code]()

### Update ActivityContent.js

- Edit `frontend-react-js/src/components/ActivityContent.js`
- Here is the updated [code]()

### Update DDB Seed

- Edit `bin/ddb/seed`
- Replace this code `now = datetime.now(timezone.utc).astimezone()`
  - With this code `now = datetime.now()`
- Replace this code `  created_at = (now + timedelta(minutes=i)).isoformat()`
  - With this code `  created_at = (now - timedelta(days=1) + timedelta(minutes=i)).isoformat()`


### Update ddb.py

- Edit `backend-flask/lib/ddb.py`
- Repalce this code
```python
now = datetime.now(timezone.utc).astimezone().isoformat()
created_at = now
```  
  - With this code `created_at = datetime.now().isoformat()`
- Remove all `print('== create_message_group.`

---
---


## Enhance Activity UX

### Update ActivityShowPage.js

- Edit `frontend-react-js/src/pages/ActivityShowPage.js`
- Here is the updated [code]()

### Update ActivityShowPage.css

- Edit `frontend-react-js/src/pages/ActivityShowPage.css`
- Add the following code
```css
.back {
  font-size: 24px;
  color: rgba(255,255,255,0.5);
  cursor: pointer;
  padding: 0px 16px;
}

.back:hover {
  color: rgba(255,255,255,1)
}

.activity_feed_heading.flex {
  display: flex;
  flex-direction: row;
  align-items: center;
}

.activity_feed_heading.flex .title{
  flex-grow: 1
}
```

### Create ActivityShowItem.js

- Create a new file `frontend-react-js/src/components/ActivityShowItem.js`
- Here is the full [code]()


### Update ProfileHeading.css

- Edit `frontend-react-js/src/components/ProfileHeading.css`
- Add the follfowing to the `.profile_heading .profile-avatar`
```css
background-color: var(--fg);
```

### Update ReplyForm.js

- Edit `frontend-react-js/src/components/ReplyForm.js`
- Add the following code to `success: function(data)`
```js
if (props.setReplies) {
  props.setReplies(current => [data,...current]);
}
```

### Update ActivityItem.js

- Edit `frontend-react-js/src/components/ActivityItem.js`
- Here is the updated [code]()

### Update ActivityItem.css

- Edit `frontend-react-js/src/components/ActivityItem.css`
- Add the following code
```css
.activity_item.expanded .activity_content {
  display: flex;
}
.activity_item.expanded .activity_content .activity_identity{
  flex-grow: 1;
}
```

---
---


## Machine User

We will create a new user "machine user" that will have the permissions to read and write from DynamoDB table 

### Machine User Template.yaml

- Create new dir: `aws/cfn/machine-user`
- Create **template.yaml** file
- Add the following code
```yml
AWSTemplateFormatVersion: '2010-09-09'
Resources:
  CruddurMachineUser:
    Type: 'AWS::IAM::User'
    Properties: 
      UserName: 'cruddur_machine_user'
  DynamoDBFullAccessPolicy: 
    Type: 'AWS::IAM::Policy'
    Properties: 
      PolicyName: 'DynamoDBFullAccessPolicy'
      PolicyDocument:
        Version: '2012-10-17'
        Statement: 
          - Effect: Allow
            Action: 
              - dynamodb:PutItem
              - dynamodb:GetItem
              - dynamodb:Scan
              - dynamodb:Query
              - dynamodb:UpdateItem
              - dynamodb:DeleteItem
              - dynamodb:BatchWriteItem
            Resource: '*'
      Users:
        - !Ref CruddurMachineUser
```


### Machine User Config.toml

- Create **config.tom** file
- Add the following code
```
[deploy]
bucket = 'cfn-artifacts-awsbc.flyingresnova.com'
region = 'us-east-1'
stack_name = 'CrdMachinueUser'
```

### Generate Access Keys

- Go to AWS IAM console
- Select the new user 'cruddur_machine_user'
- Click on the **Security credentials** tab
- Scroll down then click on **Create access key**


### Update Parameter Store

- Go to AWS SSM console
- Select Parameter Store
- Add the new access key to '/cruddur/backend-flask/AWS_ACCESS_KEY_ID'

### Run CodePipline 

- Go to the CodePipeine console
- Select 'CrdCicd-Pipeline' 
- Click **Release change**