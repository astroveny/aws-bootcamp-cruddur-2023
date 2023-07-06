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

### Activity Show Reply


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


#### Create Replies.js

- Create a new file `frontend-react-js/src/components/Replies.js`
- Here is the full [code](https://github.com/astroveny/aws-bootcamp-cruddur-2023/blob/60eb4d0d7d1aac7b9d3e70271f9e72f98cbd7f0d/frontend-react-js/src/components/Replies.js)



#### Update Show_Activity.py



#### Refactor Pages Auth Load

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
