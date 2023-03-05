# Week 3

## Decentralized Authentication

In this section we will integrate Decentralized Authentication with the application. We will setup AWS Cognito User Pool then integrate it with the frontend application



## AWS Cognito Frontend App Integration

We will use AWS Amlify framework SDK for React which profivdes authentication operations to implement the authentication workflows that Amazon Cognito drives.
To prepare the setup, we will first create a User Pool on AWS Cognito, install and configure AWS Amplify. Then we will update the frontend application with the required code and test the changes applied. Lastly, connect and test the full process to authenticate using AWS Cognito.

### Create AWS Cognito User Pool

1.  Go to the AWS Cognito console then click on 'Create user pool'
2.  Chose 'Email' as a sign-in option then go to the next step<br>
<img width="410" alt="image" src="https://user-images.githubusercontent.com/91587569/222979445-4b197791-5c1c-4242-a66a-863c0bb53c8c.png"><br><br>

3.  Accept the default Password policy or chose to custom; select 'No MFA' for this setup
4.  Enable 'User account Recovery' and chose 'Email' as a delivery method<br>
<img width="398" alt="image" src="https://user-images.githubusercontent.com/91587569/222979406-623bbdd8-b3b8-4602-89dd-3f7d2bc4c80b.png"><br><br>

5.  Enable 'Self-service sign-up'<br>
<img width="406" alt="image" src="https://user-images.githubusercontent.com/91587569/222979383-fedcc937-85d2-40d4-834e-3cc35c6b2059.png"><br><br>

6.  Enable 'Cognito-assisted verification and confirmation'<br>
<img width="398" alt="image" src="https://user-images.githubusercontent.com/91587569/222979362-a4003d91-3320-4f9f-9ff6-79cebed57d12.png"><br><br>

7.  Select 'Required attributes', in this case 'name' and 'preferred_username'<br>
<img width="371" alt="image" src="https://user-images.githubusercontent.com/91587569/222979339-dc309f13-9b94-4589-aa0f-40dcd9d4fc20.png"><br><br>

8.  Next step is to configure message delivery, chose 'Send email with Cognito'<br>
<img width="400" alt="image" src="https://user-images.githubusercontent.com/91587569/222979316-ff3c67e7-e4df-4cfa-b47e-de0194b13ca3.png"><br><br>

9.  Type the name of User Pool and skip 'Use the Cognito Hosted UI'<br>
<img  alt="image" src="https://user-images.githubusercontent.com/91587569/222979296-c3d76577-d241-4b87-b135-e307b7357f42.png"><br><br>

10.  Under 'Initial app client' chose 'Public Client' as App type and type the 'App client name'<br>
<img  alt="image" src="https://user-images.githubusercontent.com/91587569/222979261-28a190c8-d6d4-4e80-a294-23cdc5c0f545.png"><br><br>

11.  Lastly, review the configuration the click on 'Create user pool'
