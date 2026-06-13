# SADS Component Library Loader
import os
import json
from typing import List, Dict, Any, Callable

class ComponentLibraryLoader:
    def __init__(self, file_path: str = None):
        if file_path is None:
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            file_path = os.path.join(base_dir, "data", "component_library.json")
        self.file_path = file_path
        self._data = None

    def _load(self) -> Dict[str, Any]:
        if self._data is None:
            with open(self.file_path, "r") as f:
                self._data = json.load(f)
        return self._data

    def get_all(self) -> Dict[str, Any]:
        return self._load().get("components", {})

    def get_category(self, category: str) -> List[Dict[str, Any]]:
        return self.get_all().get(category, [])

    def filter_components(self, category: str, criteria: Callable[[Dict[str, Any]], bool]) -> List[Dict[str, Any]]:
        items = self.get_category(category)
        return [item for item in items if criteria(item)]
