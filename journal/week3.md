# Week 3

## Decentralized Authentication

In this section we will integrate Decentralized Authentication with the application. We will setup AWS Cognito User Pool then integrate it with the frontend application



## AWS Cognito Frontend App Integration

To create the authentication processes driven by Amazon Cognito, we will utilize the AWS Amlify framework library for React, which provides authentication activities.
To begin, we will create an Amazon Cognito User Pool and then install and configure AWS Amplify library. Afterwards we'll update the frontend application with the necessary code and test the changes. Finally, connect and test the entire authentication procedure using Amazon Cognito.

### Create AWS Cognito User Pool

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

-----------------------------------

### AWS Amplify Library Setup

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

#### App.js
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


#### HomeFeedPage.js
1.  Import AWS Amplify to HomeFeedPage.js by adding the following code: `import { Amplify } from 'aws-amplify';`




#### ProfileInfo.js




#### SigninPage.js 




#### SignupPage.js




#### ConfirmationPage.js





#### Recovery Page
