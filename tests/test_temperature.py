import unittest

import httpx

from bot.api.core_switch import CoreSwitchClient
from bot.formatters import format_contactors, format_temperature


class TemperatureFormattingTests(unittest.TestCase):
    def test_temperature_payload_includes_transformer_and_ambient_values(self):
        payload = {
            "success": True,
            "data": {
                "temperature_c": 52.1,
                "ambient_temperature_c": 25.3,
            },
        }

        text = format_temperature(payload)
        self.assertIn("Temperatura", text)
        self.assertIn("Trafo: <b>52.1</b> °C", text)
        self.assertIn("Ambiente: <b>25.3</b> °C", text)

    def test_contactors_normalize_boolean_and_unknown_states(self):
        status = {
            "C1": {"name": "C1", "state": True},
            "C2": {"name": "C2", "state": False},
            "C3": {"name": "C3", "state": "desconocido"},
        }

        text = format_contactors(status)
        self.assertIn("🟢 C1", text)
        self.assertIn("<b>ON</b>", text)
        self.assertIn("🔴 C2", text)
        self.assertIn("<b>OFF</b>", text)
        self.assertIn("⚪ C3", text)
        self.assertIn("<b>UNKNOWN</b>", text)

    def test_contactors_handles_api_nested_contactors_key(self):
        """La API real devuelve {contactors: {C1, C2, C3}}."""
        status = {
            "contactors": {
                "C1": {"name": "Contactor 1", "state": "ON"},
                "C2": {"name": "Contactor 2", "state": "OFF"},
                "C3": {"name": "Contactor 3", "state": "UNKNOWN", "error": "Offline"},
            }
        }

        text = format_contactors(status)
        self.assertIn("🟢 C1 (Contactor 1): <b>ON</b>", text)
        self.assertIn("🔴 C2 (Contactor 2): <b>OFF</b>", text)
        self.assertIn("⚪ C3 (Contactor 3): <b>UNKNOWN</b>", text)
        self.assertIn("⚠ Offline", text)


class CoreSwitchClientSwitchCompatibilityTests(unittest.IsolatedAsyncioTestCase):
    async def test_switch_contactor_retries_lowercase_endpoint(self):
        client = CoreSwitchClient("http://example.test")
        seen = []

        class FakeResponse:
            def __init__(self, payload):
                self._payload = payload

            def raise_for_status(self):
                return None

            def json(self):
                return self._payload

        class FakeTransport:
            async def post(self, path, json=None):
                seen.append((path, json))
                if path == "/switch/c1":
                    return FakeResponse({"success": True, "message": "ok"})
                raise httpx.HTTPStatusError("not found", request=httpx.Request("POST", "http://example.test" + path), response=httpx.Response(404, request=httpx.Request("POST", "http://example.test" + path)))

        client._client = FakeTransport()

        result = await client.switch_contactor("C1", True)

        self.assertTrue(result["success"])
        self.assertTrue(any(path == "/switch/c1" for path, _ in seen))

    async def test_switch_general_retries_compatibility_payload(self):
        client = CoreSwitchClient("http://example.test")
        seen = []

        class FakeResponse:
            def __init__(self, payload):
                self._payload = payload

            def raise_for_status(self):
                return None

            def json(self):
                return self._payload

        class FakeTransport:
            async def post(self, path, json=None):
                seen.append((path, json))
                if path == "/switch/general" and json == {"estado": True}:
                    return FakeResponse({"success": True, "message": "ok"})
                raise httpx.HTTPStatusError("not found", request=httpx.Request("POST", "http://example.test" + path), response=httpx.Response(404, request=httpx.Request("POST", "http://example.test" + path)))

        client._client = FakeTransport()

        result = await client.switch_general(True)

        self.assertTrue(result["success"])
        self.assertTrue(any(path == "/switch/general" and payload == {"estado": True} for path, payload in seen))


if __name__ == "__main__":
    unittest.main()
