"""
Decision Tree Analysis Engine
Motor de Árboles de Decisión para evaluaciones farmacoeconómicas

Implementa árboles de decisión con:
- Nodos de decisión (choice nodes)
- Nodos de probabilidad (chance nodes)
- Nodos terminales (payoffs)
- Roll-back analysis
- Análisis de sensibilidad one-way y two-way
"""

import numpy as np
from typing import Dict, List, Optional, Union, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
from copy import deepcopy
import uuid


class NodeType(str, Enum):
    """Tipos de nodos en el árbol"""
    DECISION = "decision"  # Nodo de decisión (cuadrado)
    CHANCE = "chance"  # Nodo de probabilidad (círculo)
    TERMINAL = "terminal"  # Nodo terminal (triángulo)


@dataclass
class Payoff:
    """Payoff de un nodo terminal"""
    cost: float = 0.0
    effectiveness: float = 0.0  # QALYs, LYs, u otra medida
    utility: float = 0.0
    other_outcomes: Dict[str, float] = field(default_factory=dict)


@dataclass
class TreeNode:
    """Nodo del árbol de decisión"""
    id: str
    name: str
    node_type: NodeType
    probability: Optional[float] = None  # Para nodos chance
    payoff: Optional[Payoff] = None  # Para nodos terminales
    children: List['TreeNode'] = field(default_factory=list)
    parent_id: Optional[str] = None

    # Resultados del roll-back
    expected_cost: Optional[float] = None
    expected_effectiveness: Optional[float] = None
    optimal_choice: Optional[str] = None  # Para nodos decisión

    def __post_init__(self):
        if not self.id:
            self.id = str(uuid.uuid4())[:8]


@dataclass
class DecisionTreeConfig:
    """Configuración del árbol de decisión"""
    name: str = "Decision Tree Analysis"
    perspective: str = "payer"
    currency: str = "EUR"
    effectiveness_measure: str = "QALY"  # QALY, LY, event_free, etc.
    wtp_threshold: float = 30000.0  # Willingness-to-pay threshold


@dataclass
class StrategyResult:
    """Resultado de una estrategia (rama del árbol)"""
    strategy_name: str
    expected_cost: float
    expected_effectiveness: float
    probability_weighted_outcomes: List[Dict[str, Any]]


@dataclass
class ICERResult:
    """Resultado ICER entre dos estrategias"""
    comparator: str
    intervention: str
    delta_cost: float
    delta_effectiveness: float
    icer: Optional[float]
    is_dominated: bool
    is_cost_effective: bool
    net_monetary_benefit: float


class DecisionTree:
    """
    Árbol de Decisión para análisis farmacoeconómico

    Soporta:
    - Construcción de árboles con múltiples niveles
    - Roll-back analysis
    - Comparación de estrategias
    - Análisis de sensibilidad
    """

    def __init__(self, config: DecisionTreeConfig):
        self.config = config
        self.root: Optional[TreeNode] = None
        self.nodes: Dict[str, TreeNode] = {}

    def create_node(
        self,
        name: str,
        node_type: NodeType,
        probability: Optional[float] = None,
        cost: float = 0.0,
        effectiveness: float = 0.0,
        parent_id: Optional[str] = None
    ) -> TreeNode:
        """Crear un nuevo nodo"""
        node_id = str(uuid.uuid4())[:8]

        payoff = None
        if node_type == NodeType.TERMINAL:
            payoff = Payoff(cost=cost, effectiveness=effectiveness)

        node = TreeNode(
            id=node_id,
            name=name,
            node_type=node_type,
            probability=probability,
            payoff=payoff,
            parent_id=parent_id
        )

        self.nodes[node_id] = node

        if parent_id and parent_id in self.nodes:
            self.nodes[parent_id].children.append(node)

        if self.root is None and parent_id is None:
            self.root = node

        return node

    def add_child(self, parent_id: str, child: TreeNode):
        """Añadir hijo a un nodo"""
        if parent_id in self.nodes:
            child.parent_id = parent_id
            self.nodes[parent_id].children.append(child)
            self.nodes[child.id] = child

    def build_from_dict(self, tree_dict: Dict) -> TreeNode:
        """
        Construir árbol desde diccionario

        Formato esperado:
        {
            "name": "Root Decision",
            "type": "decision",
            "children": [
                {
                    "name": "Strategy A",
                    "type": "chance",
                    "children": [
                        {"name": "Success", "type": "terminal", "probability": 0.7,
                         "cost": 1000, "effectiveness": 0.9},
                        {"name": "Failure", "type": "terminal", "probability": 0.3,
                         "cost": 5000, "effectiveness": 0.3}
                    ]
                },
                ...
            ]
        }
        """
        def build_node(node_dict: Dict, parent_id: Optional[str] = None) -> TreeNode:
            node_type = NodeType(node_dict.get("type", "terminal"))

            payoff = None
            if node_type == NodeType.TERMINAL:
                payoff = Payoff(
                    cost=node_dict.get("cost", 0),
                    effectiveness=node_dict.get("effectiveness", 0),
                    utility=node_dict.get("utility", 0)
                )

            node = TreeNode(
                id=node_dict.get("id", str(uuid.uuid4())[:8]),
                name=node_dict.get("name", "Unnamed"),
                node_type=node_type,
                probability=node_dict.get("probability"),
                payoff=payoff,
                parent_id=parent_id
            )

            self.nodes[node.id] = node

            # Procesar hijos recursivamente
            for child_dict in node_dict.get("children", []):
                child = build_node(child_dict, node.id)
                node.children.append(child)

            return node

        self.root = build_node(tree_dict)
        return self.root

    def rollback(self, node: Optional[TreeNode] = None) -> Tuple[float, float]:
        """
        Realizar roll-back analysis desde las hojas hasta la raíz

        Returns:
            Tuple de (expected_cost, expected_effectiveness)
        """
        if node is None:
            node = self.root

        if node is None:
            raise ValueError("No root node defined")

        # Caso base: nodo terminal
        if node.node_type == NodeType.TERMINAL:
            node.expected_cost = node.payoff.cost if node.payoff else 0
            node.expected_effectiveness = node.payoff.effectiveness if node.payoff else 0
            return node.expected_cost, node.expected_effectiveness

        # Calcular valores esperados de hijos
        child_results = []
        for child in node.children:
            cost, eff = self.rollback(child)
            child_results.append({
                'node': child,
                'cost': cost,
                'effectiveness': eff,
                'probability': child.probability or 0
            })

        if node.node_type == NodeType.CHANCE:
            # Nodo de probabilidad: promedio ponderado
            total_prob = sum(c['probability'] for c in child_results)
            if total_prob == 0:
                total_prob = 1  # Evitar división por cero

            node.expected_cost = sum(
                c['cost'] * c['probability'] / total_prob
                for c in child_results
            )
            node.expected_effectiveness = sum(
                c['effectiveness'] * c['probability'] / total_prob
                for c in child_results
            )

        elif node.node_type == NodeType.DECISION:
            # Nodo de decisión: elegir mejor opción
            # Criterio: maximizar Net Monetary Benefit
            best = None
            best_nmb = float('-inf')

            for c in child_results:
                nmb = (c['effectiveness'] * self.config.wtp_threshold) - c['cost']
                if nmb > best_nmb:
                    best_nmb = nmb
                    best = c

            if best:
                node.expected_cost = best['cost']
                node.expected_effectiveness = best['effectiveness']
                node.optimal_choice = best['node'].name
            else:
                node.expected_cost = 0
                node.expected_effectiveness = 0

        return node.expected_cost, node.expected_effectiveness

    def get_strategy_results(self) -> List[StrategyResult]:
        """
        Obtener resultados por estrategia (hijos directos de la raíz)
        """
        if self.root is None or self.root.node_type != NodeType.DECISION:
            return []

        results = []
        for strategy_node in self.root.children:
            # Ejecutar roll-back para esta rama
            cost, eff = self.rollback(strategy_node)

            # Recoger outcomes terminales
            terminal_outcomes = self._collect_terminal_outcomes(strategy_node)

            results.append(StrategyResult(
                strategy_name=strategy_node.name,
                expected_cost=cost,
                expected_effectiveness=eff,
                probability_weighted_outcomes=terminal_outcomes
            ))

        return results

    def _collect_terminal_outcomes(
        self,
        node: TreeNode,
        cumulative_prob: float = 1.0
    ) -> List[Dict[str, Any]]:
        """Recoger todos los outcomes terminales con probabilidades acumuladas"""
        outcomes = []

        if node.node_type == NodeType.TERMINAL:
            outcomes.append({
                'name': node.name,
                'probability': cumulative_prob,
                'cost': node.payoff.cost if node.payoff else 0,
                'effectiveness': node.payoff.effectiveness if node.payoff else 0
            })
        else:
            for child in node.children:
                child_prob = child.probability if child.probability else 1.0
                outcomes.extend(
                    self._collect_terminal_outcomes(child, cumulative_prob * child_prob)
                )

        return outcomes

    def calculate_icer(
        self,
        comparator_name: str,
        intervention_name: str
    ) -> ICERResult:
        """
        Calcular ICER entre dos estrategias
        """
        results = {r.strategy_name: r for r in self.get_strategy_results()}

        if comparator_name not in results or intervention_name not in results:
            raise ValueError("Strategy not found")

        comp = results[comparator_name]
        interv = results[intervention_name]

        delta_cost = interv.expected_cost - comp.expected_cost
        delta_eff = interv.expected_effectiveness - comp.expected_effectiveness

        # Determinar dominancia
        is_dominated = delta_cost > 0 and delta_eff <= 0

        # Calcular ICER
        if delta_eff == 0:
            icer = float('inf') if delta_cost > 0 else float('-inf')
        else:
            icer = delta_cost / delta_eff

        # Net Monetary Benefit
        nmb = (delta_eff * self.config.wtp_threshold) - delta_cost
        is_cost_effective = nmb > 0

        return ICERResult(
            comparator=comparator_name,
            intervention=intervention_name,
            delta_cost=delta_cost,
            delta_effectiveness=delta_eff,
            icer=icer if abs(icer) != float('inf') else None,
            is_dominated=is_dominated,
            is_cost_effective=is_cost_effective,
            net_monetary_benefit=nmb
        )

    def one_way_sensitivity(
        self,
        parameter_path: str,  # "Strategy A/Success/probability"
        low_value: float,
        high_value: float,
        n_steps: int = 10
    ) -> Dict[str, Any]:
        """
        Análisis de sensibilidad one-way

        Args:
            parameter_path: Ruta al parámetro (nodo/atributo)
            low_value: Valor mínimo
            high_value: Valor máximo
            n_steps: Número de pasos

        Returns:
            Resultados del análisis
        """
        values = np.linspace(low_value, high_value, n_steps)
        results = []

        # Parsear path
        parts = parameter_path.split('/')
        node_name = '/'.join(parts[:-1])
        attribute = parts[-1]

        # Encontrar nodo
        target_node = None
        for node in self.nodes.values():
            if node.name == node_name or node_name in node.name:
                target_node = node
                break

        if target_node is None:
            return {"error": f"Node not found: {node_name}"}

        original_value = None

        for value in values:
            # Modificar parámetro
            if attribute == "probability":
                original_value = original_value or target_node.probability
                target_node.probability = value
            elif attribute == "cost" and target_node.payoff:
                original_value = original_value or target_node.payoff.cost
                target_node.payoff.cost = value
            elif attribute == "effectiveness" and target_node.payoff:
                original_value = original_value or target_node.payoff.effectiveness
                target_node.payoff.effectiveness = value

            # Recalcular
            self.rollback()
            strategies = self.get_strategy_results()

            results.append({
                'parameter_value': value,
                'strategies': [
                    {
                        'name': s.strategy_name,
                        'cost': s.expected_cost,
                        'effectiveness': s.expected_effectiveness
                    }
                    for s in strategies
                ]
            })

        # Restaurar valor original
        if original_value is not None:
            if attribute == "probability":
                target_node.probability = original_value
            elif attribute == "cost" and target_node.payoff:
                target_node.payoff.cost = original_value
            elif attribute == "effectiveness" and target_node.payoff:
                target_node.payoff.effectiveness = original_value

        return {
            "parameter": parameter_path,
            "range": [low_value, high_value],
            "results": results
        }

    def to_dict(self) -> Dict:
        """Convertir árbol a diccionario para serialización"""
        def node_to_dict(node: TreeNode) -> Dict:
            d = {
                'id': node.id,
                'name': node.name,
                'type': node.node_type.value,
                'expected_cost': node.expected_cost,
                'expected_effectiveness': node.expected_effectiveness
            }

            if node.probability is not None:
                d['probability'] = node.probability

            if node.payoff:
                d['payoff'] = {
                    'cost': node.payoff.cost,
                    'effectiveness': node.payoff.effectiveness
                }

            if node.optimal_choice:
                d['optimal_choice'] = node.optimal_choice

            if node.children:
                d['children'] = [node_to_dict(c) for c in node.children]

            return d

        return node_to_dict(self.root) if self.root else {}


def run_decision_tree_analysis(params: Dict) -> Dict:
    """
    Punto de entrada principal para análisis de árbol de decisión

    Args:
        params: Diccionario con estructura del árbol y configuración

    Returns:
        Resultados del análisis
    """
    config = DecisionTreeConfig(
        name=params.get("name", "Decision Tree Analysis"),
        perspective=params.get("perspective", "payer"),
        currency=params.get("currency", "EUR"),
        effectiveness_measure=params.get("effectiveness_measure", "QALY"),
        wtp_threshold=params.get("wtp_threshold", 30000.0)
    )

    tree = DecisionTree(config)

    # Construir árbol desde estructura
    tree_structure = params.get("tree", None)

    if tree_structure:
        tree.build_from_dict(tree_structure)
    else:
        # Árbol de ejemplo por defecto
        tree.build_from_dict({
            "name": "Treatment Decision",
            "type": "decision",
            "children": [
                {
                    "name": "New Treatment",
                    "type": "chance",
                    "children": [
                        {
                            "name": "Success",
                            "type": "terminal",
                            "probability": 0.75,
                            "cost": 15000,
                            "effectiveness": 0.9
                        },
                        {
                            "name": "Failure",
                            "type": "terminal",
                            "probability": 0.25,
                            "cost": 25000,
                            "effectiveness": 0.4
                        }
                    ]
                },
                {
                    "name": "Standard Care",
                    "type": "chance",
                    "children": [
                        {
                            "name": "Success",
                            "type": "terminal",
                            "probability": 0.55,
                            "cost": 8000,
                            "effectiveness": 0.85
                        },
                        {
                            "name": "Failure",
                            "type": "terminal",
                            "probability": 0.45,
                            "cost": 20000,
                            "effectiveness": 0.35
                        }
                    ]
                }
            ]
        })

    # Ejecutar roll-back
    tree.rollback()

    # Obtener resultados por estrategia
    strategies = tree.get_strategy_results()

    # Calcular ICERs
    icer_results = []
    if len(strategies) >= 2:
        comparator = strategies[0]
        for intervention in strategies[1:]:
            try:
                icer = tree.calculate_icer(comparator.strategy_name, intervention.strategy_name)
                icer_results.append({
                    "comparator": icer.comparator,
                    "intervention": icer.intervention,
                    "delta_cost": round(icer.delta_cost, 2),
                    "delta_effectiveness": round(icer.delta_effectiveness, 4),
                    "icer": round(icer.icer, 2) if icer.icer else None,
                    "is_dominated": icer.is_dominated,
                    "is_cost_effective": icer.is_cost_effective,
                    "net_monetary_benefit": round(icer.net_monetary_benefit, 2)
                })
            except Exception:
                pass

    # Determinar estrategia óptima
    optimal = tree.root.optimal_choice if tree.root else None

    return {
        "status": "success",
        "config": {
            "name": config.name,
            "perspective": config.perspective,
            "currency": config.currency,
            "effectiveness_measure": config.effectiveness_measure,
            "wtp_threshold": config.wtp_threshold
        },
        "optimal_strategy": optimal,
        "strategies": [
            {
                "name": s.strategy_name,
                "expected_cost": round(s.expected_cost, 2),
                "expected_effectiveness": round(s.expected_effectiveness, 4),
                "outcomes": s.probability_weighted_outcomes
            }
            for s in strategies
        ],
        "icer_analysis": icer_results,
        "tree_structure": tree.to_dict()
    }
