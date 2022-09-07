from hypothesis import given, strategies as st
from microfunkhaus import generate_app_with_config, API
from fastapi.testclient import TestClient
from .mocking import b_perf_request, b_generic_request, b_labeling_request, LENGTH

APP = generate_app_with_config()
TEST_APP = TestClient(APP)
headers = {"X-Token": "testing"}
invalid_headers = {"X-Token": "invalid"}


def test_healthcheck():
    assert TEST_APP.get("/healthcheck", headers=headers).ok


def test_wrong_header():
    assert not TEST_APP.get("/healthcheck", headers=invalid_headers).ok


@given(b_perf_request)
def test_generation(r):
    payload = r.json()
    response = TEST_APP.post("/generate", payload, headers=headers)
    assert response.ok


@given(b_labeling_request)
def test_labeling(r):
    payload = r.json()
    response = TEST_APP.post("/label", payload, headers=headers)
    assert response.ok


@given(b_generic_request, st.integers(min_value=0, max_value=LENGTH - 1))
def test_amend_idiomatic_performance(r, ind):
    payload = r.json()
    generated_response = TEST_APP.post("/generate", payload, headers=headers)
    performance_response = API.PerformanceResponse.parse_raw(generated_response.text)
    amendment_req = API.AmendmentRequest(
        sess_id=r.sess_id,
        user_object=r.user_object,
        performance_object=performance_response,
    )
    am_payload = amendment_req.json()
    response = TEST_APP.post(f"/amend/{ind}", am_payload, headers=headers)
    assert response.ok
