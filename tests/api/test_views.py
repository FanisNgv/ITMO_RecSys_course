from http import HTTPStatus

from starlette.testclient import TestClient

from service.settings import ServiceConfig

GET_RECO_PATH = "/reco/{model_name}/{user_id}"


def test_health(
    client: TestClient,
) -> None:
    with client:
        response = client.get("/health")
    assert response.status_code == HTTPStatus.OK


def test_get_reco_success(
    client: TestClient,
    service_config: ServiceConfig,
) -> None:
    user_id = 123
    path = GET_RECO_PATH.format(model_name="rec_model", user_id=user_id)
    with client:
        response = client.get(path)
    assert response.status_code == HTTPStatus.OK
    response_json = response.json()
    assert response_json["user_id"] == user_id
    assert len(response_json["items"]) == service_config.k_recs
    assert all(isinstance(item_id, int) for item_id in response_json["items"])


def test_not_existing_model(client: TestClient) -> None:
    user_id = 123
    non_existing_model = "non_existing_model"
    path = GET_RECO_PATH.format(model_name=non_existing_model, user_id=user_id)
    
    with client:
        response = client.get(path)
    
    assert response.status_code == HTTPStatus.NOT_FOUND
    
    response_json = response.json()
    
    assert "errors" in response_json
    
    assert len(response_json["errors"]) > 0
    
    first_error = response_json["errors"][0]
    assert first_error["error_key"] == "http_exception"
    assert first_error["error_message"] == f"Model {non_existing_model} not found"


