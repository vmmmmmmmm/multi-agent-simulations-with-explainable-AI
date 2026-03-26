# model.py
from mesa import Model
from mesa.space import NetworkGrid
from mesa.datacollection import DataCollector
import networkx as nx
import random
from parameters import GlobalConfig
from agent import Student


class University(Model):
    def __init__(self, N, avg_degree=6, rewire_prob=0.1):
        super().__init__()
        self.params = GlobalConfig()
        self.num_agents = N
        self.rewire_prob = rewire_prob
        self.steps = 0

        # 修复点：确保在这里先初始化 self.G 和 self.grid
        # 1. 网络构建 (Nodes 必须是整数 0..N-1)
        self.G = nx.watts_strogatz_graph(n=self.num_agents, k=avg_degree, p=rewire_prob)
        self.grid = NetworkGrid(self.G)

        # 2. 创建 Agents (循环遍历刚刚创建好的 self.G)
        for node in self.G.nodes():
            # 修复点：传入 node 作为 unique_id
            a = Student(node, self)
            a.init_compliance()
            self.grid.place_agent(a, node)

        # 3. 初始感染
        self.seed_infection()

        # 4. 数据收集
        self.datacollector = DataCollector(
            model_reporters={
                "Infected_Rate": lambda m: sum(
                    [1 for a in m.agents if a.hpv_status == 'infected']) / m.num_agents
            }
        )

    def seed_infection(self):
        agents_list = list(self.agents)
        initial_infected = self.random.sample(agents_list, 10)
        for p in initial_infected:
            p.become_infected(self.assign_viral_type())

    def assign_viral_type(self):
        dist = self.params.viral.genotype_distribution_scc
        return random.choices(list(dist.keys()), weights=list(dist.values()), k=1)[0]

    def step(self):
        self.datacollector.collect(self)
        self.evolve_network()
        self.agents.shuffle().do("step")
        self.steps += 1

    def evolve_network(self):
        breakup_prob = self.rewire_prob
        edges = list(self.G.edges())

        for u, v in edges:
            if random.random() < breakup_prob:
                self.G.remove_edge(u, v)

        num_new = int(len(edges) * breakup_prob)
        for _ in range(num_new):
            u, v = random.sample(range(self.num_agents), 2)
            if u != v and not self.G.has_edge(u, v):
                self.G.add_edge(u, v)