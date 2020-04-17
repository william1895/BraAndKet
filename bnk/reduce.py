from typing import Iterable

import numpy as np
from bnk.tensor import HSpace, QTensor, zero, one


class ReducedHSpace(HSpace):
    def __init__(self, psis: Iterable[QTensor], operations: Iterable[QTensor], name=None, key=None):
        org_eigenstates = possible_eigenstates(psis, operations)
        super().__init__(len(org_eigenstates), name, key)
        
        transform = zero
        for i, org_eigenstate in enumerate(org_eigenstates):
            transform += self.eigenstate(i) @ org_eigenstate.ct
        
        self.org_eigenstates = org_eigenstates
        self.transform = transform
    
    def org_eigenstate(self, index):
        return self.org_eigenstates[index]
    
    def reduce(self, tensor: QTensor):
        has_ket = False
        has_bra = False
        for dim in tensor.dims:
            if dim.is_ket:
                has_ket = True
            elif dim.is_bra:
                has_bra = True
        if has_ket:
            tensor = self.transform @ tensor
        if has_bra:
            tensor = tensor @ self.transform.ct
        return tensor
    
    def inflate(self, tensor: QTensor):
        has_ket = False
        has_bra = False
        for dim in tensor.dims:
            if dim.is_ket:
                has_ket = True
            elif dim.is_bra:
                has_bra = True
        if has_ket:
            tensor = self.transform.ct @ tensor
        if has_bra:
            tensor = tensor @ self.transform
        return tensor


def possible_eigenstates(psis: Iterable[QTensor], operations: Iterable[QTensor]):
    def tobi(t: QTensor):
        return QTensor(t.dims, t.values != 0)
    
    all_psi = zero
    for psi in psis:
        all_psi += tobi(psi)
    all_psi = tobi(all_psi)
    
    all_op = zero
    for op in operations:
        all_op += tobi(op)
    all_op = tobi(all_op)
    
    while True:
        new_psi = all_op @ all_psi
        new_psi = tobi(new_psi)
        if new_psi == all_psi:
            break
        all_psi += new_psi
        all_psi = tobi(all_psi)
    
    indices = np.transpose(np.where(all_psi.values))
    eigenstates = []
    for index in indices:
        eigenstate = one
        for i, dim in zip(index, all_psi.dims):
            eigenstate @= dim.space.eigenstate(i)
        eigenstates.append(eigenstate)
    
    return eigenstates
