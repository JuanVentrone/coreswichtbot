from __future__ import annotations

from typing import Any

import httpx


class CoreSwitchClient:
    """HTTP client for Core Swicht V2 (same endpoints as Pain Farm)."""

    def __init__(self, base_url: str, timeout: float = 20.0) -> None:
        self.base_url = base_url.rstrip("/")
        self._client = httpx.AsyncClient(
            base_url=self.base_url,
            headers={"Accept": "application/json", "Content-Type": "application/json"},
            timeout=timeout,
        )

    async def aclose(self) -> None:
        await self._client.aclose()

    async def _get(self, path: str) -> dict[str, Any]:
        response = await self._client.get(path)
        response.raise_for_status()
        data = response.json()
        return data if isinstance(data, dict) else {"data": data}

    async def _post(self, path: str, payload: dict[str, Any]) -> dict[str, Any]:
        response = await self._client.post(path, json=payload)
        response.raise_for_status()
        data = response.json()
        return data if isinstance(data, dict) else {"data": data}

    async def health(self) -> dict[str, Any]:
        return await self._get("/health")

    async def heartbeat(self) -> dict[str, Any]:
        return await self._get("/heartbeat")

    async def devices_status(self) -> dict[str, Any]:
        return await self._get("/devices/status")

    async def general_status(self) -> dict[str, Any]:
        return await self._get("/status/general")

    async def power_metrics(self) -> dict[str, Any]:
        return await self._get("/metrics/power")

    async def temperature_metrics(self) -> dict[str, Any]:
        return await self._get("/metrics/temperature")

    async def switch_general(self, on: bool) -> dict[str, Any]:
        return await self._post("/switch/general", {"estado": on})

    async def switch_contactor(self, contactor_id: str, on: bool) -> dict[str, Any]:
        return await self._post(f"/switch/{contactor_id}", {"estado": on})

    async def switch_luces(self, on: bool) -> dict[str, Any]:
        return await self._post("/switch/luces", {"estado": on})

    async def switch_bocina(self, on: bool) -> dict[str, Any]:
        return await self._post("/switch/bocina", {"estado": on})
