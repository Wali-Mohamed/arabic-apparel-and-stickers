"""Opt-in local telemetry. Only fixed field names and sanitized values leave here.

Deliberately no HTTP/SQL auto-instrumentation, exception recording, baggage,
header/body capture or environment resource detection.
"""
import json
import logging
import os
import time
from contextlib import contextmanager
from contextvars import ContextVar
from functools import wraps

from opentelemetry import trace
from opentelemetry._logs import LogRecord
from opentelemetry.sdk._logs import LoggerProvider
from opentelemetry.sdk._logs.export import BatchLogRecordProcessor
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.trace import Status, StatusCode

_active = ContextVar("app_telemetry", default=None)
ROUTES = {"/api/products", "/api/products/{product_id}",
          "/api/products/{product_id}/price", "/api/orders"}


class Telemetry:
    def __init__(self, traces, logs, metrics):
        self.traces, self.logs, self.metrics = traces, logs, metrics
        self.tracer = traces.get_tracer("apparel")
        self.logger = logs.get_logger("apparel")
        meter = metrics.get_meter("apparel")
        self.count = meter.create_counter("apparel.requests")
        self.errors = meter.create_counter("apparel.errors")
        self.duration = meter.create_histogram("apparel.request.duration", unit="s")

    @contextmanager
    def span(self, name, kind=trace.SpanKind.INTERNAL):
        try:
            span = self.tracer.start_span(name, kind=kind)
        except Exception:
            yield None
            return
        try:
            with trace.use_span(span, end_on_exit=False, record_exception=False,
                                set_status_on_exception=False):
                yield span
        except BaseException:
            try:
                span.set_status(Status(StatusCode.ERROR))
            except Exception:
                pass
            raise
        finally:
            try:
                span.end()
            except Exception:
                pass

    def completed(self, route, method, status, elapsed, span):
        # This method is called while the request span is active (exemplars).
        attributes = {"route": route, "method": method, "status": str(status)}
        self.count.add(1, attributes)
        self.duration.record(elapsed, attributes)
        if status >= 400:
            self.errors.add(1, attributes)
        context = span.get_span_context()
        fields = {"event": "request.completed", **attributes,
                  "duration_seconds": elapsed,
                  "trace_id": format(context.trace_id, "032x"),
                  "span_id": format(context.span_id, "016x")}
        body = json.dumps(fields)
        self.logger.emit(LogRecord(timestamp=time.time_ns(), body=body,
                                   trace_id=context.trace_id, span_id=context.span_id,
                                   trace_flags=context.trace_flags))
        # Dedicated JSON stream, not a dump of request/exception objects.
        print(body, flush=True)

    def shutdown(self):
        for provider in (self.metrics, self.logs, self.traces):
            try:
                provider.shutdown()
            except Exception:
                pass


def configured_telemetry():
    if os.getenv("LOCAL_OBSERVABILITY") != "1":
        return None
    # SDK exporter diagnostics can embed URLs. Do not forward them into logs.
    for name in ("opentelemetry",):
        logger = logging.getLogger(name)
        logger.handlers = [logging.NullHandler()]
        logger.propagate = False
    try:
        from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
        from opentelemetry.exporter.otlp.proto.http._log_exporter import OTLPLogExporter
        from opentelemetry.exporter.otlp.proto.http.metric_exporter import OTLPMetricExporter
        endpoint = os.getenv("LOCAL_OTLP_ENDPOINT", "http://lgtm:4318").rstrip("/")
        resource = Resource({"service.name": "arabic-apparel-api",
                             "deployment.environment.name": "local"})
        traces = TracerProvider(resource=resource)
        traces.add_span_processor(BatchSpanProcessor(OTLPSpanExporter(
            endpoint=endpoint + "/v1/traces", timeout=1), schedule_delay_millis=500))
        logs = LoggerProvider(resource=resource)
        logs.add_log_record_processor(BatchLogRecordProcessor(OTLPLogExporter(
            endpoint=endpoint + "/v1/logs", timeout=1), schedule_delay_millis=500))
        reader = PeriodicExportingMetricReader(OTLPMetricExporter(
            endpoint=endpoint + "/v1/metrics", timeout=1), export_interval_millis=1000)
        return Telemetry(traces, logs, MeterProvider(resource=resource, metric_readers=[reader]))
    except Exception:
        # Optional telemetry must not prevent app startup.
        return None


class TelemetryMiddleware:
    def __init__(self, app, telemetry):
        self.app, self.telemetry = app, telemetry

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            return await self.app(scope, receive, send)
        status = 500
        started = time.perf_counter()

        async def safe_send(message):
            nonlocal status
            if message["type"] == "http.response.start":
                status = message["status"]
            await send(message)

        token = _active.set(self.telemetry)
        try:
            with self.telemetry.span("request", kind=trace.SpanKind.SERVER) as span:
                try:
                    await self.app(scope, receive, safe_send)
                finally:
                    # Router has now resolved the template, never use scope[path].
                    route = getattr(scope.get("route"), "path", "unmatched")
                    if route in ROUTES and span is not None:
                        try:
                            method = scope.get("method")
                            method = method if method in {"GET", "POST", "OPTIONS"} else "OTHER"
                            span.update_name(method + " " + route)
                            span.set_attribute("http.route", route)
                            span.set_attribute("http.response.status_code", status)
                            if status >= 400:
                                span.set_status(Status(StatusCode.ERROR))
                            self.telemetry.completed(route, method, status,
                                                     time.perf_counter() - started, span)
                        except Exception:
                            pass
        finally:
            _active.reset(token)


def operation(name):
    """Decorate sync operations without capturing arguments, results or exceptions."""
    def decorate(function):
        @wraps(function)
        def wrapped(*args, **kwargs):
            telemetry = _active.get()
            if telemetry is None:
                return function(*args, **kwargs)
            with telemetry.span(name):
                return function(*args, **kwargs)
        return wrapped
    return decorate
