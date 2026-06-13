# SADS - Design Reviewer Agent
class DesignReviewer:
    @staticmethod
    def audit_rules(mass_kg: float, dry_mass_limit_kg: float) -> dict:
        margin = (dry_mass_limit_kg - mass_kg) / dry_mass_limit_kg if dry_mass_limit_kg else 0.0
        return {
            "mass_margin_percent": margin * 100.0,
            "compliance": "PASSED" if margin >= 0.10 else "WARNING"
        }
