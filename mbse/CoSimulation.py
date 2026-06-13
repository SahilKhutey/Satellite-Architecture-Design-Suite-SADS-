# SADS - SysML v2 Co-Simulation Bridge
import json
from typing import Dict, List, Any
from .SysMLParser import SysMLParser
from .RequirementsManager import RequirementsManager, Requirement
from .TraceabilityEngine import TraceabilityEngine
from .VerificationMatrix import VerificationMatrix
from .ComplianceEngine import ComplianceEngine

from engines.power_engine import PowerBudget, SolarArray, Battery, Load
from engines.orbit_engine import circular_orbit

class SysMLCoSimulator:
    @staticmethod
    def run_sysml_co_simulation(sysml_blocks_json: str, altitude_km: float = 400.0) -> Dict[str, Any]:
        """
        Parses SysML v2 block definitions, instantiates corresponding physics budget engines,
        runs simulations, and audits compliance.
        """
        parsed_data = SysMLParser.parse_blocks_json(sysml_blocks_json)
        blocks = parsed_data.get("blocks", [])
        
        solar_arrays = []
        batteries = []
        loads = []
        
        # Instantiate Requirements & Traceability
        rm = RequirementsManager()
        te = TraceabilityEngine()
        measured_values = {}
        
        for block in blocks:
            name = block.get("name")
            block_type = block.get("type", "").lower()
            properties = block.get("properties", {})
            
            # 1. Map SysML blocks to physics solver objects
            if "solar" in block_type or "solar" in name.lower():
                area = float(properties.get("area_m2", 1.0))
                eff = float(properties.get("efficiency", 0.30))
                solar_arrays.append(SolarArray(name=name, area=area, efficiency=eff))
                measured_values[name] = area * eff * 1361.0 # estimated power W
                
            elif "battery" in block_type or "battery" in name.lower():
                cap = float(properties.get("capacity_wh", 50.0))
                dod = float(properties.get("dod_limit", 0.30))
                batteries.append(Battery(name=name, capacity_wh=cap, dod_limit=dod))
                measured_values[name] = cap * dod # usable energy Wh
                
            elif "load" in block_type or properties.get("power_draw_w") is not None:
                power = float(properties.get("power_draw_w", 10.0))
                loads.append(Load(name=name, nominal_power_w=power))
                measured_values[name] = power
                
            # 2. Extract and register SysML requirements
            reqs = block.get("requirements", [])
            for r in reqs:
                req_id = r.get("id")
                req_name = r.get("name")
                category = r.get("category", "power")
                limit_val = float(r.get("limit_value", 0.0))
                op = r.get("operator", "less_than")
                
                req_obj = Requirement(id=req_id, name=req_name, category=category, limit_value=limit_val, operator=op)
                rm.add_requirement(req_obj)
                te.add_trace(req_id, name)
                
        # 3. Compute orbit eclipse parameters for power budget sizing
        orbit = circular_orbit(altitude_km)
        eclipse_min = orbit.eclipse_duration_s() / 60.0
        period_min = orbit.orbital_period_s() / 60.0
        
        # 4. Execute Co-Simulation solver
        budget = PowerBudget(
            solar_arrays=solar_arrays,
            batteries=batteries,
            loads=loads,
            eclipse_duration_min=eclipse_min,
            orbit_period_min=period_min
        )
        power_report = budget.power_balance()
        
        # 5. MBSE Compliance Audits
        # Map physics report fields for requirements matching
        sim_results = {
            "Total_Generation": power_report["generation_w"],
            "Total_Load": power_report["average_load_w"],
            "Battery_Margin": power_report["battery_margin"]
        }
        
        # Update measured values for requirements verification mapping
        # Requirements might check individual components or overall totals
        verification_inputs = {}
        verification_inputs.update(measured_values)
        verification_inputs["Total_Generation"] = power_report["generation_w"]
        verification_inputs["Total_Load"] = power_report["average_load_w"]
        verification_inputs["Battery_Margin"] = power_report["battery_margin"]
        
        verification_results = VerificationMatrix.verify_all(rm, te, verification_inputs)
        signoff_log = ComplianceEngine.generate_signoff_log(verification_results)
        
        return {
            "orbit_parameters": {
                "altitude_km": altitude_km,
                "period_min": period_min,
                "eclipse_min": eclipse_min
            },
            "solver_report": power_report,
            "verification_results": verification_results,
            "signoff_log": signoff_log
        }
