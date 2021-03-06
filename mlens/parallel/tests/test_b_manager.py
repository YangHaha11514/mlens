"""
Test specific functionality of the parallel manager module.
"""
import numpy as np
from scipy.sparse import csr_matrix
from mlens.ensemble.base import LayerContainer
from mlens.utils.dummy import OLS


class OLSSparse(OLS):

    """Handle Sparse Matrices"""

    def fit(self, X, y):
        return super(OLSSparse, self).fit(X.toarray(), y)

    def predict(self, X):
        return super(OLSSparse, self).predict(X.toarray())


X = np.arange(10).reshape(2, 5)
y = np.random.random(2)

first_prop = [1, 2, 3]
n_first_prop = len(first_prop)

second_prop = [i for i in range(n_first_prop)]
second_prop.append(second_prop[-1] + 1)
second_prop.append(second_prop[-1] + 1)
n_second_prop = len(second_prop)

ens1 = LayerContainer()
ens1.add([OLS(0), OLS(1)], 'stack', propagate_features=first_prop)

ens2 = LayerContainer()
ens2.add([OLS(0), OLS(1)], 'stack', propagate_features=first_prop)
ens2.add([OLS(2), OLS(3)], 'stack', propagate_features=second_prop)

ens3 = LayerContainer()
ens3.add([OLSSparse(0), OLSSparse(1)], 'stack', propagate_features=first_prop)
ens3.add([OLSSparse(2), OLSSparse(3)], 'stack', propagate_features=second_prop)


def test_propagation_one():
    """[Parallel] Test feature propagation from original data to first layer"""
    # Check that original data is propagated through first layer
    out_1 = ens1.fit(X, y, return_preds=True)[1]
    np.testing.assert_array_equal(out_1.astype('int32')[:, :n_first_prop], X[:, first_prop])


def test_propagation_two():
    """[Parallel] Test feature propagation from original data to second layer"""
    # Check that original data is propagated through second layer
    out_2 = ens2.fit(X, y, return_preds=True)[1]
    np.testing.assert_array_equal(out_2.astype('int32')[:, :n_first_prop], X[:, first_prop])


def test_propagation_three():
    """[Parallel] Test feature propagation from first layer prediction to second layer"""
    out_1 = ens1.fit(X, y, return_preds=True)[1]
    out_2 = ens2.fit(X, y, return_preds=True)[1]
    np.testing.assert_array_equal(out_2[:, n_first_prop:n_second_prop], out_1[:, n_first_prop:])


def test_sparse():
    """[Parallel] Test sparse feature propagation."""
    out_1 = ens2.fit(X, y, return_preds=True)[1]
    Z = csr_matrix(X)
    out_2 = ens3.fit(Z, y, return_preds=True)[1]
    np.testing.assert_allclose(out_1, out_2.toarray().astype(dtype=np.float32))

