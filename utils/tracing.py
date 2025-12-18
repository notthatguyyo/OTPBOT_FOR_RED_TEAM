"""Tracing initialization for OTP Voice App using OpenTelemetry.

This module configures an OpenTelemetry TracerProvider with a Console
exporter for local debugging and an OTLP exporter if `OTEL_EXPORTER_OTLP_ENDPOINT`
is set in the environment. It also provides a helper to instrument a Flask app.
"""
import os
import logging
from opentelemetry import trace
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from opentelemetry.sdk.trace.export import SimpleSpanProcessor

logger = logging.getLogger(__name__)


def init_tracing(service_name: str = "otp-voice-app"):
    """Initialize OpenTelemetry tracing.

    - Configures TracerProvider with resource.service.name
    - Adds ConsoleSpanExporter for local visibility
    - If `OTEL_EXPORTER_OTLP_ENDPOINT` is present, adds an OTLP exporter
    """
    try:
        # Prevent double initialization
        if trace.get_tracer_provider() and isinstance(trace.get_tracer_provider(), TracerProvider):
            # already initialized by another module
            return
    except Exception:
        pass

    otel_endpoint = os.environ.get('OTEL_EXPORTER_OTLP_ENDPOINT')

    resource = Resource.create({"service.name": service_name})
    provider = TracerProvider(resource=resource)

    # Console exporter for local debugging
    console_exporter = ConsoleSpanExporter()
    provider.add_span_processor(SimpleSpanProcessor(console_exporter))

    # OTLP exporter if endpoint provided
    if otel_endpoint:
        try:
            otlp_exporter = OTLPSpanExporter(endpoint=otel_endpoint)
            provider.add_span_processor(BatchSpanProcessor(otlp_exporter))
            logger.info("OTLP exporter configured: %s", otel_endpoint)
        except Exception as e:
            logger.warning("Failed to configure OTLP exporter: %s", e)

    trace.set_tracer_provider(provider)

    # Instrument outgoing requests globally
    try:
        RequestsInstrumentor().instrument()
    except Exception:
        logger.debug("Requests instrumentation not applied")

    logger.info("Tracing initialized for %s", service_name)


def instrument_app(app):
    """Instrument a Flask app instance for automatic tracing."""
    try:
        FlaskInstrumentor().instrument_app(app)
        logger.info("Flask app instrumented for tracing")
    except Exception as e:
        logger.warning("Failed to instrument Flask app: %s", e)
