import unittest

from bot.formatters import format_temperature


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


if __name__ == "__main__":
    unittest.main()
