from pytest import fixture
from pydantic import EmailStr
from ipaddress import IPv4Address
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
    VoiceOrderings,
    GraphNames,
)
from microfunkhaus import API

LENGTH = 3

b_note = st.sampled_from(tuple(NotesInt))
b_voice = st.lists(st.integers(), min_size=LENGTH, max_size=LENGTH)
b_special_cases_or_alternatives = st.lists(
    st.booleans(), min_size=LENGTH, max_size=LENGTH
)
b_structures_int = st.lists(
    st.sampled_from(tuple(ChordIntervalStructures)),
    min_size=LENGTH,
    max_size=LENGTH,
)
b_structures_sym = st.lists(
    st.sampled_from(tuple(ChordSymbolStructures)),
    min_size=LENGTH,
    max_size=LENGTH,
)
b_cheetsheet = st.builds(
    CheetSheet,
    info=st.lists(
        st.tuples(
            st.sampled_from(tuple(NodeIDs)),
            st.sampled_from(tuple(ChordSymbolStructures)),
        ),
        min_size=LENGTH,
        max_size=LENGTH,
    ),
    structures=b_structures_int,
    special_cases=b_special_cases_or_alternatives,
    bases=st.lists(b_note, min_size=LENGTH, max_size=LENGTH),
    key=b_note,
    ordering=st.one_of(st.sampled_from(tuple(VoiceOrderings)), st.none()),
)
b_pseudomidi = st.builds(
    PseudoMIDI,
    voices=st.lists(
        b_voice,
        min_size=4,  # stacked voices ar chords of 4 notes
        max_size=4,
    ),
    ticket=st.text("0123456789-", min_size=7, max_size=40),
)
b_user_obj = st.builds(API.User, email=st.from_type(EmailStr))
b_user_obj_opt = st.one_of(b_user_obj, st.none())
b_labeling_request = st.builds(
    API.LabelingRequest,
    user_object=b_user_obj_opt,
    sess_id=st.ip_addresses(v=4),
    flag=st.sampled_from(tuple(PerformanceFlags)),
)
b_generic_request = st.builds(
    API.GenericRequest, user_object=b_user_obj_opt, sess_id=st.ip_addresses(v=4)
)
b_node_fields = st.builds(
    NodeFields,
    mode=st.booleans(),
    tonality=st.booleans(),
    node_id=st.sampled_from(tuple(NodeIDs)),
    gravity=st.sampled_from(tuple(ChordGravities)),
    base=b_note,
)
b_progression_fields = st.builds(
    ProgressionFields,
    structures=b_structures_int,
    changeabilities=b_special_cases_or_alternatives,
    nodes=st.lists(
        b_node_fields,
        min_size=LENGTH,
        max_size=LENGTH,
    ),
)

b_perf_response = st.builds(
    API.PerformanceResponse,
    key=b_note,
    graph=st.sampled_from(tuple(GraphNames)),
    ticket=st.text("0123456789-", min_size=7, max_size=40),
    hex_blob=st.text(min_size=20, max_size=60),
    structures=b_structures_sym,
    changeabilities=b_special_cases_or_alternatives,
    human_readable=st.lists(st.none(), min_size=0, max_size=0),
    nodes=st.lists(
        b_node_fields,
        min_size=LENGTH,
        max_size=LENGTH,
    ),
)
b_performance = st.builds(
    API.Performance, user_object=b_user_obj_opt, sess_id=st.ip_addresses(v=4)
)
b_perf_request = st.builds(
    API.PerformanceRequest,
    user=b_user_obj_opt,
    performance_object=st.one_of(b_perf_response, b_performance),
)
b_amend_request = st.builds(
    API.AmendmentRequest, user=b_user_obj_opt, performance_object=b_perf_response
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
