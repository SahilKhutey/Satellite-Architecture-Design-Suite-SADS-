# SADS - Quaternion Math
import math

class QuaternionMath:
    @staticmethod
    def normalize(q: list) -> list:
        norm = math.sqrt(sum(x*x for x in q))
        return [x/norm for x in q]
