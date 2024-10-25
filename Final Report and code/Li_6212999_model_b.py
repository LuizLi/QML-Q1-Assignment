from gurobipy import Model, GRB, quicksum
import numpy as np
import pandas as pd

# Data used in question b
data_b = {
    "months": 12,  # Number of months
    "storage_costs": np.array([20, 10, 5]),  # Storage costs for 18/10, 18/8, and 18/0
    "max_production": 100,  # Maximum production capacity per month
    "demand": {  # Demand for each type (18/10, 18/8, 18/0)
        "18_10": np.array([25, 25, 0, 0, 0, 50, 12, 0, 10, 10, 45, 99]),
        "18_8": np.array([10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10]),
        "18_0": np.array([5, 20, 80, 25, 50, 125, 150, 80, 40, 35, 3, 100]),
    },
    "suppliers": {
        "A": [0.18, 0.00, 0.00, 90, 5],
        "B": [0.25, 0.15, 0.04, 30, 10],
        "C": [0.15, 0.10, 0.02, 50, 9],
        "D": [0.14, 0.16, 0.05, 70, 7],
        "E": [0.00, 0.10, 0.03, 20, 8.5],
    },  # Supplier matrix
    "chromium_content_ratio": np.array([0.18, 0.18, 0.18]),  # Chromium content ratio
    "nickel_content_ratio": np.array([0.1, 0.08, 0]),  # Nickel content ratio
    "Product set": 3,  # Kinds of products
    "Supplier set": 5,  # Kinds of suppliers
}


# Define function to extract supplier data into separate matrices
def get_supplier_data(data):
    chromium_content = []
    nickel_content = []
    max_supply = []
    costs = []

    for supplier, params in data["suppliers"].items():
        chromium_content.append(params[0])
        nickel_content.append(params[1])
        max_supply.append(params[3])
        costs.append(params[4])

    return (
        data["months"],
        np.array(chromium_content),
        np.array(nickel_content),
        np.array(max_supply),
        np.array(costs),
        data["chromium_content_ratio"],
        data["nickel_content_ratio"],
        np.array([data["demand"]["18_10"], data["demand"]["18_8"], data["demand"]["18_0"]]),  # Demand for each type
        np.array(data["storage_costs"]),  # Storage costs for each type
        data["max_production"],  # Max production
        data["Product set"],
        data["Supplier set"],
    )


# Extract supplier data as separate arrays
months, chromium_content, nickel_content, max_supply, costs, \
    chromium_content_ratio, nickel_content_ratio, \
    demand, storage_costs, max_production, num_product, num_supplier = get_supplier_data(data_b)


# Create a mathematical model in matrix form
model = Model("Steel Production")

# Variables: Create decision variables for production, storage, and scrap amounts
P = model.addVars(num_product, months, vtype=GRB.CONTINUOUS, name="P")  # Production for each product
S = model.addVars(num_product, months, vtype=GRB.CONTINUOUS, name="S")  # Storage for each product
X = model.addVars(num_product, num_supplier, months, vtype=GRB.CONTINUOUS, name="X")  # Scrap amounts from suppliers

# Objective function: Minimize total cost (procurement + storage)
model.setObjective(
    quicksum(costs[j] * X[i, j, t] for i in range(num_product) for j in range(num_supplier) for t in range(months)) +
    quicksum(storage_costs[i] * S[i, t] for i in range(num_product) for t in range(months)),
    GRB.MINIMIZE
)

# Constraints
for t in range(months):
    # Demand satisfaction constraints: production + storage from last month = demand + current storage
    if t == 0:
        for i in range(num_product):
            model.addConstr(P[i, t] == demand[i, t] + S[i, t])  # No previous month storage in the first month
    else:
        for i in range(num_product):
            model.addConstr(P[i, t] + S[i, t - 1] == demand[i, t] + S[i, t])

    # Production capacity constraint
    model.addConstr(quicksum(P[i, t] for i in range(num_product)) <= max_production)

    # Supply limits constraints: scrap material from suppliers cannot exceed maximum supply
    for j in range(num_supplier):
        model.addConstr(quicksum(X[i, j, t] for i in range(num_product)) <= max_supply[j])

    # Supply-production balance: each production must equal total procurement from suppliers
    for i in range(num_product):
        model.addConstr(P[i, t] == quicksum(X[i, j, t] for j in range(num_supplier)))

    # Chromium content constraint: ensure the chromium content in products matches suppliers' material
    for i in range(num_product):
        model.addConstr(
            chromium_content_ratio[i] * P[i, t] == quicksum(chromium_content[j] * X[i, j, t] for j in range(num_supplier))
        )

    # Nickel content constraint: ensure the nickel content in products matches suppliers' material
    for i in range(num_product):
        model.addConstr(
            nickel_content_ratio[i] * P[i, t] == quicksum(nickel_content[j] * X[i, j, t] for j in range(num_supplier))
        )

# Non-negativity constraints are handled automatically by Gurobi (for continuous variables)


# Define print function
def display_results(model, months, P, S, X, num_products, num_suppliers):
    # Check if optimal solution found
    if model.status == GRB.OPTIMAL:
        production_data = []
        storage_data = []
        supplier_data = {i: [] for i in range(num_products)}  # Separate supplier data for each product

        print("\nMinimized cost: {:.2f} euro".format(model.objVal))

        for t in range(months):
            # Collect production and storage data (one table for all products)
            production_data.append({
                "Month": t + 1,
                "18/10 Production": P[0, t].x,
                "18/8 Production": P[1, t].x,
                "18/0 Production": P[2, t].x,
            })

            storage_data.append({
                "Month": t + 1,
                "18/10 Storage": S[0, t].x,
                "18/8 Storage": S[1, t].x,
                "18/0 Storage": S[2, t].x,
            })

            # Collect supplier data for each product separately
            for i in range(num_products):
                supplier_data_row = {"Month": t + 1}
                for j in range(num_suppliers):
                    supplier_data_row[f"From Supplier {chr(65 + j)}"] = X[i, j, t].x  # A, B, C, D, E
                supplier_data[i].append(supplier_data_row)

        # Set display options to avoid scientific notation and truncation
        pd.set_option('display.float_format', '{:.2f}'.format)
        pd.set_option('display.max_rows', None)  # Show all rows
        pd.set_option('display.max_columns', None)  # Show all columns

        # Convert production and storage data to DataFrames
        production_df = pd.DataFrame(production_data)
        storage_df = pd.DataFrame(storage_data)

        # Print production and storage results (shared across products)
        print("\nProduction Table:")
        print(production_df.to_string(index=False))

        print("\nStorage Table:")
        print(storage_df.to_string(index=False))

        # Print supplier procurement results for each product in separate tables
        for i in range(num_products):
            print(f"\nSupplier Procurement Table for Product {i + 1}:")
            supplier_df = pd.DataFrame(supplier_data[i])
            print(supplier_df.to_string(index=False))

    else:
        print("No optimal solution found.")


# Optimize the model
model.optimize()

# Display results using the function
display_results(model, months, P, S, X, num_product, num_supplier)

