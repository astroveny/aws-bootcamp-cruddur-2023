# Week 2

## Distributed Tracing

During this stage, we will intigrate our distributed system with an observability solution (**Honeycomb**) that will be used to monitor and observe requests as they flow through the distributed services. Using distributed tracing will simplify debugging, verifying and comparing services' response time, and spotting unusual patterns.
This would allow us to see and understand how the distributed services handle a single request and apply changes as required.

### Open Ports using Gitpod.yml
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

### Honeycomb Integration 

#### **Initial Setup**

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
#### Test and validate Honeycomb Spans



#### **Add NEW Span and Attributes**

1. Create a new **Mock Home Endpoint** (Ref. [Week-1 Notifications Endpoint](https://github.com/astroveny/aws-bootcamp-cruddur-2023/blob/main/journal/week1.md#create-the-notification-feature))
  - Add new PATH "/api/activities/mockhome" and "GET" operator to the OpenAPI file 
  - Created a copy of home service  under services: `mockhome_activities.py`
  - Update flask app to import the new service and add new route
 
3. Update [mockhome_activities.py](https://github.com/astroveny/aws-bootcamp-cruddur-2023/blob/main/backend-flask/services/mockhome_activities.py) by adding new span & Attributes (Ref. [Honeycomb Docs](https://docs.honeycomb.io/getting-data-in/opentelemetry/python/#adding-attributes-to-spans))
4. Restart/run docker compose 
5. Access the endpoint to generate spans on Honeycomb
6. Honeycomb sample results
   1. Traces
   2. Routes latency
   3. Heatmap duration in ms
