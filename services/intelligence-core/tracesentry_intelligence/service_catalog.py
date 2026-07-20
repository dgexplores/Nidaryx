from __future__ import annotations

from collections import defaultdict, deque
from collections.abc import Iterable

from tracesentry_contracts import ServiceDependency


class DependencyGraph:
    def __init__(self, dependencies: Iterable[ServiceDependency] = ()) -> None:
        self._downstreams: dict[str, set[str]] = defaultdict(set)
        self._upstreams: dict[str, set[str]] = defaultdict(set)
        self._services: set[str] = set()
        for dependency in dependencies:
            self.add(dependency.upstream, dependency.downstream)

    def add(self, upstream: str, downstream: str) -> None:
        if not upstream or not downstream:
            raise ValueError("upstream and downstream are required")
        self._downstreams[upstream].add(downstream)
        self._upstreams[downstream].add(upstream)
        self._services.update({upstream, downstream})

    def downstreams(self, service: str) -> frozenset[str]:
        return frozenset(self._downstreams.get(service, set()))

    def upstreams(self, service: str) -> frozenset[str]:
        return frozenset(self._upstreams.get(service, set()))

    def are_adjacent(self, left: str, right: str) -> bool:
        return (
            left == right
            or right in self._downstreams.get(left, set())
            or right in self._upstreams.get(left, set())
        )

    def is_upstream(self, candidate: str, service: str, max_depth: int = 4) -> bool:
        if candidate == service:
            return False
        visited: set[str] = set()
        queue: deque[tuple[str, int]] = deque((upstream, 1) for upstream in self.upstreams(service))
        while queue:
            current, depth = queue.popleft()
            if current == candidate:
                return True
            if current in visited or depth >= max_depth:
                continue
            visited.add(current)
            queue.extend((upstream, depth + 1) for upstream in self.upstreams(current))
        return False

    def services(self) -> frozenset[str]:
        return frozenset(self._services)

