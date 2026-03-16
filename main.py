from fastapi import FastAPI
import requests

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
    endpoint="http://http://201.23.70.15/:4318/v1/traces"
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
    return {"message": "app-telemetria-teste rodando"}


@app.get("/teste")
def teste():

    with tracer.start_as_current_span("teste-span"):

        r = requests.get("https://httpbin.org/get")

        return {
            "status": r.status_code
        }