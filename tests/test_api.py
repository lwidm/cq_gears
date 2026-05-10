import cq_gears
from cq_gears.core import ParametricGear, Gear

class TestApiFunctinos:
    def test_build_parametric_gear_returns_parametric_gear(self, spur):
        pg = cq_gears.build_parametric_gear(geardata=spur, n_spline_points=200)

        assert isinstance(pg, ParametricGear)
        assert isinstance(pg, Gear)  # satisfies Protocol
        assert pg.data is spur  # data passed through unchanged
        assert pg.workplane is not None
