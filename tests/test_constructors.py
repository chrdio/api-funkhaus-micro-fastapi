
from ipaddress import IPv4Address
from microfunkhaus import API, actions
from hypothesis import given, strategies as st, HealthCheck, settings
from chrdiotypes.musical import ProgressionFields, ProgressionRequest, CheetSheet, ProgressionFields, PseudoMIDI, NodeFields
from chrdiotypes.transport import PathTransport, SessionTransport, UserTransport, LabelTransport, GenericUser
from chrdiotypes.data_enums import ChordSymbolStructures, ChordIntervalStructures, NotesInt, NodeIDs
from .mocking import (
    f_perf_response,
    f_pseudomidi,
    f_cheetsheet,
    b_progression_fields,
    b_generic_request,
    b_labeling_request
)

from devtools import debug



@given(b_progression_fields)
def test_construct_path_data(seed_instance):
    assert API.construct_path_data(seed_instance)

@settings(suppress_health_check=[HealthCheck(9)])
@given(progression=b_progression_fields)
def test_construct_voicing_data(progression, f_cheetsheet, f_pseudomidi):
    assert API.construct_voicing_data(progression, f_cheetsheet, f_pseudomidi)

@given(b_generic_request)
def test_construct_user_data(r):
    assert API.construct_user_data(r)

@given(b_generic_request)
def test_construct_session_data(r):
    assert API.construct_session_data(r)

@given(b_labeling_request)
def test_construct_label_data(seed_instance):
    assert API.construct_label_data(seed_instance)

def test_construct_progression_request(f_perf_response):
    assert API.construct_progression_request(f_perf_response)

@settings(suppress_health_check=[HealthCheck(9)])
@given(progression=b_progression_fields)
def test_construct_cheet_sheet(progression, f_perf_response):
    assert API.construct_cheet_sheet(f_perf_response, progression=progression)


def test_construct_performance_through(f_perf_response):
    assert API.construct_progression(f_perf_response)

@settings(suppress_health_check=[HealthCheck(9)])
@given(
    hex_blob=st.text(min_size=1),
    progression=b_progression_fields
    )
def test_construct_performance(progression, f_cheetsheet, f_pseudomidi, hex_blob):
    debug(progression)
    assert API.construct_performance(progression=progression, cheet_sheet=f_cheetsheet, pseudo_midi=f_pseudomidi, hex_blob=hex_blob)