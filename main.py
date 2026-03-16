from fastapi import FastAPI
import requests
import time
from otel_metrics import requests_counter, response_time_histogram

# OpenTelemetry
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.semconv.attributes.service_attributes import SERVICE_NAME

# Auto instrumentation
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor


# ============================
# CONFIGURAÇÃO DO SERVICE
# ============================

resource = Resource.create({
    SERVICE_NAME: "app-telemetria-teste"
})

trace_provider = TracerProvider(resource=resource)

otlp_exporter = OTLPSpanExporter(
    endpoint="http://201.23.70.15:4318/v1/traces"
)

trace_provider.add_span_processor(
    BatchSpanProcessor(otlp_exporter)
)

trace.set_tracer_provider(trace_provider)

tracer = trace.get_tracer(__name__)

# ============================
# FASTAPI
# ============================

app = FastAPI()

FastAPIInstrumentor.instrument_app(app)
RequestsInstrumentor().instrument()

@app.get("/")
def root():
    start = time.time()

    requests_counter.add(1, {"endpoint": "/"})

    elapsed = time.time() - start
    response_time_histogram.record(elapsed, {"endpoint": "/"})

    return {"message": "ok"}