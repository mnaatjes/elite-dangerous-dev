# tests/unit/test_gateway.py
from dataclasses import dataclass
from typing import Callable, Any
from src.gateways import BaseGateway, FilesystemGateway
from src.gateways.models.request_dto import GatewayRequest
from src.gateways.models.simple_request import SimpleRequest

def test_execute(gateway):
    request = SimpleRequest(
        plan="save_json_atomic",
        payload="json string of sorts",
        target="downloads/2022/file.json"
    )

    gateway.execute(request)