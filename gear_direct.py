import cadquery as cq

from .core import GearData


def _involute_sketch() -> cq.Sketch:
    pass

def _undercut(geardata: GearData) -> cq.Sketch:
    pass


def _circles(geardata: GearData) -> cq.Sketch:
    result: cq.Sketch = (
        cq.Sketch()
        .circle(geardata.d / 2.0)
        .circle(geardata.db / 2.0)
        .circle(geardata.da / 2.0)
        .circle(geardata.df / 2.0)
    )
    return result
