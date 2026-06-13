from .MissionSimulator import MissionSimulator

class ScenarioRunner:
    @staticmethod
    def run_iss_scenario() -> dict:
        sim = MissionSimulator(steps=150)
        output = sim.run()
        return {
            "scenario": "ISS Orbit",
            "simulator_output": output,
            "status": "COMPLETED"
        }
