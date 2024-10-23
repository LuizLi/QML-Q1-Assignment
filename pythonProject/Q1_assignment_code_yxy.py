import gurobipy as gp
from gurobipy import GRB

# ------------- 数据部分 -------------------
suppliers = ['A', 'B', 'C', 'D', 'E']
chromium_content = [18, 25, 15, 14, 0]  # 每个供应商的铬百分比
nickel_content = [0, 15, 10, 16, 10]    # 每个供应商的镍百分比
max_supply = [90, 30, 50, 70, 20]       # 每月最大供应量（kg）
cost_per_kg = [5, 10, 9, 7, 8.5]        # 每公斤成本（欧元）

# 月度需求
demand_18_10 = [25, 25, 0, 0, 0, 50, 12, 0, 10, 10, 45, 99]
demand_18_8 = [10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10]
demand_18_0 = [5, 20, 80, 25, 50, 125, 150, 80, 40, 35, 3, 100]

# 库存成本
holding_costs = [20, 10, 5]  # 18/10、18/8、18/0 的每公斤库存成本（欧元）

# 每月的总生产能力（kg）
production_capacity = 100  # kg

# 铬和镍的需求比例
chromium_req = [18, 18, 18]  # 18/10、18/8 和 18/0
nickel_req = [10, 8, 0]      # 18/10、18/8 和 18/0

# 创建模型
model = gp.Model("stainless_steel_production")

n_suppliers = len(suppliers)
n_months = len(demand_18_10)
n_products = 3  # 18/10、18/8、18/0

# 决策变量：连续变量而非整数
x = model.addVars(n_suppliers, n_products, n_months, lb=0, vtype=GRB.CONTINUOUS, name="x")  
production = model.addVars(n_products, n_months, lb=0, vtype=GRB.CONTINUOUS, name="production")
inventory = model.addVars(n_products, n_months, lb=0, vtype=GRB.CONTINUOUS, name="inventory")

# 目标函数：最小化材料和库存成本
material_cost = gp.quicksum(cost_per_kg[i] * x[i, j, t] for i in range(n_suppliers) for j in range(n_products) for t in range(n_months))
holding_cost = gp.quicksum(holding_costs[j] * inventory[j, t] for j in range(n_products) for t in range(n_months))

model.setObjective(material_cost + holding_cost, GRB.MINIMIZE)

# 约束条件
for t in range(n_months):
    for j in range(n_products):
        # 确保铬和镍比例要求得到满足
        model.addConstr(gp.quicksum(chromium_content[i] * x[i, j, t] for i in range(n_suppliers)) == chromium_req[j] * production[j, t], f"chromium_{j}_{t}")
        model.addConstr(gp.quicksum(nickel_content[i] * x[i, j, t] for i in range(n_suppliers)) == nickel_req[j] * production[j, t], f"nickel_{j}_{t}")
        
        # 第一个月：库存为0，生产需要满足所有产品的需求
        if t == 0:
            model.addConstr(production[0, t] == demand_18_10[t] + inventory[0, t], f"initial_demand_18_10_{t}")
            model.addConstr(production[1, t] == demand_18_8[t] + inventory[1, t], f"initial_demand_18_8_{t}")
            model.addConstr(production[2, t] == demand_18_0[t] + inventory[2, t], f"initial_demand_18_0_{t}")
            # model.addConstr(inventory[j, t] == 0, f"inventory_initial_{j}_{t}")  # 第一个月的库存设置为0
        else:
            # 当前月的库存 = 上个月的库存 + 本月生产 - 本月各产品的需求
            model.addConstr(inventory[0, t] == inventory[0, t-1] + production[0, t] - demand_18_10[t], f"inventory_balance_18_10_{t}")
            model.addConstr(inventory[1, t] == inventory[1, t-1] + production[1, t] - demand_18_8[t], f"inventory_balance_18_8_{t}")
            model.addConstr(inventory[2, t] == inventory[2, t-1] + production[2, t] - demand_18_0[t], f"inventory_balance_18_0_{t}")

# 每月的生产总量不能超过100kg
for t in range(n_months):
    model.addConstr(gp.quicksum(production[j, t] for j in range(n_products)) <= production_capacity, f"capacity_{t}")

# 每月供应商的最大供应限制
for t in range(n_months):
    for i in range(n_suppliers):
        model.addConstr(gp.quicksum(x[i, j, t] for j in range(n_products)) <= max_supply[i], f"supply_{i}_{t}")

# 添加一个约束，确保每个月购买的废料总重量等于生产的产品重量
for t in range(n_months):
    model.addConstr(gp.quicksum(x[i, j, t] for i in range(n_suppliers) for j in range(n_products)) == gp.quicksum(production[j, t] for j in range(n_products)), f"material_balance_{t}")

# 优化模型
model.optimize()

# 输出结果
if model.status == GRB.OPTIMAL:
    print(f"最优成本: {model.ObjVal}")
    print("生产计划：")
    for t in range(n_months):
        for j in range(n_products):
            print(f"第 {t+1} 个月，产品 {j+1}： {production[j, t].X} kg")
    
    print("\n每个月从每个供应商处购买的废料量：")
    for t in range(n_months):
        print(f"\n第 {t+1} 个月：")
        for i in range(n_suppliers):
            total_material_from_supplier = sum(x[i, j, t].X for j in range(n_products))
            print(f"供应商 {suppliers[i]}: {total_material_from_supplier} kg")
else:
    print("未找到最优解。")
