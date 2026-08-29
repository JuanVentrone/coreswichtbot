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

    async def _post_fallback(self, candidates: list[tuple[str, dict[str, Any]]]) -> dict[str, Any]:
        last_error: Exception | None = None
        for path, payload in candidates:
            try:
                return await self._post(path, payload)
            except httpx.HTTPError as exc:
                last_error = exc
                continue

        if last_error is not None:
            raise last_error
        raise RuntimeError("No hay candidatos válidos para la operación solicitada")

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
        candidates: list[tuple[str, dict[str, Any]]] = []
        for payload in ({"estado": on}, {"state": on}, {"status": on}, {"on": on}):
            candidates.extend(
                [
                    ("/switch/general", payload),
                    ("/switch/general/state", payload),
                    ("/switch/system", payload),
                    ("/switch", payload),
                ]
            )
        return await self._post_fallback(candidates)

    async def switch_contactor(self, contactor_id: str, on: bool) -> dict[str, Any]:
        variants = {contactor_id, contactor_id.upper(), contactor_id.lower()}
        if contactor_id.isdigit():
            variants.add(f"contactor_{contactor_id}")
        candidates: list[tuple[str, dict[str, Any]]] = []
        for target in sorted(variants):
            for payload in ({"estado": on}, {"state": on}, {"status": on}, {"on": on}, {"target": target, "estado": on}):
                candidates.extend(
                    [
                        (f"/switch/{target}", payload),
                        (f"/switch/{target}/state", payload),
                        (f"/switch/contactor/{target}", payload),
                        (f"/switch/contactor/{target}/state", payload),
                    ]
                )
        return await self._post_fallback(candidates)

    async def switch_luces(self, on: bool) -> dict[str, Any]:
        candidates: list[tuple[str, dict[str, Any]]] = []
        for payload in ({"estado": on}, {"state": on}, {"status": on}, {"on": on}):
            candidates.extend(
                [
                    ("/switch/luces", payload),
                    ("/switch/light", payload),
                    ("/switch/luces/state", payload),
                ]
            )
        return await self._post_fallback(candidates)

    async def switch_bocina(self, on: bool) -> dict[str, Any]:
        candidates: list[tuple[str, dict[str, Any]]] = []
        for payload in ({"estado": on}, {"state": on}, {"status": on}, {"on": on}):
            candidates.extend(
                [
                    ("/switch/bocina", payload),
                    ("/switch/sound", payload),
                    ("/switch/bocina/state", payload),
                ]
            )
        return await self._post_fallback(candidates)
