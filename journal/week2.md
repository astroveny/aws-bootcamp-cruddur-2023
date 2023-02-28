# Week 2

## Distributed Tracing

During this stage, we will intigrate our distributed system with an observability solution (**Honeycomb**) that will be used to monitor and observe requests as they flow through the distributed services. Using distributed tracing will simplify debugging, verifying and comparing services' response time, and spotting unusual patterns.
This would allow us to see and understand how the distributed services handle a single request and apply changes as required.

### Honeycomb Setup

The project will have 1 API key, and each service will have an OTEL service name
- Honeycomb Environment setup
  - Got to https://www.honeycomb.io/ then login
  - Click on _Environment_ "**Test**" then click on (**Manage Environments**)
  - Create a new Environment "**bootcamp**"
  - Obtain the API key 
- Add the required ENV variables
  - Add the API key to the ENV variables  
  - Add OTEL ENV variables to the backend docker compose file
- Install the required backend packages
  - Add the required OpenTelemetry packages to the backend requirements.txt file
  - The backend Dockerfile will install the requirements once it is built 
- Import the OpenTelemetry modules to the backend app
- Add the below code to the app to initialize tracing 
- Add the below code to the app to initialize automatic instrumentation
