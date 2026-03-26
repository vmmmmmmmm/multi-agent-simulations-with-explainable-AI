# batch_run.py
import pandas as pd
import random
from tqdm import tqdm
from model import University

N_SCENARIOS = 1000
AGENT_COUNT = 1000
SIMULATION_MONTHS = 48

data_records = []

print(f"--- 开始批量仿真: 共 {N_SCENARIOS} 组场景 ---")

for i in tqdm(range(N_SCENARIOS)):
    rewire_prob = random.uniform(0.0, 0.2)
    avg_degree = random.randint(2, 10)
    condom_usage = random.uniform(0.0, 0.8)

    viral_load_impact = random.uniform(2.0, 5.0)
    clearance_1618 = random.uniform(0.03, 0.06)

    screen_compliance = random.uniform(0.3, 0.95)
    test_sensitivity = random.uniform(0.75, 0.99)
    treat_success = random.uniform(0.80, 0.90)

    start_year = random.choice([1, 2, 3])
    vax_female = random.uniform(0.0, 1.0)
    vax_male = random.uniform(0.0, 1.0)

    model = University(N=AGENT_COUNT, avg_degree=avg_degree, rewire_prob=rewire_prob)

    model.params.behavior.condom_usage_rate = condom_usage
    model.params.viral.viral_load_multiplier = viral_load_impact
    model.params.viral.clearance_rate_1618 = clearance_1618

    model.params.intervention.screening_compliance = screen_compliance
    model.params.intervention.test_sensitivity = test_sensitivity
    model.params.intervention.treatment_success_rate = treat_success
    model.params.intervention.screening_start_year = start_year

    # 修改为 model.agents
    for agent in model.agents:
        if agent.gender == 0 and random.random() < vax_female:
            agent.is_vaccinated = True
        elif agent.gender == 1 and random.random() < vax_male:
            agent.is_vaccinated = True

    for step in range(SIMULATION_MONTHS):
        model.step()

    # 修改为 model.agents
    final_infected = sum([1 for a in model.agents if a.hpv_status == 'infected'])
    infection_rate = final_infected / AGENT_COUNT

    record = {
        "Scenario_ID": i,
        "Rewire_Prob": rewire_prob,
        "Avg_Degree": avg_degree,
        "Condom_Usage": condom_usage,
        "Viral_Load_Impact": viral_load_impact,
        "Clearance_Rate_1618": clearance_1618,
        "Screening_Compliance": screen_compliance,
        "Test_Sensitivity": test_sensitivity,
        "Treatment_Success": treat_success,
        "Screening_Start_Year": start_year,
        "Vax_Cov_Female": vax_female,
        "Vax_Cov_Male": vax_male,
        "Infection_Rate": infection_rate
    }
    data_records.append(record)

df = pd.DataFrame(data_records)
file_name = f"simulation_data_{N_SCENARIOS}_runs.csv"
df.to_csv(file_name, index=False)
print(f"\n数据已保存至 {file_name}。现在您可以运行 analysis_shap.py 了！")