# coding: utf-8

from __future__ import division, print_function

# Standard library
from collections import OrderedDict

# Third-party
import astropy.units as u
import numpy as np

# Project
from ..dynamics import PhaseSpacePosition
from ..util import atleast_2d
from ..units import UnitSystem, DimensionlessUnitSystem

class PotentialCommonBase(object):

    def _validate_units(self, units):

        # make sure the units specified are a UnitSystem instance
        if units is not None and not isinstance(units, UnitSystem):
            units = UnitSystem(*units)

        elif units is None:
            units = DimensionlessUnitSystem()

        return units

    def _prepare_parameters(self, parameters, units):
        pars = OrderedDict()
        for k,v in parameters.items():
            if hasattr(v, 'unit'):
                pars[k] = v.decompose(units)
            else:
                pars[k] = v*u.one
        return pars

    def _remove_units_prepare_shape(self, x):
        if hasattr(x, 'unit'):
            x = x.decompose(self.units).value

        elif isinstance(x, PhaseSpacePosition):
            x = x.w(self.units)

        x = atleast_2d(x, insert_axis=1).astype(np.float64)
        return x

    def _get_c_valid_arr(self, x):
        """
        Warning! Interpretation of axes is different for C code.
        """
        orig_shape = x.shape
        x = np.ascontiguousarray(x.reshape(orig_shape[0], -1).T)
        return orig_shape, x

    def energy(self, w, t=0.):
        w = self._remove_units_prepare_shape(w)
        orig_shape,w = self._get_c_valid_arr(w)
        return self._energy(w, t=t).T.reshape(orig_shape[1:]) * self.units['energy'] / self.units['mass']

    def gradient(self, w, t=0.):
        w = self._remove_units_prepare_shape(w)
        return self._gradient(w, t=t) # TODO: what to do about units here?

    def hessian(self, w, t=0.):
        w = self._remove_units_prepare_shape(w)

        try:
            return self._hessian(w, t=t) # TODO: what to do about units here?
        except NotImplementedError:
            raise NotImplementedError("This potential has no specified hessian function.")