"""Tests for cq_gears.core."""

import numpy as np
import pytest
from dataclasses import FrozenInstanceError
from typing import get_args
import cadquery as cq

from cq_gears import (
    GearData,
    SpurGearData,
    HelicalGearData,
    InternalSpurGearData,
    InternalHelicalGearData,
    BevelGearData,
    WormGearData,
    CrossedHelicalGearData,
    HypoidGearData,
    make_spur_gear_data,
    make_helical_gear_data,
    # make_internal_spur_gear_data,
    # make_internal_helical_gear_data,
    make_bevel_gear_data,
    make_worm_gear_data,
    make_crossed_helical_gear_data,
    make_hypoid_gear_data,
    Gear,
    ParametricGear,
    HobbedGear,
)

from cq_gears.core import (
    is_helical,
    is_internal,
    GearDataConcrete,
    GearConcrete,
    implemented_gear_types,
    implemented_gear_solids,
)

# ================================================================================
# Registry invariants
#
# These tests catch the most common "I added a new gear type
# but forgot to update X" mistakes.
# ================================================================================


class TestRegistryInvariants:
    def test_gear_data_concrete_covers_registry(self):
        """
        Every class registered with @register_gear_type must appear
        in the GearDataConcrete union, and vice versa.
        """
        registered: set[type] = set(implemented_gear_types())
        in_union: set[type] = set(get_args(GearDataConcrete))

        missing_from_union: set[type] = registered - in_union
        unregistered_in_union: set[type] = in_union - registered

        assert not missing_from_union, (
            f"GearDataConcrete is missing registered classes: "
            f"{sorted(c.__name__ for c in missing_from_union)}. "
            f"Add them to the union in core.py."
        )
        assert not unregistered_in_union, (
            f"GearDataConcrete contains unregistered classes: "
            f"{sorted(c.__name__ for c in unregistered_in_union)}. "
            f"Either decorate the class with @register_gear_type "
            f"or remove it from the union."
        )

    def test_gear_concrete_covers_registry(self):
        """
        Every class registered with @register_gear_solid must appear
        in the GearConcrete union, and vice versa.
        """
        registered: set[type] = set(implemented_gear_solids())
        in_union: set[type] = set(get_args(GearConcrete))

        missing_from_union: set[type] = registered - in_union
        unregistered_in_union: set[type] = in_union - registered

        assert not missing_from_union, (
            f"GearConcrete is missing registered classes: "
            f"{sorted(c.__name__ for c in missing_from_union)}. "
            f"Add them to the union in core.py."
        )
        assert not unregistered_in_union, (
            f"GearConcrete contains unregistered classes: "
            f"{sorted(c.__name__ for c in unregistered_in_union)}. "
            f"Either decorate the class with @register_gear_solid "
            f"or remove it from the union."
        )

    def test_any_gear_fixture_covers_registry(
        self, spur, helical, internal_spur, internal_helical
    ):
        """
        Every registered gear type must have a fixture so it appears
        in 'any_gear'-parametrized tests.

        If a new registered type doesn't show up here, this test fails
        with a clear message pointing at the missing fixture.
        """
        fixture_classes: set[type] = {
            type(spur),
            type(helical),
            type(internal_spur),
            type(internal_helical),
        }
        registered: set[type] = set(implemented_gear_types())

        missing_from_fixtures: set[type] = registered - fixture_classes
        missing_from_registered: set[type] = fixture_classes - registered
        assert not missing_from_fixtures, (
            f"Per-type fixture missing in conftest.py for: "
            f"{sorted(c.__name__ for c in missing_from_fixtures)}. "
            f"Add a fixture and update both the function signature "
            f"of this test AND the `any_gear` params list."
        )
        assert not missing_from_registered, (
            f"Per-type fixture in conftest.py does not appear to be registered: "
            f"{sorted(c.__name__ for c in missing_from_registered)}. "
            f"Either register gear data type it or remove it from 'any_gear' fixture"
        )


# ================================================================================
# Protocol conformance
# -> Every concrete gear data class must satisfy the GearData protocol
# ================================================================================


def test_any_gear_satisfies_gear_data_protocol(any_gear) -> None:
    assert isinstance(any_gear, GearData)


# ================================================================================
# Frozen-ness
# -> Every concrete gear data record is immutable
# ================================================================================


def test_any_gear_data_is_frozen(any_gear):
    with pytest.raises(FrozenInstanceError):
        any_gear.m_n = 999.0


# ================================================================================
# SpurGearData
# ================================================================================
class TestSpurGearData:
    def test_returns_correct_type(self, spur):
        assert isinstance(spur, SpurGearData)

    def test_pitch_diameter(self, spur):
        # d_p = m_t * z; for spur m_t = m_n
        assert spur.dp == pytest.approx(1.0 * 20)

    def test_base_diameter(self, spur):
        # d_b = d_p * cos(alpha_t); for spur alpha_t = alaph_n = 20
        expected = 20.0 * np.cos(np.radians(20.0))
        assert spur.db == pytest.approx(expected)

    def test_addendum_diameter(self, spur):
        # d_a = d_p + 2 * h_a; h_a = (h_a* + x) * m_n = (1 + 0) * 1 = 1
        assert spur.da == pytest.approx(22.0)

    def test_dedendum_diameter(self, spur):
        # d_f = d_p - 2 * h_f; h_f = (h_a* + c* - x) * m_n = (1 + 0.25 - 0) * 1 = 1.25
        assert spur.df == pytest.approx(17.5)

    def test_transverse_equals_normal(self, spur):
        assert spur.m_t == spur.m_n
        assert spur.alpha_t == spur.alpha_n
        assert spur.alpha_t_r == spur.alpha_n_r

    def test_default_alpha_n_is_20(self):
        g = make_spur_gear_data(m_n=1.0, z=20, b=10.0)
        assert g.alpha_n == 20.0

    def test_pitch_is_pi_times_module(self, spur):
        assert spur.p == pytest.approx(np.pi * spur.m_t)


# ================================================================================
# HelicalGearData
# ================================================================================


class TestHelicalGearData:
    def test_returns_correct_type(self, helical):
        assert isinstance(helical, HelicalGearData)

    def test_alpha_t_helical_conversion(self, helical):
        # tan(alpha_t) = tan(alpha_n) / cos(beta)
        expected = np.degrees(
            np.atan(np.tan(np.radians(20.0)) / np.cos(np.radians(20.0)))
        )
        assert helical.alpha_t == pytest.approx(expected)

    def test_m_t_helical_conversion(self, helical):
        # m_t = m_n / cos(beta)
        expected = 1.0 / np.cos(np.radians(20.0))
        assert helical.m_t == pytest.approx(expected)

    def test_beta_b_helical_conversion(self, helical):
        # tan(beta_b) = tan(beta) * cos(alpha_t)
        expected = np.degrees(
            np.atan(np.tan(np.radians(20.0)) * np.cos(np.radians(helical.alpha_t)))
        )
        assert helical.beta_b == pytest.approx(expected)

    def test_transverse_module_larger_than_normal(self, helical):
        assert helical.m_t > helical.m_n

    def test_transverse_pressure_angle_larger_than_normal(self, helical):
        assert helical.alpha_t > helical.alpha_n

    def test_base_helix_angle_smaller_than_pitch_helix_angle(self, helical):
        assert helical.beta_b < helical.beta

    def test_pitch_diameter_uses_transverse_module(self, helical):
        assert helical.dp == pytest.approx(helical.m_t * helical.z)

    def test_spur_limit(self):
        """beta -> 0 should reproduce spur geometry."""
        g_h = make_helical_gear_data(m_n=1.0, z=20, b=10.0, beta=1e-12)
        g_s = make_spur_gear_data(m_n=1.0, z=20, b=10.0)
        assert g_h.m_t == pytest.approx(g_s.m_t)
        assert g_h.alpha_t == pytest.approx(g_s.alpha_t)
        assert g_h.dp == pytest.approx(g_s.dp)
        assert g_h.db == pytest.approx(g_s.db)
        assert g_h.da == pytest.approx(g_s.da)
        assert g_h.df == pytest.approx(g_s.df)


# ================================================================================
# InternalSpurGearData
# ================================================================================


class TestInternalSpurGearData:
    def test_returns_correct_type(self, internal_spur):
        assert isinstance(internal_spur, InternalSpurGearData)

    def test_inverted_diameter_ordering(self, internal_spur):
        """Internal: d_a < d_p < d_f."""
        assert internal_spur.da < internal_spur.dp < internal_spur.df

    def test_addendum_diameter_subtracts(self, internal_spur):
        # d_a = d_p - 2 * h_a; for z=80, m_n=1, x=0: d_p=80, h_a=1
        assert internal_spur.da == pytest.approx(78.0)

    def test_dedendum_diameter_adds(self, internal_spur):
        # d_f = d_p + 2 * h_f; h_f = 1.25
        assert internal_spur.df == pytest.approx(82.5)

    def test_pitch_and_base_match_external_at_same_inputs(self, internal_spur):
        """Pitch and base diameters depend only on m_t/alpha_t/z, not on internal-ness."""
        external = make_spur_gear_data(m_n=1.0, z=80, b=10.0)
        assert internal_spur.dp == pytest.approx(external.dp)
        assert internal_spur.db == pytest.approx(external.db)


# ================================================================================
# InternalHelicalGearData
# ================================================================================


class TestInternalHelicalGearData:
    def test_returns_correct_type(self, internal_helical):
        assert isinstance(internal_helical, InternalHelicalGearData)

    def test_inverted_diameter_ordering(self, internal_helical):
        assert internal_helical.da < internal_helical.dp < internal_helical.df

    def test_helical_conversions_match_external_helical(self, internal_helical):
        """The α_t, m_t, β_b formulas don't depend on internal-ness."""
        external = make_helical_gear_data(m_n=1.0, z=80, b=10.0, beta=20.0)
        assert internal_helical.m_t == pytest.approx(external.m_t)
        assert internal_helical.alpha_t == pytest.approx(external.alpha_t)
        assert internal_helical.beta_b == pytest.approx(external.beta_b)


# ================================================================================
# Unimplemented gear-type stubs
# ================================================================================


class TestUnimplementedStubs:
    @pytest.mark.parametrize(
        "factory, kwargs",
        [
            (make_bevel_gear_data, dict(m_n=1.0, z=20, b=10.0, delta=45.0)),
            (make_worm_gear_data, dict(m_n=1.0, z=1, b=10.0)),
            (make_crossed_helical_gear_data, dict(m_n=1.0, z=20, b=10.0, beta=20.0)),
            (make_hypoid_gear_data, dict(m_n=1.0, z=20, b=10.0, delta=45.0)),
        ],
        ids=["bevel", "worm", "crossed_helical", "hypoid"],
    )
    def test_stub_factory_raises_not_implemented(self, factory, kwargs):
        with pytest.raises(NotImplementedError):
            factory(**kwargs)

    @pytest.mark.parametrize(
        "stub_class",
        [BevelGearData, WormGearData, CrossedHelicalGearData, HypoidGearData],
        ids=["bevel", "worm", "crossed_helical", "hypoid"],
    )
    def test_stub_dataclass_is_importable(self, stub_class):
        # Class exists and can at least be referenced
        assert stub_class.__name__.endswith("GearData")


# ================================================================================
# Dispatch helpers
# ================================================================================


class TestDispatchHelpers:
    @pytest.mark.parametrize(
        "fixture_name, expected",
        [
            ("spur", False),
            ("helical", True),
            ("internal_spur", False),
            ("internal_helical", True),
        ],
        ids=["spur", "helical", "internal_spur", "internal_helical"],
    )
    def test_is_helical(self, request, fixture_name, expected) -> None:
        gear: GearDataConcrete = request.getfixturevalue(fixture_name)
        assert is_helical(gear) is expected

    @pytest.mark.parametrize(
        "fixture_name, expected",
        [
            ("spur", False),
            ("helical", False),
            ("internal_spur", True),
            ("internal_helical", True),
        ],
        ids=["spur", "helical", "internal_spur", "internal_helical"],
    )
    def test_is_internal(self, request, fixture_name, expected) -> None:
        gear: GearDataConcrete = request.getfixturevalue(fixture_name)
        assert is_internal(gear) is expected

    def test_is_internal_and_is_helical_are_independent(
        self, spur, helical, internal_spur, internal_helical
    ):
        """The two flags vary independently across the four gear types."""
        # fmt: off
        truth_table: dict[tuple[bool, bool], str] = {
            (is_internal(spur),             is_helical(spur)):              "spur",
            (is_internal(helical),          is_helical(helical)):           "helical",
            (is_internal(internal_spur),    is_helical(internal_spur)):     "internal_spur",
            (is_internal(internal_helical), is_helical(internal_helical)):  "internal_helical",
        }
        # fmt: on
        # All four (internal, helical) combinations must occur exactly once
        assert set(truth_table.keys()) == {
            (False, False),
            (False, True),
            (True, False),
            (True, True),
        }


# ================================================================================
# Constructed gear classes (Gear, ParametricGear, HobbedGear)
# ================================================================================


class TestGearClasses:
    def test_parametric_gear_satisfies_gear_protocol(self, spur):
        pg: ParametricGear = ParametricGear(data=spur, workplane=cq.Workplane())
        assert isinstance(pg, Gear)

    def test_hobbed_gear_satisfies_gear_protocol(self, spur):
        pg: HobbedGear = HobbedGear(
            data=spur, workplane=cq.Workplane(), cutter=cq.Workplane()
        )
        assert isinstance(pg, Gear)

    # INFO : Not sure if it makes sense to have this frozen (though the data should be frozen)
    def test_parmetric_gear_is_fozen(self, spur):
        pg: ParametricGear = ParametricGear(data=spur, workplane=cq.Workplane())
        with pytest.raises(FrozenInstanceError):
            pg.workplane = cq.Workplane()  # type: ignore

    def test_hobbed_gear_is_fozen(self, spur):
        pg: HobbedGear = HobbedGear(
            data=spur, workplane=cq.Workplane(), cutter=cq.Workplane()
        )
        with pytest.raises(FrozenInstanceError):
            pg.workplane = cq.Workplane()  # type: ignore
