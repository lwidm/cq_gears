import pytest

import cq_gears
from cq_gears import (
    Gear,
    ParametricGear,
    HobbedGear,
    make_spur_gear_data,
)
from cq_gears.core import SpurGearData

# ================================================================================
# build_parametric_gear   (existing — keep as-is)
# ================================================================================


class TestBuildParametricGear:
    def test_returns_parametric_gear(self, any_gear) -> None:
        pg: ParametricGear = cq_gears.build_parametric_gear(
            geardata=any_gear, n_spline_points=200
        )

        assert isinstance(pg, ParametricGear)
        assert isinstance(pg, Gear)
        assert pg.data is any_gear
        assert pg.workplane is not None


# ================================================================================
# build_hobbed_gear (single)
# ================================================================================


class TestBuildHobbedGear:
    def test_spur_returns_hobbed_gear(self, spur) -> None:
        hg: HobbedGear = cq_gears.build_hobbed_gear(
            geardata=spur,
            n_cut_positions=4,
            visualize=None,
            gear_index=0,
        )
        assert isinstance(hg, HobbedGear)
        assert isinstance(hg, Gear)
        assert hg.data is spur
        assert hg.workplane is not None
        assert hg.cutter is not None

    def test_helical_returns_hobbed_gear(self, helical) -> None:
        hg: HobbedGear = cq_gears.build_hobbed_gear(
            geardata=helical,
            n_cut_positions=4,
            visualize=None,
            gear_index=0,
        )
        assert isinstance(hg, HobbedGear)
        assert hg.data is helical

    def test_rack_raises(self, rack) -> None:
        with pytest.raises(NotImplementedError):
            cq_gears.build_hobbed_gear(
                geardata=rack,
                n_cut_positions=4,
                visualize=None,
                gear_index=0,
            )

    def test_helical_rack_raises(self, helical_rack) -> None:
        with pytest.raises(NotImplementedError):
            cq_gears.build_hobbed_gear(
                geardata=helical_rack,
                n_cut_positions=4,
                visualize=None,
                gear_index=0,
            )

    def test_internal_spur_raises(self, internal_spur) -> None:
        with pytest.raises(NotImplementedError):
            cq_gears.build_hobbed_gear(
                geardata=internal_spur,
                n_cut_positions=4,
                visualize=None,
                gear_index=0,
            )

    def test_internal_helical_raises(self, internal_helical) -> None:
        with pytest.raises(NotImplementedError):
            cq_gears.build_hobbed_gear(
                geardata=internal_helical,
                n_cut_positions=4,
                visualize=None,
                gear_index=0,
            )


# ================================================================================
# build_hobbed_gear_list   (batch with rack sharing)
# ================================================================================


class TestBuildHobbedGearList:
    def test_empty_list(self) -> None:
        result: list[HobbedGear] = cq_gears.build_hobbed_gear_list(
            geardata_list=[],
            n_cut_positions=4,
            visualize=None,
        )
        assert result == []

    def test_single_gear(self, spur) -> None:
        result: list[HobbedGear] = cq_gears.build_hobbed_gear_list(
            geardata_list=[spur],
            n_cut_positions=4,
            visualize=None,
        )
        assert len(result) == 1
        assert isinstance(result[0], HobbedGear)
        assert result[0].data is spur

    def test_compatible_gears_share_cutter(self) -> None:
        a: SpurGearData = make_spur_gear_data(m_n=1.0, z=20, b=10.0)
        b: SpurGearData = make_spur_gear_data(m_n=1.0, z=40, b=15.0)

        result: list[HobbedGear] = cq_gears.build_hobbed_gear_list(
            geardata_list=[a, b],
            n_cut_positions=4,
            visualize=None,
        )
        assert len(result) == 2
        assert result[0].cutter is result[1].cutter

    def test_incompatible_gears_get_separate_cutters(self) -> None:
        a: SpurGearData = make_spur_gear_data(m_n=1.0, z=20, b=10.0)
        b: SpurGearData = make_spur_gear_data(m_n=2.0, z=20, b=10.0)  # different m_n

        result: list[HobbedGear] = cq_gears.build_hobbed_gear_list(
            geardata_list=[a, b],
            n_cut_positions=4,
            visualize=None,
        )
        assert result[0].cutter is not result[1].cutter

    def test_order_preserved(self) -> None:
        """Output list aligns positionally with input list, regardless of grouping."""
        a: SpurGearData = make_spur_gear_data(m_n=1.0, z=20, b=10.0)
        b: SpurGearData = make_spur_gear_data(m_n=2.0, z=20, b=10.0)
        c: SpurGearData = make_spur_gear_data(
            m_n=1.0, z=40, b=15.0
        )  # back to group of `a`

        result: list[HobbedGear] = cq_gears.build_hobbed_gear_list(
            geardata_list=[a, b, c],
            n_cut_positions=4,
            visualize=None,
        )
        assert result[0].data is a
        assert result[1].data is b
        assert result[2].data is c
        # And the cutter sharing is correct: a and c share, b alone
        assert result[0].cutter is result[2].cutter
        assert result[0].cutter is not result[1].cutter
