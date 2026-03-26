# -*- codeing = utf-8 -*-
# @time :2026/1/29 20:19
# @author: vicm
# @file:network_remake.py
# @software:PyCharm

import matplotlib.pyplot as plt
import networkx as nx
import random

# --- 1. 设置模拟参数
N = 15              # 节点数
k = 4               # 平均度
p_rewire = 0.2      # 初始构建的小世界重连概率
breakup_prob = 0.15 # rewire_prob

# --- 2. 初始化网络
G = nx.watts_strogatz_graph(n=N, k=k, p=p_rewire, seed=42)
pos = nx.circular_layout(G)

# --- 3. 模拟 evolve_network 的逻辑并记录变化 ---
edges_original = list(G.edges())
edges_removed = []
edges_added = []

# 3.1 断边逻辑 (复制您的代码逻辑)
for u, v in edges_original:
    if random.random() < breakup_prob:
        edges_removed.append((u, v))

# 3.2 重连逻辑 (复制您的代码逻辑)
num_new = int(len(edges_original) * breakup_prob)
potential_new_edges = []
while len(edges_added) < num_new:
    u, v = random.sample(range(N), 2)
    if u != v and not G.has_edge(u, v) and (u, v) not in edges_added and (v, u) not in edges_added:
        if (u, v) not in edges_original and (v, u) not in edges_original: # 确保不是刚断开的边
             edges_added.append((u, v))

# --- 4. 绘图 ---
fig, axes = plt.subplots(1, 3, figsize=(18, 6))

# 通用绘图函数
def draw_base_nodes(ax, title):
    nx.draw_networkx_nodes(G, pos, node_color='lightblue', node_size=500, ax=ax, edgecolors='black')
    nx.draw_networkx_labels(G, pos, font_size=10, ax=ax)
    ax.set_title(title, fontsize=14, fontweight='bold')
    ax.axis('off')

# [图1] 原始状态 (Time t)
draw_base_nodes(axes[0], "State at Time $t$\n(Before Rewiring)")
nx.draw_networkx_edges(G, pos, edgelist=edges_original, edge_color='gray', width=1.5, ax=axes[0])

# [图2] 重组动态 (Dynamics)
draw_base_nodes(axes[1], "Rewiring Dynamics\n(Breakup & Formation)")
# 画保留的边
edges_kept = [e for e in edges_original if e not in edges_removed]
nx.draw_networkx_edges(G, pos, edgelist=edges_kept, edge_color='lightgray', width=1.0, alpha=0.5, ax=axes[1])
# 画断裂的边 (红色虚线)
nx.draw_networkx_edges(G, pos, edgelist=edges_removed, edge_color='red', width=2.0, style='dashed', ax=axes[1], label='Dissolved')
# 画新增的边 (绿色实线)
nx.draw_networkx_edges(G, pos, edgelist=edges_added, edge_color='green', width=2.5, ax=axes[1], label='Formed')
# 添加图例
axes[1].legend(['Nodes', 'Kept', 'Dissolved (Breakup)', 'New (Re-connect)'], loc='upper right', fontsize=9)

# [图3] 最终状态 (Time t+1)
draw_base_nodes(axes[2], "State at Time $t+1$\n(After Rewiring)")
# 构建新图的边列表
final_edges = edges_kept + edges_added
nx.draw_networkx_edges(G, pos, edgelist=final_edges, edge_color='gray', width=1.5, ax=axes[2])
# 可以高亮新边一下，让人看清楚
nx.draw_networkx_edges(G, pos, edgelist=edges_added, edge_color='green', width=1.5, ax=axes[2])

plt.tight_layout()
plt.savefig("Network_Dynamics.tiff", dpi=300, format='tiff', bbox_inches='tight')
plt.show()