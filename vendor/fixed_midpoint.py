"""Fixed gate-level schedule for future M2-B; not used in M2-A sampling."""
from qiskit import QuantumCircuit, transpile
from aer_two_order_pilot import encoding, BASIS_GATES


def fixed_midpoint(x, y, theta):
    qc=QuantumCircuit(2,2)
    qc.compose(encoding(x),inplace=True)
    qc.barrier()
    qc.cx(0,1)
    qc.rz(float(theta),1)
    qc.cx(0,1)
    qc.barrier()
    qc.compose(encoding(y).inverse(),inplace=True)
    qc.measure([0,1],[0,1])
    return transpile(qc,basis_gates=BASIS_GATES,optimization_level=0,
                     seed_transpiler=21,num_processes=1)


def schedule(qc):
    """Ordered operation names and physical wire indices, excluding angles."""
    return [(item.operation.name,[qc.find_bit(q).index for q in item.qubits],
             [qc.find_bit(c).index for c in item.clbits]) for item in qc.data]
