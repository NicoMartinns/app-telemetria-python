from opentelemetry import metrics
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.exporter.otlp.proto.http.metric_exporter import OTLPMetricExporter
from opentelemetry.semconv.attributes.service_attributes import SERVICE_NAME, SERVICE_VERSION

resource = Resource.create({
    SERVICE_NAME: "app-telemetria-teste",
    SERVICE_VERSION: "1.0.0",
})

metric_exporter = OTLPMetricExporter(
    endpoint="http://201.23.70.15:4318/v1/metrics"
)

metric_reader = PeriodicExportingMetricReader(
    exporter=metric_exporter,
    export_interval_millis=5000,
)

provider = MeterProvider(
    resource=resource,
    metric_readers=[metric_reader],
)

metrics.set_meter_provider(provider)
meter = metrics.get_meter("app-telemetria-teste")

requests_counter = meter.create_counter(
    name="app_requests_total",
    description="Total de requisições da aplicação",
    unit="1",
)

response_time_histogram = meter.create_histogram(
    name="app_response_time_seconds",
    description="Tempo de resposta das requisições",
    unit="s",
)