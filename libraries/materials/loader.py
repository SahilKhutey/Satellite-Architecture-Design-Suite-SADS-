# SADS Materials Library Loader
import os
import json
from typing import List, Dict, Any

class MaterialsLibraryLoader:
    def __init__(self, file_path: str = None):
        if file_path is None:
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            file_path = os.path.join(base_dir, "libraries", "materials", "materials_library.json")
        self.file_path = file_path
        self._data = None

    def _load(self) -> Dict[str, Any]:
        if self._data is None:
            with open(self.file_path, "r") as f:
                self._data = json.load(f)
        return self._data

    def get_all(self) -> List[Dict[str, Any]]:
        return self._load().get("materials", [])

    def get_material(self, name: str) -> Dict[str, Any]:
        materials = self.get_all()
        for mat in materials:
            if mat["name"].lower() == name.lower():
                return mat
        return None
