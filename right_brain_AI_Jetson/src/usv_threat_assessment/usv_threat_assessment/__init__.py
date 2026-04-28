"""USV Left Brain - Threat Assessment Module

Responsible for:
- Target threat level evaluation (1-5)
- Intent inference
- Engagement rule compliance check
- Attack suggestion generation
"""

from .threat_evaluator import ThreatEvaluator

__all__ = ['ThreatEvaluator']
