"""Replay archived two-qubit measurements; no RNG, Aer jobs or new experiment."""
import hashlib,json,sys
from pathlib import Path
import numpy as np
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE/'vendor'));sys.path.insert(0,str(HERE/'vendor/m2b'))
from core import preparation,moments,numpy_probabilities,ARMS
from fixed_midpoint import fixed_midpoint

def main():
    for name,item in json.loads((HERE/'source_manifest.json').read_text()).items():
        if hashlib.sha256((HERE/name).read_bytes()).hexdigest()!=item['sha256']:raise RuntimeError('Verified source copy changed')
    print('ARCHIVED MEASUREMENT REPLAY — no new shots or scientific comparisons')
    for case in json.loads((HERE/'archived_example.json').read_text())['cases']:
        x,y=case['features'];s=case['shots'];theta=case['theta'];counts=np.array(case['counts'])
        assert counts.shape==(5,4) and (counts>=0).all()
        np.testing.assert_array_equal(counts.sum(axis=1),[s,s,s//2,s//2,s])
        pf=numpy_probabilities(fixed_midpoint(x,y,theta),'midpoint')[0]
        pr=numpy_probabilities(fixed_midpoint(y,x,theta),'midpoint')[0]
        k=abs(np.vdot(preparation(y)[:,0],preparation(x)[:,0]))**2
        model=moments(pf,pr,k,s)
        n=counts[:,0];est=np.array([n[0],n[1],n[2]+n[3],n[4]])/s
        np.testing.assert_array_equal(est,case['historical_estimates'])
        if theta==0:np.testing.assert_allclose([pf,pr],[k,k],atol=1e-12)
        np.testing.assert_allclose(model['mse'][3]-model['mse'][2],model['a']**2,atol=1e-14)
        print(f'\ntheta={theta:.2f}, ideal={k:.8f}, p_forward={pf:.8f}, p_reverse={pr:.8f}')
        for i,arm in enumerate(ARMS):print(f'{arm:8} estimate={est[i]:.8f} total_shots={s} circuit_executions={2 if arm=="paired" else 1}')
        print('Saved random direction:', ['forward','reverse'][case['direction']])
    print('\nPASS: archived counts, equal budgets, verified functions and noiseless reference.')
    print('One archived repetition cannot establish a performance improvement.')
if __name__=='__main__':main()
