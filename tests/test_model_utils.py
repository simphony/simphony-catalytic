def test_read_case():
    from osp.models.catalytic.utils import _read_patches

    expected = [
        "wedge1",
        "wedge2",
        "wedge3",
        "wedge4",
        "reactingWall",
        "inlet",
        "outlet",
        "inertWall",
    ]

    assert sorted(expected) == sorted(_read_patches())
