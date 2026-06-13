# SADS - Structures Engine
import numpy as np
from typing import List, Dict, Any, Tuple, Optional
import importlib

# Dynamic imports for the hyphenated sub-packages
launch_loads_mod = importlib.import_module("engines.structures-engine.launch_loads.models")
LaunchLoads = launch_loads_mod.LaunchLoads

stress_mod = importlib.import_module("engines.structures-engine.stress_analysis.models")
StressAnalysisSolver = stress_mod.StressAnalysisSolver

vibe_mod = importlib.import_module("engines.structures-engine.vibration_analysis.models")
VibrationAnalysis = vibe_mod.VibrationAnalysis

from scientific.finite_element.truss_solver import TrussSolver, TrussElement

class StructuralComponent:
    def __init__(self, name: str, mass_kg: float, position_m: List[float]):
        self.name = name
        self.mass_kg = mass_kg
        self.position = np.array(position_m, dtype=float)

class StructuresEngine:
    def __init__(
        self, 
        components: List[StructuralComponent],
        nodes: Optional[List[Tuple[float, float]]] = None,
        elements: Optional[List[Tuple[int, int, float, float]]] = None,
        applied_forces: Optional[Dict[int, Tuple[float, float]]] = None,
        boundary_conditions: Optional[Dict[int, Tuple[bool, bool]]] = None,
        static_g_axial: float = 6.0,
        dynamic_g_lateral: float = 2.0,
        stiffness_n_m: float = 1e7
    ):
        self.components = components
        self.nodes = nodes
        self.elements = elements
        self.applied_forces = applied_forces
        self.boundary_conditions = boundary_conditions
        self.static_g_axial = static_g_axial
        self.dynamic_g_lateral = dynamic_g_lateral
        self.stiffness_n_m = stiffness_n_m

    def calculate_total_mass(self) -> float:
        return sum(c.mass_kg for c in self.components)

    def calculate_center_of_mass(self) -> np.ndarray:
        total_mass = self.calculate_total_mass()
        if total_mass == 0:
            return np.zeros(3)
        weighted_sum = sum(c.mass_kg * c.position for c in self.components)
        return weighted_sum / total_mass

    def calculate_inertia_tensor(self) -> np.ndarray:
        com = self.calculate_center_of_mass()
        I = np.zeros((3, 3))
        for c in self.components:
            r = c.position - com
            x, y, z = r[0], r[1], r[2]
            I[0, 0] += c.mass_kg * (y**2 + z**2)
            I[1, 1] += c.mass_kg * (x**2 + z**2)
            I[2, 2] += c.mass_kg * (x**2 + y**2)
            I[0, 1] -= c.mass_kg * (x * y)
            I[0, 2] -= c.mass_kg * (x * z)
            I[1, 2] -= c.mass_kg * (y * z)
        I[1, 0] = I[0, 1]
        I[2, 0] = I[0, 2]
        I[2, 1] = I[1, 2]
        return I

    def run_structural_fe_analysis(self) -> Optional[Dict[str, Any]]:
        if not self.nodes or not self.elements:
            return None
            
        truss_elems = [TrussElement(e[0], e[1], e[2], e[3]) for e in self.elements]
        solver = TrussSolver(self.nodes, truss_elems)
        
        bc = self.boundary_conditions or {}
        forces = self.applied_forces or {}
        
        if not forces:
            total_mass = self.calculate_total_mass()
            ll = LaunchLoads(self.static_g_axial, self.dynamic_g_lateral)
            f_inertial = ll.calculate_inertial_force_n(total_mass)
            
            fixed_nodes = set(bc.keys())
            free_nodes = [i for i in range(len(self.nodes)) if i not in fixed_nodes]
            if free_nodes:
                f_per_node = f_inertial / len(free_nodes)
                forces = {node_idx: (0.0, -f_per_node) for node_idx in free_nodes}
                
        return solver.solve(bc, forces)

    def report(self) -> dict:
        com = self.calculate_center_of_mass()
        I = self.calculate_inertia_tensor()
        total_mass = self.calculate_total_mass()
        
        ll = LaunchLoads(self.static_g_axial, self.dynamic_g_lateral)
        eq_accel = ll.calculate_equivalent_acceleration()
        inertial_force = ll.calculate_inertial_force_n(total_mass)
        
        nat_freq = VibrationAnalysis.calculate_natural_frequency_hz(self.stiffness_n_m, total_mass)
        vibe_compliance = VibrationAnalysis.audit_frequency_compliance(nat_freq, 50.0)
        
        fe_results = self.run_structural_fe_analysis()
        
        stresses = []
        safety_factors = []
        if fe_results:
            for elem in fe_results["elements"]:
                stresses.append(abs(elem["stress_mpa"]))
                fos = StressAnalysisSolver.factor_of_safety(276.0, abs(elem["stress_mpa"]))
                safety_factors.append(fos)
                elem["safety_factor"] = fos
                
        max_stress = max(stresses) if stresses else 0.0
        min_fos = min(safety_factors) if safety_factors else float('inf')
        
        return {
            "total_mass_kg": total_mass,
            "center_of_mass_m": com.tolist(),
            "inertia_tensor_kg_m2": I.tolist(),
            "launch_loads": {
                "equivalent_acceleration_g": eq_accel,
                "inertial_force_n": inertial_force
            },
            "vibration_analysis": {
                "natural_frequency_hz": nat_freq,
                "compliance": vibe_compliance
            },
            "finite_element_analysis": fe_results,
            "safety_margins": {
                "max_stress_mpa": max_stress,
                "minimum_factor_of_safety": min_fos,
                "margins_ok": bool(min_fos >= 1.5) if min_fos != float('inf') else True
            }

        }

