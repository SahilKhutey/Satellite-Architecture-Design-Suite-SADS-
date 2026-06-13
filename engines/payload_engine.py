# SADS Payload Engine Wrapper to support standard dot imports
import sys
import importlib

# Dynamic import of the hyphenated module parts
mod = importlib.import_module("engines.payload-engine.payload_model")
sys.modules[__name__ + ".payload_model"] = mod

opt_mod = importlib.import_module("engines.payload-engine.optical.optical_payload")
sys.modules[__name__ + ".optical"] = opt_mod

radar_mod = importlib.import_module("engines.payload-engine.radar.radar_payload")
sys.modules[__name__ + ".radar"] = radar_mod

comm_mod = importlib.import_module("engines.payload-engine.communication.comm_payload")
sys.modules[__name__ + ".communication"] = comm_mod

sci_mod = importlib.import_module("engines.payload-engine.science.science_payload")
sys.modules[__name__ + ".science"] = sci_mod

pkg_mod = importlib.import_module("engines.payload-engine")

# Expose classes directly at module level
PayloadComponent = mod.PayloadComponent
PayloadSystem = mod.PayloadSystem
OpticalPayloadModel = opt_mod.OpticalPayloadModel
RadarPayloadModel = radar_mod.RadarPayloadModel
CommPayloadModel = comm_mod.CommPayloadModel
SciencePayloadModel = sci_mod.SciencePayloadModel
OpticalPayload = pkg_mod.OpticalPayload
