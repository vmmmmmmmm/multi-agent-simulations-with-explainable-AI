Generate Simulation Data
Run the batch simulation to generate the synthetic dataset (1,000 scenarios):

Note: This will output a CSV file named simulation_data_1000_runs.csv.

1. Run XAI Attribution
Train the XGBoost model and generate SHAP dependence and summary plots:

2. Evaluate Strategies & Cost-Effectiveness
Reproduce the epidemiological curves and cost-effectiveness analysis (Figures 1-3 in the manuscript):

3. Network Visualization & Sensitivity Analysis
To visualize the network rewiring process: python network_remake.py

To run the convergence test for the number of scenarios: python sensitivity_n_scenarios.py# multi-agent-simulations-with-explainable-AI
