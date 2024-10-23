from gurobipy import Model, GRB, quicksum
import pandas as pd
from data import get_supplier_data, experimental_scenarios


def create_model(data):
    # Extract supplier data as separate arrays
    months, chromium_content, nickel_content, max_supply, procurement_costs, \
        chromium_content_ratio, nickel_content_ratio, \
        demand, storage_costs, max_production, num_product, num_supplier = get_supplier_data(data)

    # Create a mathematical model in matrix form
    model = Model("Steel Production")

    # Variables: Create decision variables for production, storage, and scrap amounts
    P = model.addVars(num_product, months, vtype=GRB.CONTINUOUS, name="P")
    S = model.addVars(num_product, months, vtype=GRB.CONTINUOUS, name="S")
    X = model.addVars(num_product, num_supplier, months, vtype=GRB.CONTINUOUS, name="X")

    # Objective function: Minimize total cost (procurement + storage)
    model.setObjective(
        quicksum(
            procurement_costs[j] * X[i, j, t] for i in range(num_product) for j in range(num_supplier) for t in range(months)) +
        quicksum(storage_costs[i] * S[i, t] for i in range(num_product) for t in range(months)),
        GRB.MINIMIZE
    )

    # Constraints
    for t in range(months):
        # Demand satisfaction constraints
        if t == 0:
            for i in range(num_product):
                model.addConstr(P[i, t] == demand[i, t] + S[i, t])
        else:
            for i in range(num_product):
                model.addConstr(P[i, t] + S[i, t - 1] == demand[i, t] + S[i, t])

        # Production capacity constraint
        model.addConstr(quicksum(P[i, t] for i in range(num_product)) <= max_production)

        # Supply limits constraints
        for j in range(num_supplier):
            model.addConstr(quicksum(X[i, j, t] for i in range(num_product)) <= max_supply[j])

        # Supply-production balance
        for i in range(num_product):
            model.addConstr(P[i, t] == quicksum(X[i, j, t] for j in range(num_supplier)))

        # Chromium content constraint
        for i in range(num_product):
            model.addConstr(
                chromium_content_ratio[i] * P[i, t] == quicksum(
                    chromium_content[j] * X[i, j, t] for j in range(num_supplier))
            )

        # Nickel content constraint
        for i in range(num_product):
            model.addConstr(
                nickel_content_ratio[i] * P[i, t] == quicksum(
                    nickel_content[j] * X[i, j, t] for j in range(num_supplier))
            )

    return model, P, S, X, num_product, num_supplier, months, storage_costs, procurement_costs


def run_experiments():
    results = []

    for scenario in experimental_scenarios:
        model, P, S, X, num_product, num_supplier, months, storage_costs, procurement_costs = create_model(scenario)
        model.optimize()

        if model.status == GRB.OPTIMAL:
            total_production = sum(P[i, t].x for i in range(num_product) for t in range(months))
            total_storage = sum(S[i, t].x for i in range(num_product) for t in range(months))
            total_procurement = sum(
                X[i, j, t].x for i in range(num_product) for j in range(num_supplier) for t in range(months))

            # Calculate total storage cost
            total_storage_cost = sum(storage_costs[i] * S[i, t].x for i in range(num_product) for t in range(months))

            # Calculate total procurement cost
            total_procurement_cost = sum(
                procurement_costs[j] * X[i, j, t].x for i in range(num_product) for j in range(num_supplier) for t in range(months))

            results.append({
                'Max Production': scenario['max_production'],
                'Storage Costs': scenario['storage_costs'].tolist(),
                # Convert numpy array to list for Excel compatibility
                'Total Cost': model.objVal,
                'Total Production': total_production,
                'Total Storage': total_storage,
                'Total Procurement': total_procurement,
                'Total Storage Cost': total_storage_cost,
                'Total Procurement Cost': total_procurement_cost
            })
        else:
            results.append({
                'Max Production': scenario['max_production'],
                'Storage Costs': scenario['storage_costs'].tolist(),
                'Total Cost': 'No solution',
                'Total Production': 'N/A',
                'Total Storage': 'N/A',
                'Total Procurement': 'N/A',
                'Total Storage Cost': 'N/A',
                'Total Procurement Cost': 'N/A'
            })

    return pd.DataFrame(results)


# Run the experiments and save results
results_df = run_experiments()
results_df.to_excel('steel_production_experiment_results.xlsx', index=False)
print("Experiments completed. Results saved to 'steel_production_experiment_results.xlsx'.")