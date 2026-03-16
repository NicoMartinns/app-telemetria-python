from fastapi import FastAPI, HTTPException
import time
import random

from otel_metrics import (
    requests_counter,
    response_time_histogram,
    errors_counter,
    inprogress_gauge,
)

from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.semconv.attributes.service_attributes import SERVICE_NAME
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor

resource = Resource.create({
    SERVICE_NAME: "app-telemetria-teste"
})

trace_provider = TracerProvider(resource=resource)
otlp_exporter = OTLPSpanExporter(
    endpoint="http://201.23.70.15:4318/v1/traces"
)
trace_provider.add_span_processor(BatchSpanProcessor(otlp_exporter))
trace.set_tracer_provider(trace_provider)

app = FastAPI()
FastAPIInstrumentor.instrument_app(app)

@app.get("/")
def root():
    start = time.time()
    attrs = {"endpoint": "/", "method": "GET"}

    inprogress_gauge.add(1, attrs)
    try:
        requests_counter.add(1, attrs)
        return {"message": "ok"}
    finally:
        elapsed = time.time() - start
        response_time_histogram.record(elapsed, attrs)
        inprogress_gauge.add(-1, attrs)

@app.get("/erro")
def erro():
    start = time.time()
    attrs = {"endpoint": "/erro", "method": "GET"}

    inprogress_gauge.add(1, attrs)
    try:
        requests_counter.add(1, attrs)
        errors_counter.add(1, attrs)
        raise HTTPException(status_code=500, detail="erro simulado")
    finally:
        elapsed = time.time() - start
        response_time_histogram.record(elapsed, attrs)
        inprogress_gauge.add(-1, attrs)

@app.get("/lento")
def lento():
    start = time.time()
    attrs = {"endpoint": "/lento", "method": "GET"}

    inprogress_gauge.add(1, attrs)
    try:
        requests_counter.add(1, attrs)
        time.sleep(random.uniform(0.2, 1.2))
        return {"message": "resposta lenta"}
    finally:
        elapsed = time.time() - start
        response_time_histogram.record(elapsed, attrs)
        inprogress_gauge.add(-1, attrs)