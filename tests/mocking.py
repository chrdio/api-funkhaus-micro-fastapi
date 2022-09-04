from pytest import fixture
from pydantic import EmailStr
from hypothesis import strategies as st
from chrdiotypes.musical import (
  ProgressionFields,
  NodeFields,
  CheetSheet,
  PseudoMIDI,
)
from chrdiotypes.data_enums import (
  ChordSymbolStructures,
  ChordIntervalStructures,
  NotesInt,
  NodeIDs,
  ChordGravities,
  PerformanceFlags,
)
from microfunkhaus import API

b_user_obj = st.builds(
  API.User,
  email=st.from_type(EmailStr)
  )
b_labeling_request = st.builds(
  API.LabelingRequest,
  user_object=b_user_obj,
  sess_id=st.ip_addresses(v=4),
  flag=st.from_type(PerformanceFlags)
  )
b_generic_request = st.builds(
  API.GenericRequest,
  user_object=b_user_obj,
  sess_id=st.ip_addresses(v=4)
  )
b_node_fields = st.builds(
  NodeFields,
  node_id=st.sampled_from(NodeIDs),
  gravity=st.from_type(ChordGravities)
)
b_progression_fields = st.builds(
            ProgressionFields,
            structures=st.lists(
                st.from_type(ChordIntervalStructures),
                min_size=3,
                max_size=3,
                ),
            changeabilities=st.lists(
                st.booleans(),
                min_size=3,
                max_size=3,
            ),
            nodes=st.lists(
                b_node_fields,
                min_size=3,
                max_size=3,
            )
        )

raw_performance = """{
  "key": 10,
  "graph": "major_graph",
  "ticket": "8120674621874145142",
  "hex_blob": "4d546864000000060000000100404d54726b0000008b00ff0307636872642e696f00902e4c003540003940004a4c8200e0004000802e40003540003940004a400090264c003940003e40004d4c8200e0004000802640003940003e40004d400090274c003a40003f40004f4c8200e0004000802740003a40003f40004f4000902b4c003740003a40004a4c8200e0004000802b40003740003a40004a4000ff2f00",
  "structures": [
    "M3Q5M7",
    "m3Q5O8",
    "M3Q5O8"
  ],
  "changeabilities": [
    true,
    true,
    true
  ],
  "human_readable": [
    [
      "A#",
      "maj",
      7
    ],
    [
      "D",
      "min",
      null
    ],
    [
      "D#",
      "maj",
      null
    ]
  ],
  "nodes": [
    {
      "node_id": "NORM1+",
      "mode": true,
      "tonality": true,
      "gravity": 0,
      "base": 0
    },
    {
      "node_id": "SHRP3-",
      "mode": true,
      "tonality": false,
      "gravity": 1,
      "base": 4
    },
    {
      "node_id": "NORM4+",
      "mode": true,
      "tonality": true,
      "gravity": -2,
      "base": 5
    }
  ]
}"""
raw_cheetsheet = """{"info": [["NORM1+", "M3Q5O8"], ["NORM4+", "M3Q5O8"], ["SHRP6-", "m3Q5O8"]], "structures": [[0, 12, 7, 4], [0, 12, 7, 4], [0, 12, 7, 3]], "special_cases": [false, false, false], "bases": [0, 5, 9], "key": 5}"""

@fixture
def f_cheetsheet():
    """Has a length of 3"""
    return CheetSheet.parse_raw(raw_cheetsheet)

@fixture
def f_pseudomidi():
    """Has a length of 3"""
    return PseudoMIDI(voices=[[1, 1, 1], [0, 0, 0], [1, 1, 1], [0, 0, 0]], ticket="")

@fixture
def f_perf_response():
    """Has a length of 3"""
    return API.PerformanceResponse.parse_raw(raw_performance)