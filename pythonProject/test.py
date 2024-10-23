from gurobipy import Model, GRB, quicksum
import numpy as np
import pandas as pd
# from data import get_supplier_data, data_b
# from data import get_supplier_data, data_exp
from data import get_supplier_data, data_c1
# from data import get_supplier_data, data_c2
# from data import get_supplier_data, data_c3




# Extract supplier data as separate arrays
months, chromium_content, nickel_content, max_supply, costs, \
    chromium_content_ratio, nickel_content_ratio, \
    demand, storage_costs, max_production, num_product, num_supplier = get_supplier_data(data_c1)

nickel_content_ratio_1, nickel_content_ratio_2 = 0, 0
chromium_content_ratio = 0.18
nickel_content_ratio_3 = 0


# Create a mathematical model in matrix form
model = Model("Steel Production")

# Variables: Create decision variables for production, storage, and scrap amounts
P = model.addVars(3, months, vtype=GRB.CONTINUOUS, name="P")  # Production for 18/10, 18/8, 18/0
S = model.addVars(3, months, vtype=GRB.CONTINUOUS, name="S")  # Storage for 18/10, 18/8, 18/0
X = model.addVars(5, months, vtype=GRB.CONTINUOUS, name="X")  # Scrap amounts from suppliers A, B, C, D, E

# Objective function: Minimize total cost (procurement + storage)
model.setObjective(
    quicksum(costs[i] * X[i, t] for i in range(num_supplier) for t in range(months)) +
    quicksum(storage_costs[j] * S[j, t] for j in range(num_product) for t in range(months)),
    GRB.MINIMIZE
)

# Constraints
for t in range(months):
    # Demand satisfaction constraints
    if t == 0:
        model.addConstr(P[0, t] == demand[0, t] + S[0, t])  # No storage from previous month for 18/10
        model.addConstr(P[1, t] == demand[1, t] + S[1, t])  # No storage from previous month for 18/8
        model.addConstr(P[2, t] == demand[2, t] + S[2, t])  # No storage from previous month for 18/0
    else:
        model.addConstr(P[0, t] + S[0, t - 1] == demand[0, t] + S[0, t])
        model.addConstr(P[1, t] + S[1, t - 1] == demand[1, t] + S[1, t])
        model.addConstr(P[2, t] + S[2, t - 1] == demand[2, t] + S[2, t])

    # Production capacity constraint
    model.addConstr(quicksum(P[j, t] for j in range(num_product)) <= max_production)

    # Supply limits constraints
    for i in range(num_supplier):
        model.addConstr(X[i, t] <= max_supply[i])

    # Supply-production balance
    model.addConstr(quicksum(X[i, t] for i in range(num_supplier)) \
                    == quicksum(P[j, t] for j in range(num_product)))

    # Chromium content constraint
    model.addConstr(
        chromium_content_ratio * (P[0, t] + P[1, t]) + 0.8*P[2, t] ==
        quicksum(chromium_content[i] * X[i, t] for i in range(num_supplier))
    )

    # Nickel content constraint
    model.addConstr(
        nickel_content_ratio_1 * P[0, t] + nickel_content_ratio_2 * P[1, t] + nickel_content_ratio_3 * P[2, t] ==
        quicksum(nickel_content[i] * X[i, t] for i in range(1, num_supplier))
    )

# Non-negativity constraints are handled automatically by Gurobi (for continuous variables)

# Define print function
def display_results(model, months, P, S, X):
    # Check if optimal solution found
    if model.status == GRB.OPTIMAL:
        production_data = []
        storage_data = []
        supplier_data = []

        print("\nMinimized cost: {:.2f} euro".format(model.objVal))

        for t in range(months):
            # Collect production data
            production_data.append({
                "Month": t + 1,
                "18/10 Production": P[0, t].x,
                "18/8 Production": P[1, t].x,
                "18/0 Production": P[2, t].x,
            })

            # Collect storage data
            storage_data.append({
                "Month": t + 1,
                "18/10 Storage": S[0, t].x,
                "18/8 Storage": S[1, t].x,
                "18/0 Storage": S[2, t].x,
            })

            # Collect supplier data
            supplier_data.append({
                "Month": t + 1,
                "From A": X[0, t].x,
                "From B": X[1, t].x,
                "From C": X[2, t].x,
                "From D": X[3, t].x,
                "From E": X[4, t].x,
            })

        # Set display options to avoid scientific notation and truncation
        pd.set_option('display.float_format', '{:.2f}'.format)
        pd.set_option('display.max_rows', None)  # Show all rows
        pd.set_option('display.max_columns', None)  # Show all columns

        # Convert collected data to DataFrames
        production_df = pd.DataFrame(production_data)
        storage_df = pd.DataFrame(storage_data)
        supplier_df = pd.DataFrame(supplier_data)

        # Print results
        print("\nProduction Table:")
        print(production_df.to_string(index=False))

        print("\nStorage Table:")
        print(storage_df.to_string(index=False))

        print("\nSupplier Procurement Table:")
        print(supplier_df.to_string(index=False))
    else:
        print("No optimal solution found.")

# Optimize the model
model.optimize()

# Display results using the function
display_results(model, months, P, S, X)