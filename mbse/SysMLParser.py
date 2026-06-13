# SADS - SysML Parser
import json

class SysMLParser:
    @staticmethod
    def parse_blocks_json(json_str: str) -> dict:
        try:
            return json.loads(json_str)
        except Exception:
            return {"blocks": []}
