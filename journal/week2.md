# Week 2

## Distributed Tracing

During this stage, we will intigrate our distributed system with an observability solution (**Honeycomb**) that will be used to monitor and observe requests as they flow through the distributed services. Using distributed tracing will simplify debugging, verifying and comparing services' response time, and spotting unusual patterns.
This would allow us to see and understand how the distributed services handle a single request and apply changes as required.

-  [Open Ports using Gitpod.yml](#Open-Ports-using-Gitpodyml)
-  [Honeycomb Integration](#HoneycombIntegration)
    1.  [Initial Setup](#Initial-Setup)
    2.  [Test and Generate Data](#Test-and-Generate-Data)
    3.  [Explore with Honeycomb](#Explore-with-Honeycomb)

-  [](#)
-  [](#)
-  [](#)
-  [Challenges](#Challenges)
    1.  [Add NEW Span and Attributes](#Add-NEW-Span-and-Attributes)
    2.  [](#)
    3.  [](#)
  


## Open Ports using Gitpod.yml
- update gitpod.yml with the below then reload the workspace
```yml
ports: 
  - name: frontend 
    port: 3000
    onOpen: open-browser
    visibility: public 
  - name: backend
    port: 4567
    visibility: public
  - name: xray-daemon
    port: 2000
    visibility: public
```

## Honeycomb Integration 
[Back to top](#Week-2)

### **Initial Setup**

>> **NOTE:** output has been reduced!

The project will have 1 API key, and each service will have an OTEL service name
- Honeycomb Environment setup
  - Got to https://www.honeycomb.io/ then login
  - Click on _Environment_ "**Test**" then click on (**Manage Environments**)
  - Create a new Environment "**bootcamp**"
  - Obtain the API key 

<br>

- Add the required ENV variables
  - Add the API key to the ENV variables 
    ```bash
    gitpod /workspace/aws-bootcamp-cruddur-2023 (main) $ export HONEYCOMB_API_KEY="*******************uxF"
    gitpod /workspace/aws-bootcamp-cruddur-2023 (main) $ gp env HONEYCOMB_API_KEY="*******************uxF"
    ``` 
  - Add OTEL ENV variables to the backend service inside docker compose file 
    ```yml
    OTEL_EXPORTER_OTLP_ENDPOINT: "https://api.honeycomb.io"
    OTEL_EXPORTER_OTLP_HEADERS: "x-honeycomb-team=${HONEYCOMB_API_KEY}"
    OTEL_SERVICE_NAME: "backend-flask"
    ```
<br>

- Install the required backend packages
  - Add the required OpenTelemetry packages to the backend requirements.txt file
    ```
    opentelemetry-api 
    opentelemetry-sdk 
    opentelemetry-exporter-otlp-proto-http 
    opentelemetry-instrumentation-flask 
    opentelemetry-instrumentation-requests
    ```
  - The backend Dockerfile will install the requirements once it is built 

<br>


- Update the backend app
  - Import the OpenTelemetry modules to the backend app
    ```python
    # Honeycomb 
    from opentelemetry import trace
    from opentelemetry.instrumentation.flask import FlaskInstrumentor
    from opentelemetry.instrumentation.requests import RequestsInstrumentor
    from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import BatchSpanProcessor
    from opentelemetry.sdk.trace.export import ConsoleSpanExporter, SimpleSpanProcessor
    ```
  - Add the below code to the app to initialize tracing 
    ```python
    # Honeycomb 
    # Initialize tracing and an exporter that can send data to Honeycomb
    provider = TracerProvider()
    processor = BatchSpanProcessor(OTLPSpanExporter())
    provider.add_span_processor(processor)

    # simple span to show as pary of backend-flask app
    simple_processor = SimpleSpanProcessor(ConsoleSpanExporter())
    provider.add_span_processor(simple_processor)

    trace.set_tracer_provider(provider)
    tracer = trace.get_tracer(__name__)
    ```

  - Add the below code to the app to initialize automatic instrumentation
    ```python
    # Honeycomb
    # Initialize automatic instrumentation with Flask
    FlaskInstrumentor().instrument_app(app)
    RequestsInstrumentor().instrument()
    ```
### **Test and Generate Data**
[Back to top](#Week-2)

>> **NOTE:** output has been reduced!

  1. Start the backend app by running `docker compose up -d` 
  2. Make few requests by accessing backend app endpoint "/api/activities/home"
  ```bash
  gitpod /workspace/aws-bootcamp-cruddur-2023 (main) $ curl -X GET http://localhost:4567/api/activities/home -H "Accept: application/json" -H "Content-Type: application/json"
  ```
  4. Making requests to the service will generate the telemetry that will be sent to Honeycomb
  5. You can verify if span has been created successfully by checking docker logs while running the requests
  ```json
  gitpod /workspace/aws-bootcamp-cruddur-2023 (main) $ docker logs -f e0a3bc15aca1
  ...
{
    "name": "/api/activities/home",
    "context": {
        "trace_id": "0xca6434c0cf906fd9a3bc106060a88567",
        "span_id": "0xf349d077a4ec7db8",
        "trace_state": "[]"
    },
    "kind": "SpanKind.SERVER",
    "parent_id": null,
    "start_time": "2023-02-28T13:06:08.833089Z",
    "end_time": "2023-02-28T13:06:08.834375Z",
    "status": {
        "status_code": "UNSET"
    },
    "attributes": {
        "http.method": "GET",
        "http.server_name": "0.0.0.0",
        "http.scheme": "http",
        "net.host.port": 4567,
        "http.host": "localhost:4567",
        "http.target": "/api/activities/home",
        ...
        "http.route": "/api/activities/home",
        "http.status_code": 200
    },
  ...
    "resource": {
        "attributes": {
            "telemetry.sdk.language": "python",
            "telemetry.sdk.name": "opentelemetry",
            "telemetry.sdk.version": "1.16.0",
            "service.name": "backend-flask"
    ...
```

### **Explore with Honeycomb**
[Back to top](#Week-2)

- Chceck the bootcamp environment Home page
<img  alt="image" src="https://user-images.githubusercontent.com/91587569/221942102-c2e51f02-a14d-4156-be7e-af7a9d874dc8.png">

- Go to "**New Query**" on the left navigation menu then click on "**Run Query**"
- **Raw Data** tab will list all the recent requests or events from the backend app
<img  alt="image" src="https://user-images.githubusercontent.com/91587569/221943056-bb346d08-8855-4dcc-aef0-f27402990454.png">


## Instrument AWS X-Ray

### Initial Setup


### Resources Setup


### Daemon Service Setup


### Create Group and Test Rule

---------------------------------------------
---------------------------------------------

##  Challenges
[Back to top](#Week-2)

### **Add NEW Span and Attributes**
[Back to top](#Week-2)

>> **NOTE:** output has been reduced!

1. Create a new **Mock Home Endpoint** (Ref. [Week-1 Notifications Endpoint](https://github.com/astroveny/aws-bootcamp-cruddur-2023/blob/main/journal/week1.md#create-the-notification-feature))
    -   Add new PATH "/api/activities/mockhome" and "GET" operator to the OpenAPI file 
    -   Created a copy of home service  under services: `mockhome_activities.py`
    -   Update flask app to import the new service and add new route
 
3. Update [mockhome_activities.py](https://github.com/astroveny/aws-bootcamp-cruddur-2023/blob/main/backend-flask/services/mockhome_activities.py) by adding new span & Attributes (Ref. [Honeycomb Docs](https://docs.honeycomb.io/getting-data-in/opentelemetry/python/#adding-attributes-to-spans))
4. **Restart/run docker compose**
5. **Test and Generate Data**
```json
gitpod /workspace/aws-bootcamp-cruddur-2023 (main) $ curl -X GET http://localhost:4567/api/activities/mockhome -H "Accept: application/json" -H "Content-Type: application/json"
[
  {
    "created_at": "2023-02-26T15:45:39.217236+00:00",
    "expires_at": "2023-03-05T15:45:39.217236+00:00",
    "handle": "Andrew Brown",
    "likes_count": 5,
    "message": "Mock this: Cloud is fun!",
    ...

```
7. **Explore with Honeycomb**
   -   **Traces**   
   

     <img  alt="image" src="https://user-images.githubusercontent.com/91587569/221948776-b260bd77-b59d-4fdd-94ff-28f19b9a56da.png"><br>  
   
   -   **Routes latency**   
   
      <img  alt="image" src="https://user-images.githubusercontent.com/91587569/221948892-3799b30e-14a9-4f32-9371-e5b3f387e707.png"><br>   
   
   -   **Heatmap duration in ms** 
   
   <img  alt="image" src="https://user-images.githubusercontent.com/91587569/221948823-80de853a-e33b-439f-8830-f1de1b55c560.png"><br>    
   
   

