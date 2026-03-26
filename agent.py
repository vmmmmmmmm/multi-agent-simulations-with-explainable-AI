# agent.py
from mesa import Agent
import random


class Student(Agent):
    def __init__(self, unique_id, model):
        # 修复点：添加 unique_id 并传递给父类
        super().__init__(unique_id, model)

        self.hpv_status = 'susceptible'
        self.hpv_type = None
        self.is_vaccinated = False
        self.diagnosis_result = None

        self.gender = 0 if self.random.random() < 0.5 else 1
        self.is_high_viral_load = False
        self.willing_to_screen = False

    def init_compliance(self):
        if self.random.random() < self.model.params.intervention.screening_compliance:
            self.willing_to_screen = True
        else:
            self.willing_to_screen = False

    def step(self):
        self.contact_dynamics()
        self.check_external_infection()
        if self.hpv_status == 'infected':
            self.natural_clearance()
        self.try_screening()

    def check_external_infection(self):
        if self.hpv_status == 'susceptible':
            if self.random.random() < self.model.params.viral.external_infection_prob:
                self.become_infected(self.model.assign_viral_type())

    def contact_dynamics(self):
        neighbors = self.model.grid.get_neighbors(self.pos, include_center=False)
        if not neighbors:
            return

        chosen_target = self.random.choice(neighbors)
        partner = None

        if isinstance(chosen_target, Agent):
            partner = chosen_target
        else:
            cell_contents = self.model.grid.get_cell_list_contents([chosen_target])
            if cell_contents:
                partner = cell_contents[0]

        if partner is None:
            return

        if partner.hpv_status == 'infected':
            self.try_infection(partner)

    def try_infection(self, partner):
        virus_type = partner.hpv_type
        trans_prob = self.model.params.viral.beta_f if self.gender == 0 else self.model.params.viral.beta_m

        if partner.is_high_viral_load:
            trans_prob *= self.model.params.viral.viral_load_multiplier

        if self.random.random() < self.model.params.behavior.condom_usage_rate:
            trans_prob *= (1 - 0.85)

        if self.is_vaccinated:
            efficacy = self.model.params.intervention.vaccine_efficacy_2v.get(virus_type, 0.0)
            trans_prob *= (1 - efficacy)

        if self.random.random() < trans_prob:
            self.become_infected(virus_type)

    def become_infected(self, virus_type):
        self.hpv_status = 'infected'
        self.hpv_type = virus_type
        self.is_high_viral_load = True if self.random.random() < 0.3 else False

    def natural_clearance(self):
        if self.hpv_type in ['16', '18']:
            rate = self.model.params.viral.clearance_rate_1618
        else:
            rate = self.model.params.viral.clearance_rate_other

        if self.random.random() < rate:
            self.hpv_status = 'susceptible'
            self.hpv_type = None
            self.is_high_viral_load = False

    def try_screening(self):
        # 使用自定义的 self.model.steps 获取当前时间步
        current_year = (self.model.steps // 12) + 1
        start_year = self.model.params.intervention.screening_start_year
        if current_year < start_year:
            return

        if self.model.steps % 12 != 0:
            return

        if not self.willing_to_screen:
            return

        if self.hpv_status == 'infected':
            sensitivity = self.model.params.intervention.test_sensitivity
            if self.random.random() < sensitivity:
                self.diagnosis_result = 'positive'
                self.receive_treatment()
            else:
                self.diagnosis_result = 'negative'

    def receive_treatment(self):
        success_rate = self.model.params.intervention.treatment_success_rate
        if self.random.random() < success_rate:
            self.hpv_status = 'susceptible'
            self.hpv_type = None
            self.is_high_viral_load = False