
import devtools
from ipaddress import IPv4Address
from microfunkhaus import API, actions
from hypothesis import given, strategies as st, HealthCheck, settings
from chrdiotypes.musical import ProgressionFields, ProgressionRequest, CheetSheet, ProgressionFields, PseudoMIDI, NodeFields
from chrdiotypes.transport import PathTransport, SessionTransport, UserTransport, LabelTransport, GenericUser
from chrdiotypes.data_enums import ChordSymbolStructures, ChordIntervalStructures, NotesInt, NodeIDs
from .mocking import (
    b_pseudomidi,
    b_cheetsheet,
    b_progression_fields,
    b_generic_request,
    b_labeling_request,
    b_perf_response
)




@given(b_progression_fields)
def test_construct_path_data(progression):
    assert API.construct_path_data(progression)

@given(progression=b_progression_fields, cheetsheet=b_cheetsheet, pseudomidi=b_pseudomidi)
def test_construct_voicing_data(progression, cheetsheet, pseudomidi):
    assert API.construct_voicing_data(progression, cheetsheet, pseudomidi)

@given(b_generic_request)
def test_construct_user_data(r):
    assert API.construct_user_data(r)

@given(b_generic_request)
def test_construct_session_data(r):
    assert API.construct_session_data(r)

@given(b_labeling_request)
def test_construct_label_data(r):
    assert API.construct_label_data(r)

@given(b_perf_response)
def test_construct_progression_request(pr):
    assert API.construct_progression_request(pr)

@given(progression=b_progression_fields, pr=b_perf_response)
def test_construct_cheet_sheet(progression, pr):
    assert API.construct_cheet_sheet(pr, progression=progression)


@given(b_perf_response)
def test_construct_performance_through(pr):
    assert API.construct_progression(pr)

@given(
    hex_blob=st.text(min_size=1),
    progression=b_progression_fields,
    chsh=b_cheetsheet,
    psdm=b_pseudomidi
    )
def test_construct_performance(progression, chsh, psdm, hex_blob):
    assert API.construct_performance(progression=progression, cheet_sheet=chsh, pseudo_midi=psdm, hex_blob=hex_blob)