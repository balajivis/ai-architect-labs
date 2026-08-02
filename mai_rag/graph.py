"""
mai_rag.graph — the GraphRAG layer, glass-box, two interchangeable backends.

The lab teaches GraphRAG PRIMITIVES, not a query language:

    g = graph.connect(user="asha")          # remote class graph if reachable, else local
    g.add_triples([("AI Practitioner", "teaches", "RAG"), ...])
    g.neighbors("RAG")                       # 1-2 hop neighborhood
    g.path("AI Practitioner", "evals")       # how are two entities connected?
    g.subgraph("RAG", hops=2)                # the retrieval unit GraphRAG stuffs into context
    g.stats() / g.clear()

Backends:
  · RemoteGraph — the class proxy (learn.modernaipro.com/api/graph/v1/query) in front
    of a shared Cosmos DB (Gremlin). Auth = the SAME class token as the LLM proxy
    (OPENAI_API_KEY in your .env); your `user` handle namespaces your partition, so
    every student plays in their own graph. Zero extra signup.
  · LocalGraph — networkx in-process. Keyless, offline, identical API — the lab's
    default path can never go down mid-class.

Plus the ingestion primitive: extract_triples(text) — LLM entity/relation extraction
(classification → LLM, per the house rule; never a pattern).
"""
from __future__ import annotations

import json
import os
from typing import Iterable

Triple = tuple[str, str, str]

def _norm(triples: Iterable) -> list[dict]:
    out = []
    for t in triples:
        if isinstance(t, dict):
            s, r, o = t.get("s"), t.get("r"), t.get("o")
        else:
            s, r, o = t
        if s and r and o:
            out.append({"s": str(s).strip(), "r": str(r).strip(), "o": str(o).strip()})
    return out


class LocalGraph:
    """networkx backend — same primitives, in-process, keyless."""

    def __init__(self):
        import networkx as nx
        self._nx = nx
        self.g = nx.MultiDiGraph()

    backend = "local (networkx)"

    def add_triples(self, triples: Iterable) -> dict:
        ts = _norm(triples)
        for t in ts:
            self.g.add_edge(t["s"].lower(), t["o"].lower(), label=t["r"].lower())
        return {"added": len(ts)}

    def neighbors(self, entity: str, depth: int = 1) -> list[Triple]:
        e = entity.lower()
        if e not in self.g:
            return []
        seen, frontier, out = {e}, {e}, []
        for _ in range(max(1, min(depth, 2))):
            nxt = set()
            for node in frontier:
                for u, v, d in list(self.g.out_edges(node, data=True)) + list(self.g.in_edges(node, data=True)):
                    out.append((u, d.get("label", "?"), v))
                    for cand in (u, v):
                        if cand not in seen:
                            seen.add(cand); nxt.add(cand)
            frontier = nxt
        return list(dict.fromkeys(out))

    def path(self, a: str, b: str) -> list[list[str]]:
        ug = self.g.to_undirected(as_view=True)
        try:
            p = self._nx.shortest_path(ug, a.lower(), b.lower())
        except Exception:
            return []
        return [p]

    def subgraph(self, entity: str, hops: int = 2) -> list[Triple]:
        return self.neighbors(entity, depth=hops)

    def clear(self) -> dict:
        n = self.g.number_of_nodes()
        self.g.clear()
        return {"dropped": n}

    def stats(self) -> dict:
        return {"vertices": self.g.number_of_nodes(), "edges": self.g.number_of_edges()}


class RemoteGraph:
    """The class proxy backend — typed ops over HTTPS with the class token."""

    def __init__(self, user: str, url: str | None = None, token: str | None = None):
        import requests
        self._rq = requests
        self.user = user
        self.url = (url or os.getenv("MAI_GRAPH_URL")
                    or "https://learn.modernaipro.com/api/graph/v1/query")
        self.token = token or os.getenv("OPENAI_API_KEY", "")
        self.backend = f"remote class graph ({self.url.split('/')[2]}) · partition stu-{user}"

    def _call(self, op: str, **kw):
        r = self._rq.post(self.url, timeout=float(os.getenv("MAI_GRAPH_TIMEOUT", "25")),
                          headers={"authorization": f"Bearer {self.token}", "content-type": "application/json"},
                          json={"op": op, "user": self.user, **kw})
        if r.status_code != 200:
            try:
                msg = r.json().get("error", r.text[:120])
            except Exception:
                msg = r.text[:120]
            raise RuntimeError(f"graph proxy {r.status_code}: {msg}")
        return r.json()

    def add_triples(self, triples: Iterable) -> dict:
        # Ingestion is the ONE bulk write, and a whole class shares the service — sending
        # 168 triples as a single request is what pushes past the timeout. Chunk it, so
        # each request is small and a slow service costs latency, not the stage.
        ts = _norm(triples)
        size = max(1, int(os.getenv("MAI_GRAPH_BATCH", "40")))
        added = 0
        for i in range(0, len(ts), size):
            added += int(self._call("add", triples=ts[i:i + size]).get("added", 0))
        return {"added": added}

    @staticmethod
    def _as_triples(entity: str, rows) -> list[Triple]:
        """The proxy answers a traversal as {"e": relation, "v": target}; LocalGraph
        answers (s, r, o). Same data, different shape — and callers that expect a triple
        (the labs do) would silently show NOTHING against the remote backend. Normalise
        here so "identical primitives either way" is true rather than aspirational.
        """
        out: list[Triple] = []
        for row in rows or []:
            if isinstance(row, dict):
                s = row.get("s") or row.get("from") or entity
                r = row.get("r") or row.get("e") or row.get("label") or "?"
                o = row.get("o") or row.get("v") or row.get("to") or ""
            elif isinstance(row, (list, tuple)) and len(row) == 3:
                s, r, o = row
            else:
                continue
            if o:
                out.append((str(s).lower(), str(r).lower(), str(o).lower()))
        return list(dict.fromkeys(out))

    def neighbors(self, entity: str, depth: int = 1):
        return self._as_triples(entity, self._call("neighbors", entity=entity, depth=depth).get("results", []))

    def path(self, a: str, b: str):
        return self._call("path", **{"from": a, "to": b}).get("paths", [])

    def subgraph(self, entity: str, hops: int = 2):
        return self._as_triples(entity, self._call("subgraph", entity=entity, hops=hops).get("paths", []))

    def clear(self) -> dict:
        return self._call("clear")

    def stats(self) -> dict:
        return self._call("stats")


class ResilientGraph:
    """Remote-first with an operation-time rescue — the honest version of "the hosted
    path going down must never kill the lab".

    `connect()`'s reachability probe only proves the service was up at connect time. The
    failure students actually hit is a service that answers the cheap probe and then
    times out on a real operation. So: remember every triple we've written, and on the
    first operation failure, degrade to networkx, REPLAY what was already loaded, and
    carry on with the same API. Degrading is announced, never silent — a fallback you
    can't see is how you ship a demo that was secretly never using the thing you were
    demoing.
    """

    def __init__(self, remote):
        self._g = remote
        self._added: list[dict] = []
        self.degraded = False

    @property
    def backend(self) -> str:
        return self._g.backend

    def _rescue(self, op: str, exc: Exception):
        if self.degraded:
            raise exc                     # already local — a local failure is a real bug
        print(f"[mai_rag.graph] class graph failed on {op}() ({type(exc).__name__}: "
              f"{str(exc)[:70]}) — degrading to local networkx and replaying "
              f"{len(self._added)} triples")
        local = LocalGraph()
        if self._added:
            local.add_triples(self._added)
        self._g, self.degraded = local, True

    def add_triples(self, triples: Iterable) -> dict:
        ts = _norm(triples)
        try:
            res = self._g.add_triples(ts)
        except Exception as e:
            self._rescue("add_triples", e)      # replays self._added into the fresh local
            res = self._g.add_triples(ts)
        self._added.extend(ts)
        return res

    def _read(self, op: str, *a, **kw):
        try:
            return getattr(self._g, op)(*a, **kw)
        except Exception as e:
            self._rescue(op, e)
            return getattr(self._g, op)(*a, **kw)

    def neighbors(self, entity: str, depth: int = 1):
        return self._read("neighbors", entity, depth)

    def path(self, a: str, b: str):
        return self._read("path", a, b)

    def subgraph(self, entity: str, hops: int = 2):
        return self._read("subgraph", entity, hops)

    def stats(self) -> dict:
        return self._read("stats")

    def clear(self) -> dict:
        self._added.clear()
        return self._read("clear")


def connect(user: str = "student", prefer: str = "auto"):
    """auto → remote class graph when reachable, LocalGraph otherwise (stated out loud —
    the hosted path going down must never kill the lab).

    MAI_GRAPH_BACKEND=local forces networkx without touching the network — the escape
    hatch for a class service that is *reachable but slow* (a full room writing into one
    partition), where the reachability probe below passes and a later bulk write is the
    thing that times out.
    """
    prefer = (os.getenv("MAI_GRAPH_BACKEND") or prefer).strip().lower()
    if prefer in ("auto", "remote"):
        try:
            g = RemoteGraph(user)
            g.stats()                                    # one cheap reachability probe
            return ResilientGraph(g)                     # …and a rescue for every op after it
        except Exception as e:
            if prefer == "remote":
                raise
            print(f"[mai_rag.graph] class graph unreachable ({str(e)[:60]}) — using local networkx")
    return LocalGraph()


def extract_triples(text: str, max_triples: int = 15) -> list[Triple]:
    """The GraphRAG ingestion primitive: LLM entity/relation extraction (never a regex)."""
    from . import llm
    d = llm.complete_json(
        "Extract the key entity relationships from this document as subject-relation-object "
        "triples. Entities are short noun phrases; relations are 1-3 word verbs "
        f"(e.g. requires, supersedes, escalates_to, part_of). At most {max_triples}.\n"
        'JSON: {"triples": [["subject", "relation", "object"], ...]}\n\n' + text[:6000])
    return [tuple(map(str, t))[:3] for t in d.get("triples", []) if len(t) == 3]
