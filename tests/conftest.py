"""Fixtures shared accross all test files in tests/."""

import pytest

from cq_gears import (
    GearData,
    SpurGearData,
    HelicalGearData,
    RackGearData,
    InternalSpurGearData,
    InternalHelicalGearData,
    # BevelGearData,
    # WormGearData,
    # CrossedHelicalGearData,
    # HypoidGearData,
    make_spur_gear_data,
    make_helical_gear_data,
    make_rack_gear_data,
    make_internal_spur_gear_data,
    make_internal_helical_gear_data,
    # make_bevel_gear_data,
    # make_worm_gear_data,
    # make_crossed_helical_gear_data,
    # make_hypoid_gear_data,
)

# ================================================================================
# Reference gear instances
# -> Small, fixed inputs
# -> Use these as canonical "A typical X gear" in tests.
# ================================================================================


@pytest.fixture
def spur() -> SpurGearData:
    return make_spur_gear_data(m_n=1.0, z=20, b=10.0)


@pytest.fixture
def helical() -> HelicalGearData:
    return make_helical_gear_data(m_n=1.0, z=20, b=10.0, beta=20.0)

@pytest.fixture
def rack() -> RackGearData:
    return make_rack_gear_data(m_n=1.0, z=20, b=10.0, rail_width=0.2)


@pytest.fixture
def internal_spur() -> InternalSpurGearData:
    return make_internal_spur_gear_data(m_n=1.0, z=80, b=10.0)


@pytest.fixture
def internal_helical() -> InternalHelicalGearData:
    return make_internal_helical_gear_data(m_n=1.0, z=80, b=10.0, beta=20.0)


@pytest.fixture(
    params=["spur", "helical", "rack", "internal_spur", "internal_helical"],
    ids=["spur", "helical", "rack", "internal_spur", "internal_helical"],
)
def any_gear(request) -> GearData:
    """
    Parameterised fixtures that yields each concrete gear type in turn.

    Use this for tests that should pass for every gear (e.g. Protocol
    conformance, frozen-ness). The test body runs once  per gear type.
    """
    return request.getfixturevalue(request.param)
