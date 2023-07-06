# Week 13 

## Refactoring part 2



## Refactor Frontend App 

### Activity Message Reply

#### Update ActivityContent.js

Change Reply behviour and layout

- Edit `frontend-react-js/src/components/ActivityContent.js`
- Here is the full updated [code]()

#### Update ActivityContent.css

- Edit `frontend-react-js/src/components/ActivityContent.css`
- Here is the full updated [code]()


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
- Here is the full updated [code]()

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
- Here is the full [code]()
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
- Here is the full [code]()
