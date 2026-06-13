# SADS - Aerospace RAG Pipeline
class AerospaceRAG:
    @staticmethod
    def query_reference(topic: str) -> str:
        db = {
            "power": "Wertz SMAD Chapter 11.4: EPS Sizing requires 20-30% solar array EOL margin.",
            "thermal": "Wertz SMAD Chapter 11.5: Passive thermal coatings must maintain LEO temps between -20C and 50C.",
            "adcs": "Wertz SMAD Chapter 11.1: Star Tracker accuracy determines fine pointing budgets down to arcsecond limits."
        }
        return db.get(topic.lower(), "Refer to NASA Spacecraft Design Standards (NASA-STD-5001).")
