class MissionAdvisor:
    @staticmethod
    def advise_trajectory(launch_mass_kg: float, delta_v_required_m_s: float, isp_s: float) -> dict:
        import math
        g0 = 9.80665
        mass_ratio = math.exp(delta_v_required_m_s / (isp_s * g0))
        propellant_mass = launch_mass_kg * (1.0 - 1.0 / mass_ratio)
        dry_mass = launch_mass_kg / mass_ratio
        
        status = "FEASIBLE" if dry_mass > 0.10 * launch_mass_kg else "MARGINAL"
        return {
            "propellant_mass_kg": propellant_mass,
            "dry_mass_limit_kg": dry_mass,
            "feasibility": status,
            "recommendation": "Mission is feasible. Fuel fraction is within safe limit." if status == "FEASIBLE" else "Warning: high fuel fraction. Consider a higher Isp thruster (e.g. electric propulsion)."
        }
