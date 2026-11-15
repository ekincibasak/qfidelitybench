"""Independent operators, channel oracle, and elementary MSE accounting."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import numpy as np
from qiskit.quantum_info import Operator
from qiskit_aer.noise import (NoiseModel,coherent_unitary_error,amplitude_damping_error,
                             phase_damping_error,depolarizing_error,ReadoutError)
from fixed_midpoint import fixed_midpoint,schedule

ANGLES=[-.1,-.05,-.02,-.01,0.,.01,.02,.05,.1]
GROUPS=['midpoint','local_zz','amplitude','phase','depolarizing','readout','mixed']
ARMS=['forward','reverse','paired','random']
I=np.eye(2,dtype=complex); Z=np.diag([1.,-1.]);ZZ=np.kron(Z,Z)
CX=np.array([[1,0,0,0],[0,0,0,1],[0,0,1,0],[0,1,0,0]],complex)

def ry(a):return np.array([[np.cos(a/2),-np.sin(a/2)],[np.sin(a/2),np.cos(a/2)]],complex)
def rz(a):return np.diag(np.exp(-.5j*a*np.array([1,-1])))
def embed(u,q):return np.kron(I,u) if q==0 else np.kron(u,I)
def preparation(x):
    u=np.eye(4,dtype=complex)
    for g in [embed(ry(x[0]),0),embed(rz(x[1]),0),embed(ry(x[2]),1),embed(rz(x[3]),1),CX,
              embed(ry(.35*x[0]-.20*x[3]),1),embed(rz(.18*x[1]+.29*x[2]),0)]:u=g@u
    return u

def noise(group):
    nm=NoiseModel(basis_gates=['ry','rz','cx'])
    w=np.diag(np.exp(-.5j*.03*np.diag(ZZ)))
    if group=='local_zz':nm.add_all_qubit_quantum_error(coherent_unitary_error(w),['cx'])
    if group in ['amplitude','phase']:
        e=(amplitude_damping_error(.01) if group=='amplitude' else phase_damping_error(.01))
        nm.add_all_qubit_quantum_error(e.tensor(e),['cx'])
    if group=='depolarizing':nm.add_all_qubit_quantum_error(depolarizing_error(.01,2),['cx'])
    if group=='mixed':nm.add_all_qubit_quantum_error(coherent_unitary_error(w).compose(depolarizing_error(.01,2)),['cx'])
    if group in ['readout','mixed']:nm.add_all_qubit_readout_error(ReadoutError([[.99,.01],[.01,.99]]))
    return nm

def channel(rho,group):
    if group in ['local_zz','mixed']:
        w=np.diag(np.exp(-.5j*.03*np.diag(ZZ)));rho=w@rho@w.conj().T
    if group in ['depolarizing','mixed']:rho=.99*rho+.01*np.eye(4)/4
    if group in ['amplitude','phase']:
        if group=='amplitude':ks=[np.diag([1,np.sqrt(.99)]),np.array([[0,.1],[0,0]])]
        else:ks=[np.diag([1,np.sqrt(.99)]),np.diag([0,.1])]
        for q in [0,1]:rho=sum(embed(k,q)@rho@embed(k,q).conj().T for k in ks)
    return rho

def numpy_probabilities(qc,group):
    rho=np.zeros((4,4),complex);rho[0,0]=1
    for item in qc.data:
        name=item.operation.name;qs=[qc.find_bit(q).index for q in item.qubits]
        if name in ['barrier','measure']:continue
        if name=='ry':u=embed(ry(float(item.operation.params[0])),qs[0])
        elif name=='rz':u=embed(rz(float(item.operation.params[0])),qs[0])
        elif name=='cx':
            assert qs==[0,1];u=CX
        else:raise ValueError(name)
        rho=u@rho@u.conj().T
        if name=='cx':rho=channel(rho,group)
    p=np.real(np.diag(rho))
    if group in ['readout','mixed']:
        transition=np.kron(np.array([[.99,.01],[.01,.99]]),np.array([[.99,.01],[.01,.99]]));p=transition@p
    return p

def moments(pf,pr,k,s):
    a=(pf-pr)/2;b=(pf+pr)/2-k;qf=pf*(1-pf);qr=pr*(1-pr)
    bias=np.array([pf-k,pr-k,b,b]);shot=np.array([qf/s,qr/s,(qf+qr)/(2*s),(qf+qr)/(2*s)])
    direction=np.array([np.zeros_like(a),np.zeros_like(a),np.zeros_like(a),a*a])
    return dict(a=a,b=b,bias=bias,shot_variance=shot,direction_variance=direction,
                population_squared_bias=bias*bias,infinite_shot_mse=bias*bias+direction,
                mse=bias*bias+shot+direction)
