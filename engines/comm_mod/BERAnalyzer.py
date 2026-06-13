# SADS - Bit Error Rate Analyzer
import math
from scipy.special import erfc

class BERAnalyzer:
    @staticmethod
    def calculate_ber_bpsk(eb_no_db: float) -> float:
        eb_no = 10 ** (eb_no_db / 10.0)
        return 0.5 * erfc(math.sqrt(eb_no))
