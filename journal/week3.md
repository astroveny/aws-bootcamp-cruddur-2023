# Week 3

## Decentralized Authentication

In this section we will integrate Decentralized Authentication with the application. We will setup AWS Cognito User Pool then integrate it with the frontend application



## AWS Cognito Frontend App Integration
[Back to top](#Week-3)

To create the authentication processes driven by Amazon Cognito, we will utilize the AWS Amlify framework library for React, which provides authentication activities.
To begin, we will create an Amazon Cognito User Pool and then install and configure AWS Amplify library. Afterwards we'll update the frontend application with the necessary code and test the changes. Finally, connect and test the entire authentication procedure using Amazon Cognito.

### Create AWS Cognito User Pool
[Back to top](#Week-3)

1.  Go to the AWS Cognito console then click on 'Create user pool'
2.  Chose 'Email' as a sign-in option then go to the next step<br>
<img width="410" alt="image" src="https://user-images.githubusercontent.com/91587569/222979445-4b197791-5c1c-4242-a66a-863c0bb53c8c.png"><br>

3.  Accept the default Password policy or chose to custom; select 'No MFA' for this setup
4.  Enable 'User account Recovery' and chose 'Email' as a delivery method<br>
<img width="398" alt="image" src="https://user-images.githubusercontent.com/91587569/222979406-623bbdd8-b3b8-4602-89dd-3f7d2bc4c80b.png"><br>

5.  Enable 'Self-service sign-up'<br>
<img width="406" alt="image" src="https://user-images.githubusercontent.com/91587569/222979383-fedcc937-85d2-40d4-834e-3cc35c6b2059.png"><br>

6.  Enable 'Cognito-assisted verification and confirmation'<br>
<img width="398" alt="image" src="https://user-images.githubusercontent.com/91587569/222979362-a4003d91-3320-4f9f-9ff6-79cebed57d12.png"><br>

7.  Select 'Required attributes', in this case 'name' and 'preferred_username'<br>
<img width="371" alt="image" src="https://user-images.githubusercontent.com/91587569/222979339-dc309f13-9b94-4589-aa0f-40dcd9d4fc20.png"><br>

8.  Next step is to configure message delivery, chose 'Send email with Cognito'<br>
<img width="400" alt="image" src="https://user-images.githubusercontent.com/91587569/222979316-ff3c67e7-e4df-4cfa-b47e-de0194b13ca3.png"><br>

9.  Type the name of User Pool and skip 'Use the Cognito Hosted UI'<br>
<img width="400" alt="image" src="https://user-images.githubusercontent.com/91587569/222979296-c3d76577-d241-4b87-b135-e307b7357f42.png"><br>

10.  Under 'Initial app client' chose 'Public Client' as App type and type the 'App client name'<br>
<img  width="400" alt="image" src="https://user-images.githubusercontent.com/91587569/222979261-28a190c8-d6d4-4e80-a294-23cdc5c0f545.png"><br>

11.  Lastly, review the configuration then click on 'Create user pool'
![userpool-created](https://user-images.githubusercontent.com/91587569/223108706-4c6169db-2c5e-4175-a5ff-43ce30584768.jpg)


-----------------------------------

### AWS Amplify Library Setup
[Back to top](#Week-3)

1. Install the necessary dependencies by running the following command inside dir: frontend-react `npm i aws-amplify --save`
2. Add the following ENV variables to the docker compose under the frontend section
```yml
REACT_APP_AWS_PROJECT_REGION:"${AWS_DEFAULT_REGION}"
REACT_APP_AWS_COGNITO_REGION:"${AWS_DEFAULT_REGION}"
REACT_APP_AWS_USER_POOLS_ID:"us-east-1_********t"
REACT_APP_CLIENT_ID:"353********************vte"
```
3. Import the required dependencies for each application entry point. (the code will be added in the next section)

---

### Update The Frontend Application files

<br>
#### App.js
[Back to top](#Week-3)

1.  Import AWS Amplify to App.js by adding the following code: `import { Amplify } from 'aws-amplify';`
2.  Configure AWS Amplify by adding the following code:
```js
Amplify.configure({
  "AWS_PROJECT_REGION": process.env.REACT_APP_AWS_PROJECT_REGION,
  "aws_cognito_region": process.env.REACT_APP_AWS_COGNITO_REGION,
  "aws_user_pools_id": process.env.REACT_APP_AWS_USER_POOLS_ID,
  "aws_user_pools_web_client_id": process.env.REACT_APP_CLIENT_ID,
  "oauth": {},
  Auth: {
    // We are not using an Identity Pool
    // identityPoolId: process.env.REACT_APP_IDENTITY_POOL_ID, // REQUIRED - Amazon Cognito Identity Pool ID
    region: process.env.REACT_APP_AWS_PROJECT_REGION,           // REQUIRED - Amazon Cognito Region
    userPoolId: process.env.REACT_APP_AWS_USER_POOLS_ID,         // OPTIONAL - Amazon Cognito User Pool ID
    userPoolWebClientId: process.env.REACT_APP_CLIENT_ID,   // OPTIONAL - Amazon Cognito Web Client ID (26-char alphanumeric string)
  }
});
```

<br>

#### HomeFeedPage.js
[Back to top](#Week-3)

1.  Import AWS Amplify to HomeFeedPage.js by adding the following code: `import { Auth } from 'aws-amplify';`
2.  Replace the **`const checkAuth`** (lines 40-49) with the following code: 
```js
// check if we are authenicated
const checkAuth = async () => {
  Auth.currentAuthenticatedUser({
    // Optional, By default is false. 
    // If set to true, this call will send a 
    // request to Cognito to get the latest user data
    bypassCache: false 
  })
  .then((user) => {
    console.log('user',user);
    return Auth.currentAuthenticatedUser()
  }).then((cognito_user) => {
      setUser({
        display_name: cognito_user.attributes.name,
        handle: cognito_user.attributes.preferred_username
      })
  })
  .catch((err) => console.log(err));
};
```
>> **NOTE:** The following code will pass the user to Desktop Navigation & Desktop Sidebar
```js
<DesktopNavigation user={user} active={'home'} setPopped={setPopped} />
<DesktopSidebar user={user} />
```

<br>

#### ProfileInfo.js
[Back to top](#Week-3)

1.  Import Auth by replacing **`import cookies`** with the following code: `import { Auth } from 'aws-amplify';`
2.  Replace **`const SignOut`** with the following code:
```js
const signOut = async () => {
  try {
      await Auth.signOut({ global: true });
      window.location.href = "/"
  } catch (error) {
      console.log('error signing out: ', error);
  }
}
```

<br>

#### SigninPage.js 
[Back to top](#Week-3)

1.  Import Auth by replacing **`import cookies`** with the following code: `import { Auth } from 'aws-amplify';`
2.  Replace **`const onsubmit`** with the following code:
```js
const onsubmit = async (event) => {
    setErrors('')
    console.log()
    event.preventDefault();
      Auth.signIn(email, password)
      .then(user => {
        localStorage.setItem("access_token", user.signInUserSession.accessToken.jwtToken)
        window.location.href = "/"
      })
      .catch(error => { 
        if (error.code == 'UserNotConfirmedException') {
          window.location.href = "/confirm"
        }
        setErrors(error.message)
      });
      return false
 }
 ```


<br>

#### Test Signin 
1. Go to AWS console > Amazon Cognito > User pools > cruddur-user-pool
2. Create a _Test User_ by clicking on **'Create User'** under User tab, then enter the email and password 
![userpool-force-pw](https://user-images.githubusercontent.com/91587569/223103966-a089606f-cd29-4a31-b5fc-c7cd99ad6643.jpg)

3. Run the following to confirm **'Force change password'**
```bash
aws cognito-idp admin-set-user-password --username youremailid@example.com --password Newpass123! --user-pool-id us-east-1_wU97ATLit --permanent
```
![userpool-pw-confirmed](https://user-images.githubusercontent.com/91587569/223103991-b874e5d5-2e33-4817-8888-00ebb166bd1f.jpg)

4.  Go back to the User pools console, click on the _Test User_ then edit 'User attributes'
5.  Enter the 'name' and 'preferred_username' then save changes
6.  Go to the frontend app URL then try to sign in using the  _Test User_ you have created <br>
![signup-loggedin-4](https://user-images.githubusercontent.com/91587569/223109743-4e936064-6389-4d36-a75e-95dc21a199a8.jpg)


<br>

#### SignupPage.js
[Back to top](#Week-3)

1.  Import Auth by replacing **`import cookies`** with the following code: `import { Auth } from 'aws-amplify';`
2.  Replace **`const onsubmit`** with the following code:
```js
const onsubmit = async (event) => {
  event.preventDefault();
  setErrors('')
  try {
      const { user } = await Auth.signUp({
        username: email,
        password: password,
        attributes: {
            name: name,
            email: email,
            preferred_username: username,
        },
        autoSignIn: { // optional - enables auto sign in after user is confirmed
            enabled: true,
        }
      });
      console.log(user);
      window.location.href = `/confirm?email=${email}`
  } catch (error) {
      console.log(error);
      setErrors(error.message)
  }
  return false
}
```

<br>

#### ConfirmationPage.js
[Back to top](#Week-3)

1.  Import Auth by replacing **`import cookies`** with the following code: `import { Auth } from 'aws-amplify';`
2.  Replace **`const resend_code`** with the following code:
```js
const resend_code = async (event) => {
    setErrors('')
    try {
      await Auth.resendSignUp(email);
      console.log('code resent successfully');
      setCodeSent(true)
    } catch (err) {
      // does not return a code
      // does cognito always return english
      // for this to be an okay match?
      console.log(err)
      if (err.message == 'Username cannot be empty'){
        setErrors("You need to provide an email in order to send Resend Activiation Code")   
      } else if (err.message == "Username/client id combination not found."){
        setErrors("Email is invalid or cannot be found.")   
      }
    }
  }
  ```
3.  Replace **`const onsubmit`** with the following code:
```js
const onsubmit = async (event) => {
    event.preventDefault();
    setErrors('')
    try {
      await Auth.confirmSignUp(email, code);
      window.location.href = "/"
    } catch (error) {
      setErrors(error.message)
    }
    return false
  }
  ```

<br>

#### Test Signup and Confirmation
1.  Go to the frontend app URL then click 'Sign up'
2.  Fill in the form <br>
![signup-form-1](https://user-images.githubusercontent.com/91587569/223111613-51db0e25-6b86-4a31-8e3e-6371dfe64f6a.jpg)

3.  You will recieve a verification code via an email <br>
![signup-email-2](https://user-images.githubusercontent.com/91587569/223111229-8f55583e-a4c8-4b86-b0de-fb193fdfc935.jpg)

4.  Enter the verification code in the 'confirm you Email box' <br>
![signup-confirm-3](https://user-images.githubusercontent.com/91587569/223111653-59cc465f-a9c6-4a80-bd9e-de4bfa98e0c8.jpg)
  <br>


<br>

#### Recovery Page
[Back to top](#Week-3)

1.  Import Auth by replacing **`import cookies`** with the following code: `import { Auth } from 'aws-amplify';`
2.  Replace **`const onsubmit_send_code`** with the following code:
```js
const onsubmit_send_code = async (event) => {
    event.preventDefault();
    setErrors('')
    Auth.forgotPassword(username)
    .then((data) => setFormState('confirm_code') )
    .catch((err) => setErrors(err.message) );
    return false
  }
```  
3.  Replace **`const onsubmit_confirm_code`** with the following code:
```js
  const onsubmit_confirm_code = async (event) => {
    event.preventDefault();
    setErrors('')
    if (password == passwordAgain){
      Auth.forgotPasswordSubmit(username, code, password)
      .then((data) => setFormState('success'))
      .catch((err) => setCognitoErrors(err.message) );
    } else {
      setErrors('Passwords do not match')
    }
    return false
  }
 ``` 

<br>

#### Test Recovery Method
1.  Go to the frontend app URL then click 'Sign in' then 'Forgot Password?'
2.  Enter your email to reset the password  <br>
![recovery-send-1](https://user-images.githubusercontent.com/91587569/223115470-f49bd37d-bdcf-4422-b445-91e9f5b2ca4c.jpg)

3.  You will recieve a reset code via an email  <br>
![recovery-email-2](https://user-images.githubusercontent.com/91587569/223115422-d9bbd196-4926-4928-a997-5429b0af0279.jpg)


4.  Enter the reset code in the 'Recover your Password' box  <br>
![recovery-pw](https://user-images.githubusercontent.com/91587569/223115119-606efd21-45d4-4992-835d-beada64cb887.jpg)

5.  A confirmation message will appear indicating that the password has been successfully reset  <br>
![recovery-success-4](https://user-images.githubusercontent.com/91587569/223115019-2c7eaa22-bb97-46c4-b852-e252f485e54d.jpg)


