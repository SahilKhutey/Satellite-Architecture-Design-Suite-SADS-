# SADS Scientific - Monte Carlo Analysis
import numpy as np
from typing import Callable, Dict, Any, Tuple

class MonteCarloAnalysis:
    @staticmethod
    def run_ensemble(
        model_fn: Callable[[Dict[str, Any]], float], 
        base_params: Dict[str, Any], 
        perturbations: Dict[str, Tuple[float, float]],
        samples: int = 100
    ) -> Dict[str, Any]:
        results = []
        for _ in range(samples):
            sampled_params = base_params.copy()
            for key, (mean_offset, std) in perturbations.items():
                if key in sampled_params:
                    sampled_params[key] = float(sampled_params[key] + np.random.normal(mean_offset, std))
            
            results.append(model_fn(sampled_params))
            
        results_arr = np.array(results)
        return {
            "mean": float(np.mean(results_arr)),
            "std": float(np.std(results_arr)),
            "min": float(np.min(results_arr)),
            "max": float(np.max(results_arr)),
            "margin_95_percentile": float(np.percentile(results_arr, 5.0))
        }
