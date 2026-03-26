# plot_proofs.py
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
from model import University
from tqdm import tqdm

# ==========================================
# 样式设置
# ==========================================
plt.style.use('seaborn-v0_8')
# 适配中文和负号显示。若您使用 Windows 系统，请将 'Arial Unicode MS' 替换为 'SimHei'
plt.rcParams['font.sans-serif'] = ['Arial Unicode MS']
plt.rcParams['axes.unicode_minus'] = False


def run_simulation(strategy_name, params, steps=48):
    # 1. 初始化模型
    model = University(N=1000, avg_degree=6, rewire_prob=params.get('rewire', 0.1))

    # 2. 设置模型参数
    model.params.viral.viral_load_multiplier = 2.0
    model.params.intervention.screening_compliance = params.get('compliance', 0)
    model.params.intervention.test_sensitivity = params.get('sensitivity', 0)
    model.params.intervention.treatment_success_rate = 0.85

    if 'condom_usage' in params:
        model.params.behavior.condom_usage_rate = params['condom_usage']

    # 3. 初始化智能体 (疫苗接种)
    for a in model.agents:
        a.init_compliance()
        if a.gender == 0 and np.random.random() < params.get('vax_female', 0):
            a.is_vaccinated = True
        elif a.gender == 1 and np.random.random() < params.get('vax_male', 0):
            a.is_vaccinated = True

    time_series = []

    # 4. 运行仿真步
    for _ in range(steps):
        model.step()
        inf_count = sum([1 for a in model.agents if a.hpv_status == 'infected'])
        time_series.append(inf_count / 1000)

    final_rate = time_series[-1]

    # ==========================================
    # 5. 成本计算模块 (与论文公式严格对应)
    # ==========================================
    cost = 0
    N_total = 1000

    # 提取成本参数 (若未提供则使用默认值0)
    c_test = params.get('c_test', 0)
    c_treat = params.get('c_treat', 0)
    c_prevent = params.get('c_prevent', 0)
    c_fixed = params.get('c_fixed', 0)

    # 成本项1: 疫苗接种成本 (假设单价1000)
    n_vax = sum([1 for a in model.agents if a.is_vaccinated])
    cost += n_vax * 1000

    # 成本项2: 筛查成本 (N_screen,t * c_test)
    # 每年筛查一次，计算总筛查人次
    years = steps // 12
    n_screen_per_year = N_total * params.get('compliance', 0)
    total_screen_count = n_screen_per_year * years
    cost += total_screen_count * c_test

    # 成本项3: 治疗干预成本 (N_treat,t * c_treat)
    # 估算总治疗人数 = 总筛查人次 * 仿真期间平均感染率 * 试剂灵敏度
    avg_inf_rate = np.mean(time_series)
    expected_treatments = total_screen_count * avg_inf_rate * params.get('sensitivity', 0)
    cost += expected_treatments * c_treat

    # 成本项4: 预防物资/靶向干预成本 (N_target,t * c_prevent)
    # 估算使用安全套/接受干预的群体，每月发生成本
    n_target = N_total * params.get('condom_usage', 0)
    cost += n_target * steps * c_prevent

    # 成本项5: 固定管理成本 (C_fixed)
    # 只要存在任何主动干预(筛查、额外物资发放、疫苗)，就计入固定成本 (大于默认的0.2才算额外干预)
    if params.get('compliance', 0) > 0 or params.get('condom_usage', 0) > 0.2 or n_vax > 0:
        cost += c_fixed

    return time_series, final_rate, cost


# ==========================================
# 绘图 1：动态传播时序图
# ==========================================
print("正在生成图表 1: 动态传播时序图...")
plt.figure(figsize=(10, 6))

# Static 与 Dynamic 策略，全设成本参数为0以作为基线
baseline_params = {'rewire': 0.0, 'compliance': 0, 'sensitivity': 0, 'vax_female': 0, 'vax_male': 0,
                   'condom_usage': 0.2}

ts_static_list = []
for _ in range(10):
    ts, _, _ = run_simulation("Static", baseline_params)
    ts_static_list.append(ts)
avg_static = np.mean(ts_static_list, axis=0)

baseline_params['rewire'] = 0.1
ts_dynamic_list = []
for _ in range(10):
    ts, _, _ = run_simulation("Dynamic", baseline_params)
    ts_dynamic_list.append(ts)
avg_dynamic = np.mean(ts_dynamic_list, axis=0)

plt.plot(avg_static, label='Static Network (Stable)', linestyle='--', color='blue')
plt.plot(avg_dynamic, label='Dynamic Network (Rewiring)', color='red', linewidth=2)
plt.title("Impact of Network Dynamics on HPV Spread", fontsize=14)
plt.xlabel("Month")
plt.ylabel("Infection Rate")
plt.legend()
plt.tight_layout()
plt.savefig("Figure1_Epidemic_Curve.tiff", dpi=300, format='tiff', bbox_inches='tight')
plt.close()

# ==========================================
# 策略对比蒙特卡洛实验
# ==========================================
print("正在运行策略对比实验 (跑50次蒙特卡洛，可能需要一两分钟)...")

data = []

# 三组对比策略定义
strategies = {
    "A: Baseline (No Intervention)": {
        'rewire': 0.1,
        'compliance': 0.0,
        'sensitivity': 0.0,
        'vax_female': 0.0,
        'vax_male': 0.0,
        'condom_usage': 0.2,
        'c_test': 0,
        'c_treat': 0,
        'c_prevent': 0,
        'c_fixed': 0
    },

    "B: Traditional Clinic Screening": {
        'rewire': 0.1,
        'compliance': 0.40,  # 较低的依从性
        'sensitivity': 0.85,  # 常规灵敏度
        'vax_female': 0.30,
        'vax_male': 0.10,
        'condom_usage': 0.30,
        'c_test': 250,  # 较高的临床筛查单价
        'c_treat': 800,
        'c_prevent': 0,
        'c_fixed': 100000  # 较高的医院端培训固定成本
    },

    "C: Urine Self-test (Targeted)": {
        'rewire': 0.1,
        'compliance': 0.85,  # 极高的依从性
        'sensitivity': 0.96,  # 极高灵敏度
        'vax_female': 0.50,
        'vax_male': 0.30,
        'condom_usage': 0.65,  # 靶向干预
        'c_test': 150,  # 较低的自检单价
        'c_treat': 800,
        'c_prevent': 50,  # 靶向物资单价
        'c_fixed': 50000  # 较低的自检物流体系固定成本
    }
}

for name, params in strategies.items():
    print(f"[{name}] 模拟进度:")
    for i in tqdm(range(50)):
        _, rate, cost = run_simulation(name, params)
        data.append({
            "Strategy": name,
            "Infection_Rate": rate,
            "Total_Cost": cost
        })

df_res = pd.DataFrame(data)

# ==========================================
# 绘图 2：最终感染率箱线图
# ==========================================
plt.figure(figsize=(10, 6))
# 画箱线图主体
sns.boxplot(x="Strategy", y="Infection_Rate", data=df_res, palette="Set2")
# 添加底层散点，体现实验数据量(更具学术说服力)
sns.stripplot(x="Strategy", y="Infection_Rate", data=df_res, color=".3", alpha=0.5, size=5)

plt.title("Comparison of Intervention Strategies on Final Infection Rate", fontsize=14)
plt.ylabel("Final Infection Rate")
plt.xlabel("")
plt.tight_layout()
plt.savefig("Figure2_Strategy_Boxplot.tiff", dpi=300, format='tiff', bbox_inches='tight')
plt.close()

# ==========================================
# 绘图 3：成本效益散点图
# ==========================================
plt.figure(figsize=(10, 6))
sns.scatterplot(x="Total_Cost", y="Infection_Rate", hue="Strategy", style="Strategy",
                data=df_res, s=120, alpha=0.75, palette="Set1")
plt.title("Cost-Effectiveness Analysis of Different Interventions", fontsize=14)
plt.xlabel("Total Cost (RMB)")
plt.ylabel("Final Infection Rate (Lower is Better)")
plt.grid(True, linestyle='--', alpha=0.6)
plt.tight_layout()
plt.savefig("Figure3_Cost_Benefit.tiff", dpi=300, format='tiff', bbox_inches='tight')
plt.close()

print("\n全部图表已生成完毕，并以高分辨率 (300dpi) 保存至当前目录:")
print(" - Figure1_Epidemic_Curve.tiff")
print(" - Figure2_Strategy_Boxplot.tiff")
print(" - Figure3_Cost_Benefit.tiff")