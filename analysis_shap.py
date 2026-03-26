# -*- codeing = utf-8 -*-
import pandas as pd
import xgboost as xgb
import shap
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.metrics import r2_score, mean_squared_error
import os
import numpy as np

# ---------------------------------------------------------
# 1. 数据加载与预处理
# ---------------------------------------------------------
# 同步文件名为 1000 次结果
csv_file = "simulation_data_1000_runs.csv"

if not os.path.exists(csv_file):
    raise FileNotFoundError(f"找不到文件 {csv_file}。请先运行 batch_run.py 生成数据。")

df = pd.read_csv(csv_file)
print(f"成功读取数据，共 {len(df)} 条记录。")

features = [
    "Rewire_Prob", "Avg_Degree", "Condom_Usage",
    "Viral_Load_Impact", "Clearance_Rate_1618",
    "Screening_Compliance", "Test_Sensitivity", "Treatment_Success",
    "Screening_Start_Year", "Vax_Cov_Female", "Vax_Cov_Male"
]

target = "Infection_Rate"

X = df[features]
y = df[target]

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# ---------------------------------------------------------
# 2. 训练 XGBoost 模型
# ---------------------------------------------------------
print("正在训练 XGBoost 模型...")
model = xgb.XGBRegressor(
    n_estimators=500, learning_rate=0.05, max_depth=6, random_state=42, n_jobs=-1
)
model.fit(X_train, y_train)

# ---------------------------------------------------------
# 3. 模型性能评估
# ---------------------------------------------------------
y_pred = model.predict(X_test)
r2 = r2_score(y_test, y_pred)
rmse = np.sqrt(mean_squared_error(y_test, y_pred))

print("-" * 30)
print(f"R² Score: {r2:.4f}")
print(f"RMSE: {rmse:.4f}")
print("-" * 30)

# ---------------------------------------------------------
# 4. SHAP 归因分析
# ---------------------------------------------------------
print("正在计算 SHAP 值...")
explainer = shap.TreeExplainer(model)
shap_values = explainer(X)

plt.figure(figsize=(10, 6))
shap.plots.bar(shap_values, max_display=12, show=False)
plt.title("Feature Importance Ranking (Mean |SHAP|)", fontsize=16)
plt.tight_layout()
plt.savefig("Feature_Importance_Ranking.tiff", dpi=300, format='tiff', bbox_inches='tight')
plt.show()

plt.figure(figsize=(12, 8))
shap.plots.beeswarm(shap_values, max_display=12, show=False)
plt.title("SHAP Summary: Directional Impact", fontsize=16)
plt.tight_layout()
plt.savefig("SHAP_Summary_Directional.tiff", dpi=300, format='tiff', bbox_inches='tight')
plt.show()

feature_to_plot = "Screening_Compliance"
print(f"正在绘制 {feature_to_plot} 的依赖图...")
plt.figure(figsize=(10, 6))
try:
    shap.plots.scatter(shap_values[:, feature_to_plot], color=shap_values, show=False)
except:
    shap.plots.scatter(shap_values[:, feature_to_plot], show=False)
plt.title(f"Dependence Plot: {feature_to_plot}", fontsize=16)
plt.tight_layout()
plt.savefig("Dependence_Plot_Compliance.tiff", dpi=300, format='tiff', bbox_inches='tight')
plt.show()

feature_to_plot_2 = "Viral_Load_Impact"
print(f"正在绘制 {feature_to_plot_2} 的依赖图...")
plt.figure(figsize=(10, 6))
shap.plots.scatter(shap_values[:, feature_to_plot_2], color=shap_values, show=False)
plt.title(f"Dependence Plot: {feature_to_plot_2}", fontsize=16)
plt.tight_layout()
plt.savefig("Dependence_Plot_ViralLoad.tiff", dpi=300, format='tiff', bbox_inches='tight')
plt.show()