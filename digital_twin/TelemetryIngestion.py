# SADS - Telemetry Ingestion
import json

class TelemetryIngestion:
    @staticmethod
    def parse_stream_frame(frame_str: str) -> dict:
        try:
            return json.loads(frame_str)
        except Exception:
            return {}
