# parameters.py
# =========================================================
from dataclasses import dataclass, field
from typing import Dict
# =========================================================

@dataclass
class ViralParameters:
    """病毒自然史参数"""
    beta_f: float = 0.470  # 女性基础传染概率
    beta_m: float = 0.235  # 男性基础传染概率
    genotype_distribution_scc: Dict[str, float] = field(default_factory=lambda: {
        '16': 0.642,
        '52': 0.056,
        '18': 0.054,
        'other': 0.248
    })

    external_infection_prob: float = 0.001
    viral_load_multiplier: float = 4.0
    clearance_rate_1618: float = 0.040
    clearance_rate_other: float = 0.051


@dataclass
class InterventionParameters:
    """干预措施参数"""
    vaccine_efficacy_2v: Dict[str, float] = field(default_factory=lambda: {
        '16': 0.973, '18': 0.973, '52': 0.0, 'other': 0.0
    })
    vaccine_efficacy_msm: float = 0.977

    test_sensitivity: float = 0.90
    screening_compliance: float = 0.50
    screening_start_year: int = 1
    screening_interval_months: int = 12
    treatment_success_rate: float = 0.846


@dataclass
class BehaviorParameters:
    """行为相关参数"""
    condom_usage_rate: float = 0.2

@dataclass
class GlobalConfig:
    viral: ViralParameters = field(default_factory=ViralParameters)
    intervention: InterventionParameters = field(default_factory=InterventionParameters)
    behavior: BehaviorParameters = field(default_factory=BehaviorParameters)

    steps_per_year: int = 12
    simulation_years: int = 4