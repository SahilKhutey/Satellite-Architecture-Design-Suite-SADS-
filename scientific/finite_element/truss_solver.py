# SADS Scientific - Finite Element 1D/2D Truss Solver
import numpy as np
from typing import List, Dict, Any, Tuple

class TrussElement:
    def __init__(self, node_start: int, node_end: int, E_pa: float, area_m2: float):
        self.node_start = node_start
        self.node_end = node_end
        self.E = E_pa
        self.area = area_m2

class TrussSolver:
    def __init__(self, nodes: List[Tuple[float, float]], elements: List[TrussElement]):
        """
        nodes: list of (x, y) coordinate tuples for each node.
        elements: list of TrussElement objects.
        """
        self.nodes = np.array(nodes, dtype=float)
        self.elements = elements
        self.num_nodes = len(nodes)
        self.num_elements = len(elements)

    def solve(
        self, 
        boundary_conditions: Dict[int, Tuple[bool, bool]], 
        applied_forces: Dict[int, Tuple[float, float]]
    ) -> Dict[str, Any]:
        """
        boundary_conditions: dict mapping node index to (x_fixed, y_fixed) boolean tuple.
        applied_forces: dict mapping node index to (fx, fy) force vector in Newtons.
        """
        num_dof = 2 * self.num_nodes
        K_global = np.zeros((num_dof, num_dof))
        
        # Assemble global stiffness matrix
        for elem in self.elements:
            n1 = elem.node_start
            n2 = elem.node_end
            
            x1, y1 = self.nodes[n1]
            x2, y2 = self.nodes[n2]
            
            dx = x2 - x1
            dy = y2 - y1
            L = np.sqrt(dx**2 + dy**2)
            
            if L == 0:
                continue
                
            c = dx / L
            s = dy / L
            
            # Element stiffness matrix in global coordinates
            k_local = (elem.E * elem.area / L) * np.array([
                [c*c,  c*s, -c*c, -c*s],
                [c*s,  s*s, -c*s, -s*s],
                [-c*c, -c*s, c*c,  c*s],
                [-c*s, -s*s, c*s,  s*s]
            ])
            
            # DOF indices
            dofs = [2*n1, 2*n1+1, 2*n2, 2*n2+1]
            for i in range(4):
                for j in range(4):
                    K_global[dofs[i], dofs[j]] += k_local[i, j]
                    
        # Apply boundary conditions
        fixed_dofs = []
        for node_idx, (x_fixed, y_fixed) in boundary_conditions.items():
            if x_fixed:
                fixed_dofs.append(2 * node_idx)
            if y_fixed:
                fixed_dofs.append(2 * node_idx + 1)
                
        all_dofs = list(range(num_dof))
        free_dofs = [d for d in all_dofs if d not in fixed_dofs]
        
        # Load vector
        F_global = np.zeros(num_dof)
        for node_idx, (fx, fy) in applied_forces.items():
            F_global[2*node_idx] = fx
            F_global[2*node_idx+1] = fy
            
        # Solve for displacements of free DOFs
        u_global = np.zeros(num_dof)
        if len(free_dofs) > 0:
            K_free = K_global[np.ix_(free_dofs, free_dofs)]
            F_free = F_global[free_dofs]
            try:
                u_free = np.linalg.solve(K_free, F_free)
                u_global[free_dofs] = u_free
            except np.linalg.LinAlgError:
                # Singular stiffness matrix (unconstrained motion)
                pass

        # Reaction forces: R = K * U - F
        reaction_forces = np.dot(K_global, u_global) - F_global
        
        # Calculate element axial forces and stresses
        element_results = []
        for idx, elem in enumerate(self.elements):
            n1 = elem.node_start
            n2 = elem.node_end
            
            x1, y1 = self.nodes[n1]
            x2, y2 = self.nodes[n2]
            
            dx = x2 - x1
            dy = y2 - y1
            L = np.sqrt(dx**2 + dy**2)
            
            if L == 0:
                continue
                
            c = dx / L
            s = dy / L
            
            # Retrieve global displacements for this element
            u_elem = np.array([
                u_global[2*n1],
                u_global[2*n1+1],
                u_global[2*n2],
                u_global[2*n2+1]
            ])
            
            # Strain displacement relation: delta = (u2 - u1)*c + (v2 - v1)*s
            delta = (u_elem[2] - u_elem[0])*c + (u_elem[3] - u_elem[1])*s
            stress = (elem.E / L) * delta
            force = stress * elem.area
            
            element_results.append({
                "element_index": idx,
                "length_m": L,
                "stress_mpa": stress / 1e6, # convert to MPa
                "force_n": force
            })
            
        return {
            "displacements_m": u_global.reshape(-1, 2).tolist(),
            "reactions_n": reaction_forces.reshape(-1, 2).tolist(),
            "elements": element_results
        }
