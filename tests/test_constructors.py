
from pytest import fixture
from ipaddress import IPv4Address
from microfunkhaus import API, actions
from hypothesis import given, strategies as st, HealthCheck, settings
from chrdiotypes.musical import ProgressionFields, ProgressionRequest, CheetSheet, ProgressionFields, PseudoMIDI, NodeFields
from chrdiotypes.transport import PathTransport, SessionTransport, UserTransport, LabelTransport, GenericUser
from chrdiotypes.data_enums import ChordSymbolStructures, NotesInt, NodeIDs
from .raw import raw_performance, raw_cheetsheet


@fixture
def cheetsheet():
    return CheetSheet.parse_raw(raw_cheetsheet)

@fixture
def pseudomidi():
    return PseudoMIDI(voices=[[1, 1], [0, 0]], ticket="")

@fixture
def perf_response():
    return API.PerformanceResponse.parse_raw(raw_performance)

@given(st.builds(ProgressionFields))
def test_construct_path_data(seed_instance):
    assert API.construct_path_data(seed_instance)

@settings(suppress_health_check=[HealthCheck(9)])
@given(progression=st.builds(ProgressionFields))
def test_construct_voicing_data(progression, cheetsheet, pseudomidi):
    assert API.construct_voicing_data(progression, cheetsheet, pseudomidi)

@given(r=st.builds(API.GenericRequest, user_object=st.builds(API.User), sess_id=st.ip_addresses(v=4)))
def test_construct_user_data(r):
    assert API.construct_user_data(r)

@given(st.builds(API.LabelingRequest))
def test_construct_label_data(seed_instance):
    assert API.construct_label_data(seed_instance)

def test_construct_progression_request(perf_response):
    assert API.construct_progression_request(perf_response)

@settings(suppress_health_check=[HealthCheck(9)])
@given(
    progression=st.one_of(
        st.builds(API.Performance),
        st.builds(
            API.PerformanceResponse,
            structures=st.lists(
                st.sampled_from(tuple(ChordSymbolStructures)),
                min_size=4,
                max_size=4,
                ),
            changeabilities=st.lists(
                st.booleans(),
                min_size=4,
                max_size=4,
            ),
            nodes=st.lists(
                st.builds(
                    NodeFields,
                    node_id=st.sampled_from(tuple(NodeIDs)),
                    ),
                min_size=4,
                max_size=4,
            )
        )
        )
    )
def test_construct_cheet_sheet(progression, perf_response):
    assert API.construct_cheet_sheet(perf_response, progression=progression)