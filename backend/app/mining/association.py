"""Aporte 5 (minería): reglas de asociación y repositorio de procedimientos."""

from __future__ import annotations

from collections import defaultdict
from itertools import combinations

import pandas as pd

from app.mining.cleaning import default_prepared


def _transactions(df: pd.DataFrame) -> list[frozenset[str]]:
    rows = []
    for _, row in df.iterrows():
        items = {
            f"categoria={row.get('category')}",
            f"sector={row.get('sector')}",
            f"perfil={row.get('author_profile')}",
            f"equipo={'grande' if int(row.get('team_size') or 0) >= 2 else 'solo'}",
            f"resultado={row.get('acceptance_level')}",
        }
        rows.append(frozenset(x for x in items if not str(x).endswith("=nan") and not str(x).endswith("=None")))
    return rows


def apriori(transactions: list[frozenset[str]], min_support: float = 0.08, max_k: int = 3) -> dict[frozenset[str], float]:
    n = len(transactions)
    counts: dict[frozenset[str], int] = defaultdict(int)
    for t in transactions:
        for item in t:
            counts[frozenset([item])] += 1
    frequent = {k: v / n for k, v in counts.items() if v / n >= min_support}
    current = set(frequent)
    k = 2
    while current and k <= max_k:
        candidates = set()
        current_list = list(current)
        for i, a in enumerate(current_list):
            for b in current_list[i + 1 :]:
                union = a | b
                if len(union) == k:
                    candidates.add(union)
        counts = defaultdict(int)
        for t in transactions:
            for cand in candidates:
                if cand <= t:
                    counts[cand] += 1
        nxt = {k for k, v in counts.items() if v / n >= min_support}
        for itemset in nxt:
            frequent[itemset] = counts[itemset] / n
        current = nxt
        k += 1
    return frequent


def association_rules(min_support: float = 0.08, min_confidence: float = 0.45) -> dict:
    df = default_prepared()["frames"]["integrated"]
    tx = _transactions(df)
    frequent = apriori(tx, min_support=min_support)
    n = len(tx)
    rules = []
    for itemset, support in frequent.items():
        if len(itemset) < 2:
            continue
        items = list(itemset)
        for r in range(1, len(items)):
            for ant in combinations(items, r):
                antecedent = frozenset(ant)
                consequent = itemset - antecedent
                if not consequent:
                    continue
                sup_ant = frequent.get(antecedent)
                if not sup_ant:
                    continue
                confidence = support / sup_ant
                if confidence < min_confidence:
                    continue
                sup_cons = frequent.get(consequent, 0) or sum(1 for t in tx if consequent <= t) / n
                lift = confidence / sup_cons if sup_cons else 0
                rules.append(
                    {
                        "antecedent": sorted(antecedent),
                        "consequent": sorted(consequent),
                        "support": round(support, 3),
                        "confidence": round(confidence, 3),
                        "lift": round(lift, 3),
                    }
                )
    rules = sorted(rules, key=lambda r: (r["lift"], r["confidence"]), reverse=True)[:40]
    result_rules = [r for r in rules if any(c.startswith("resultado=") for c in r["consequent"])]

    return {
        "aporte": 5,
        "asignatura": "Minería de datos",
        "entregable": "Repositorio de algoritmos, reglas de asociación y visualizaciones tabulares",
        "algorithm": "Apriori",
        "min_support": min_support,
        "min_confidence": min_confidence,
        "n_transactions": n,
        "n_frequent_itemsets": len(frequent),
        "rules_top": rules[:20],
        "rules_towards_evaluation_result": result_rules[:15],
        "scripts": [
            "app/mining/cleaning.py",
            "app/mining/patterns.py",
            "app/mining/predictive.py",
            "app/mining/segmentation.py",
            "app/mining/association.py",
        ],
        "visualization_tables": {
            "support_itemsets": [
                {"itemset": " + ".join(sorted(k)), "support": round(v, 3)}
                for k, v in sorted(frequent.items(), key=lambda kv: kv[1], reverse=True)[:15]
            ]
        },
        "reading": (
            "Las reglas con lift > 1 indican asociación positiva entre tipo de propuesta, "
            "sector, tamaño de equipo y resultado de evaluación."
        ),
    }
