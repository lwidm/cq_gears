import pytest
import cadquery as cq


from cq_gears import (
    make_spur_gear_data,
    make_helical_gear_data,
    GearData,
    SpurGearData,
    HelicalGearData,
)

from cq_gears.rack_cutter import (
    _cutters_are_compatible,
    create_rack_cutter,
    create_rack_cutter_for_group,
    find_compatible_cutter_groups,
)

# ================================================================================
# Cutter compatibility
# ================================================================================


class TestCuttersAreCompatible:
    def test_identical_spurs_are_compatible(self) -> None:
        a: SpurGearData = make_spur_gear_data(m_n=1.0, z=20, b=10.0)
        b: SpurGearData = make_spur_gear_data(m_n=1.0, z=20, b=10.0)
        assert _cutters_are_compatible(a, b)

    def test_different_z_still_compatible(self) -> None:
        """Tooth count is NOT a cutter-shaping parameter (rack length adjusts)."""
        a: SpurGearData = make_spur_gear_data(m_n=1.0, z=20, b=10.0)
        b: SpurGearData = make_spur_gear_data(m_n=1.0, z=40, b=10.0)
        assert _cutters_are_compatible(a, b)

    def test_different_b_still_compatible(self) -> None:
        """Face width is NOT a cutter-shaping parameter (rack width adjusts)."""
        a: SpurGearData = make_spur_gear_data(m_n=1.0, z=20, b=10.0)
        b: SpurGearData = make_spur_gear_data(m_n=1.0, z=20, b=20.0)
        assert _cutters_are_compatible(a, b)

    def test_different_m_n_incompatible(self) -> None:
        a: SpurGearData = make_spur_gear_data(m_n=1.0, z=20, b=10.0)
        b: SpurGearData = make_spur_gear_data(m_n=2.0, z=20, b=10.0)
        assert not _cutters_are_compatible(a, b)

    def test_different_alpha_n_incompatible(self) -> None:
        a: SpurGearData = make_spur_gear_data(m_n=1.0, z=20, b=10.0, alpha_n=20.0)
        b: SpurGearData = make_spur_gear_data(m_n=1.0, z=20, b=10.0, alpha_n=14.5)
        assert not _cutters_are_compatible(a, b)

    def test_different_x_incompatible(self) -> None:
        a: SpurGearData = make_spur_gear_data(m_n=1.0, z=20, b=10.0, x=0.0)
        b: SpurGearData = make_spur_gear_data(m_n=1.0, z=20, b=10.0, x=0.5)
        assert not _cutters_are_compatible(a, b)

    def test_different_ha_star_incompatible(self) -> None:
        a: SpurGearData = make_spur_gear_data(m_n=1.0, z=20, b=10.0, ha_star=1.0)
        b: SpurGearData = make_spur_gear_data(m_n=1.0, z=20, b=10.0, ha_star=1.25)
        assert not _cutters_are_compatible(a, b)

    def test_spur_and_helical_incompatible(self, spur, helical):
        """Different gear kinds always have different cutters."""
        assert not _cutters_are_compatible(spur, helical)

    def test_helicals_same_beta_compatible(self) -> None:
        a: HelicalGearData = make_helical_gear_data(m_n=1.0, z=20, b=10.0, beta=20.0)
        b: HelicalGearData = make_helical_gear_data(m_n=1.0, z=20, b=10.0, beta=20.0)
        assert _cutters_are_compatible(a, b)

    def test_helicals_opposite_sign_beta_compatible(self) -> None:
        """Sign of beta is just left/right handedness: Same |beta| -> same rack."""
        a: HelicalGearData = make_helical_gear_data(m_n=1.0, z=20, b=10.0, beta=20.0)
        b: HelicalGearData = make_helical_gear_data(m_n=1.0, z=20, b=10.0, beta=-20.0)
        assert _cutters_are_compatible(a, b)

    def test_helicals_different_beta_magnitude_incompatible(self) -> None:
        a: HelicalGearData = make_helical_gear_data(m_n=1.0, z=20, b=10.0, beta=20.0)
        b: HelicalGearData = make_helical_gear_data(m_n=1.0, z=20, b=10.0, beta=15.0)
        assert not _cutters_are_compatible(a, b)


# ================================================================================
# Compatibility Group
# ================================================================================


class TestFindCompatibleCutterGroups:
    def test_empty_list(self) -> None:
        assert find_compatible_cutter_groups([]) == []

    def test_single_gear(self, spur) -> None:
        assert find_compatible_cutter_groups([spur]) == [{0}]

    def test_two_compatible_gears_one_group(self) -> None:
        a: SpurGearData = make_spur_gear_data(m_n=1.0, z=20, b=10.0)
        b: SpurGearData = make_spur_gear_data(m_n=1.0, z=40, b=15.0)
        assert find_compatible_cutter_groups([a, b]) == [{0, 1}]

    def test_two_incompatible_gears_one_group(self) -> None:
        a: SpurGearData = make_spur_gear_data(m_n=1.0, z=20, b=10.0)
        b: SpurGearData = make_spur_gear_data(m_n=2.0, z=20, b=10.0)
        assert find_compatible_cutter_groups([a, b]) == [{0}, {1}]

    def test_mixed_three_gears(self) -> None:
        a: SpurGearData = make_spur_gear_data(m_n=1.0, z=20, b=10.0)
        b: SpurGearData = make_spur_gear_data(m_n=2.0, z=20, b=10.0)
        c: SpurGearData = make_spur_gear_data(m_n=1.0, z=40, b=15.0)
        groups: list[set] = find_compatible_cutter_groups([a, b, c])
        assert len(groups) == 2
        assert {0, 2} in groups
        assert {1} in groups

    def test_groups_partition_indices(self, spur, helical) -> None:
        """Every index should appear in exactly one group"""
        gears: list[GearData] = [
            spur,
            helical,
            make_spur_gear_data(m_n=2.0, z=20, b=10.0),
        ]
        groups: list[set] = find_compatible_cutter_groups(gears)
        all_indices: set[int] = set()
        for group in groups:
            assert not (group & all_indices)
            all_indices |= group
        assert all_indices == set(range(len(gears)))


# ================================================================================
# Cutter creation
# ================================================================================


class TestCreateRackCutter:
    def test_spur_produces_workplane(self, spur) -> None:
        cutter: cq.Workplane = create_rack_cutter(spur)
        assert isinstance(cutter, cq.Workplane)
        assert cutter.val() is not None

    def test_helical_produces_workplane(self, helical) -> None:
        cutter: cq.Workplane = create_rack_cutter(helical)
        assert isinstance(cutter, cq.Workplane)
        assert cutter.val() is not None

    def test_internal_spur_raises_not_implemented(self, internal_spur) -> None:
        with pytest.raises(NotImplementedError):
            create_rack_cutter(internal_spur)

    def test_internal_helical_raises_not_implemented(self, internal_helical) -> None:
        with pytest.raises(NotImplementedError):
            create_rack_cutter(internal_helical)

    def test_b_override_changes_volume(self, spur) -> None:
        small: cq.Workplane = create_rack_cutter(spur, b=spur.b)
        big: cq.Workplane = create_rack_cutter(spur, b=spur.b * 2)
        assert small.val().Volume() < big.val().Volume()  # type: ignore


class TestCreateRackCutterForGroup:
    def test_single_gear_group(self, spur) -> None:
        cutter: cq.Workplane = create_rack_cutter_for_group([spur], {0})
        assert isinstance(cutter, cq.Workplane)
        assert cutter.val() is not None

    def test_group_uses_max_z_and_max_b(self) -> None:
        small: SpurGearData = make_spur_gear_data(m_n=1.0, z=20, b=10.0)
        big: SpurGearData = make_spur_gear_data(m_n=1.0, z=40, b=20.0)
        groups: list[set] = find_compatible_cutter_groups([small, big])
        assert len(groups) == 1
        group_cutter: cq.Workplane = create_rack_cutter_for_group(
            [small, big], groups[0]
        )
        big_alone_cutter: cq.Workplane = create_rack_cutter(big)
        assert group_cutter.val().Volume() == pytest.approx(  # type: ignore
            big_alone_cutter.val().Volume(), rel=1e-3  # type: ignore
        )
