"""Private document routing does not expose an object key before authorization."""

from starlette.requests import Request

from takdora.takdora import private_document_response


def test_unauthenticated_document_request_is_a_bounded_not_found() -> None:
    request = Request({"type": "http", "headers": [], "path_params": {"invoice_id": "1"}})
    response = private_document_response(request)
    assert response.status_code == 404
    assert b"storage" not in response.body
