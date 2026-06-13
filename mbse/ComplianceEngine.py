from typing import List, Dict, Any
from mbse.InterfaceDefinitions import Port

class ComplianceEngine:
    @staticmethod
    def generate_signoff_log(verification_results: List[dict]) -> str:
        passed = all(r["satisfied"] for r in verification_results)
        log = "SADS MBSE COMPLIANCE REPORT\n"
        log += f"Status: {'PASSED' if passed else 'FAILED'}\n"
        for r in verification_results:
            status = "OK" if r["satisfied"] else "FAIL"
            log += f"Req: {r['requirement_id']:<10} Value: {r['measured_value']:.2f} Limit: {r['limit_value']:.2f} [{status}]\n"
        return log

    @staticmethod
    def audit_ports_compatibility(
        blocks_with_ports: Dict[str, List[Port]], 
        connections: List[Dict[str, str]]
    ) -> List[Dict[str, Any]]:
        """
        Audit connections in SysML Internal Block Diagrams to verify interface compatibility.
        """
        audit_logs = []
        for conn in connections:
            from_block = conn.get("from_block")
            from_port_name = conn.get("from_port")
            to_block = conn.get("to_block")
            to_port_name = conn.get("to_port")
            
            # Find ports
            port_src = None
            if from_block in blocks_with_ports:
                for p in blocks_with_ports[from_block]:
                    if p.name == from_port_name:
                        port_src = p
                        break
            
            port_dst = None
            if to_block in blocks_with_ports:
                for p in blocks_with_ports[to_block]:
                    if p.name == to_port_name:
                        port_dst = p
                        break
            
            if not port_src:
                audit_logs.append({
                    "connection": conn,
                    "compatible": False,
                    "reason": f"Source port '{from_port_name}' on block '{from_block}' not found."
                })
                continue
                
            if not port_dst:
                audit_logs.append({
                    "connection": conn,
                    "compatible": False,
                    "reason": f"Destination port '{to_port_name}' on block '{to_block}' not found."
                })
                continue
                
            # Compatibility checks
            if port_src.port_type != "output" or port_dst.port_type != "input":
                audit_logs.append({
                    "connection": conn,
                    "compatible": False,
                    "reason": f"Invalid port directions. Source must be output, destination input."
                })
                continue
                
            if port_src.flow_type != port_dst.flow_type:
                audit_logs.append({
                    "connection": conn,
                    "compatible": False,
                    "reason": f"Flow types do not match: source flow '{port_src.flow_type}' vs destination flow '{port_dst.flow_type}'."
                })
                continue
                
            if port_src.capacity < port_dst.capacity:
                audit_logs.append({
                    "connection": conn,
                    "compatible": False,
                    "reason": f"Capacity mismatch: source capacity {port_src.capacity} is less than required destination capacity {port_dst.capacity}."
                })
                continue
                
            audit_logs.append({
                "connection": conn,
                "compatible": True,
                "reason": "Interface flow and capacity are compatible."
            })
            
        return audit_logs

