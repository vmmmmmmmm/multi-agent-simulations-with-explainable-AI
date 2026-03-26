# sensitivity_n_scenarios.py
from dataclasses import dataclass, field
from typing import Dict
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import random
from tqdm import tqdm
from model import University

def get_updated_params():
    return {
        "rewire_prob": random.uniform(0.0, 0.2),
        "avg_degree": random.randint(2, 10),
        "condom_usage": random.uniform(0.0, 0.8),
        "viral_load_impact": random.uniform(2.0, 5.0),
        "clearance_1618": random.uniform(0.03, 0.06),
        "screen_compliance": random.uniform(0.3, 0.95),
        "test_sensitivity": random.uniform(0.75, 0.99),
        "treat_success": random.uniform(0.80, 0.90),
        "start_year": random.choice([1, 2, 3]),
        "vax_female": random.uniform(0.0, 1.0),
        "vax_male": random.uniform(0.0, 1.0)
    }

def run_single_simulation(params, steps=48):
    model = University(N=1000, avg_degree=params["avg_degree"], rewire_prob=params["rewire_prob"])

    model.params.behavior.condom_usage_rate = params["condom_usage"]
    model.params.viral.viral_load_multiplier = params["viral_load_impact"]
    model.params.viral.clearance_rate_1618 = params["clearance_1618"]
    model.params.intervention.screening_compliance = params["screen_compliance"]
    model.params.intervention.test_sensitivity = params["test_sensitivity"]
    model.params.intervention.treatment_success_rate = params["treat_success"]
    model.params.intervention.screening_start_year = params["start_year"]

    # 修改为使用 model.agents
    for agent in model.agents:
        if agent.gender == 0 and random.random() < params["vax_female"]:
            agent.is_vaccinated = True
        elif agent.gender == 1 and random.random() < params["vax_male"]:
            agent.is_vaccinated = True

    for _ in range(steps):
        model.step()

    # 修改为使用 model.agents
    final_infected = sum([1 for a in model.agents if a.hpv_status == 'infected'])
    return final_infected / 1000.0


MAX_N = 2000
results = []
running_means = []
running_stds = []

print(f"--- 开始 N_SCENARIOS 收敛性测试 (Max N={MAX_N}) ---")

for i in tqdm(range(MAX_N)):
    params = get_updated_params()
    rate = run_single_simulation(params)
    results.append(rate)

    current_mean = np.mean(results)
    current_std = np.std(results)
    running_means.append(current_mean)
    running_stds.append(current_std)

ns = np.arange(1, MAX_N + 1)
cis = 1.96 * np.array(running_stds) / np.sqrt(ns)
lower_bound = np.array(running_means) - cis
upper_bound = np.array(running_means) + cis

plt.figure(figsize=(12, 6))
plt.plot(ns, running_means, label='Cumulative Mean Infection Rate', color='#1f77b4', linewidth=2)
plt.fill_between(ns, lower_bound, upper_bound, color='#1f77b4', alpha=0.2, label='95% Confidence Interval')

for step in [100, 500, 1000, 2000]:
    if step <= MAX_N:
        plt.axvline(x=step, color='gray', linestyle='--', alpha=0.5)
        plt.text(step, running_means[step - 1], f' N={step}\n {running_means[step - 1]:.3f}',
                 verticalalignment='bottom', fontsize=9)

plt.xlabel('Number of Scenarios (N)', fontsize=12)
plt.ylabel('Average Infection Rate', fontsize=12)
plt.title('Sensitivity Analysis of N_SCENARIOS: Convergence Test', fontsize=14)
plt.legend()
plt.grid(True, linestyle=':', alpha=0.6)
plt.tight_layout()

plt.savefig('n_scenarios_sensitivity.tiff', dpi=300, format='tiff', bbox_inches='tight')
print(f"图表已保存为 n_scenarios_sensitivity.tiff")
print(f"最终 N={MAX_N} 时的平均感染率: {running_means[-1]:.4f} (95% CI: {lower_bound[-1]:.4f} - {upper_bound[-1]:.4f})")
plt.show()