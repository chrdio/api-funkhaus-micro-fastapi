from enum import Enum, IntEnum

class PerformanceFlags(Enum):
    served = 'served'
    amended = 'amended'
    saved = 'saved'
    downloaded = 'downloaded'


class ChordSymbolStructures(Enum):
    M3M7M9 = "M3M7M9"
    M3Q5M0 = "M3Q5M0"
    M3Q5M7 = "M3Q5M7"
    M3Q5M9 = "M3Q5M9"
    M3Q5O8 = "M3Q5O8"
    M3Q5m7 = "M3Q5m7"
    M3m7M9 = "M3m7M9"
    m3Q5M9 = "m3Q5M9"
    m3Q5O8 = "m3Q5O8"
    m3Q5m7 = "m3Q5m7"
    m3m7M9 = "m3m7M9"


class ChordIntervalStructures(Enum):
    M3M7M9 = [0, 4, 11, 14]
    M3Q5M0 = [0, 4, 7, 16]
    M3Q5M7 = [0, 7, 4, 11]
    M3Q5M9 = [0, 7, 4, 14]
    M3Q5O8 = [0, 12, 7, 4]
    M3Q5m7 = [0, 7, 4, 10]
    M3m7M9 = [0, 4, 10, 14]
    m3Q5M9 = [0, 7, 3, 14]
    m3Q5O8 = [0, 12, 7, 3]
    m3Q5m7 = [0, 7, 3, 10]
    m3m7M9 = [0, 3, 10, 14]


class GraphNames(Enum):
    major_graph = "major_graph"
    minor_graph = "minor_graph"
    default_graph = "default_graph"
    master_graph = "master_graph"
    mixed = "mixed"


class NotesInt(IntEnum):
    C = 0
    C_SHARP = 1
    D = 2
    D_SHARP = 3
    E = 4
    F = 5
    F_SHARP = 6
    G = 7
    G_SHARP = 8
    A = 9
    A_SHARP = 10
    B = 11


class NodeIDs(Enum):
    NORM1_MAJ = "NORM1+"
    NORM1_MIN = "NORM1-"
    FLAT2_MAJ = "FLAT2+"
    SHRP2_MIN = "SHRP2-"
    FLAT3_MAJ = "FLAT3+"
    SHRP3_MIN = "SHRP3-"
    NORM4_MAJ = "NORM4+"
    NORM4_MIN = "NORM4-"
    NORM5_MAJ = "NORM5+"
    NORM5_MIN = "NORM5-"
    FLAT6_MAJ = "FLAT6+"
    SHRP6_MIN = "SHRP6-"
    FLAT7_MAJ = "FLAT7+"
    SHRP7_MIN = "SHRP7-"