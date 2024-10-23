from gurobipy import Model, GRB, quicksum
import numpy as np
import pandas as pd

# Input data dictionary
data_e = {
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
    "copper_limit": 0,  # Copper content limit
    "electrolysis_fixed_cost": 100,  # Fixed cost for electrolysis
    "electrolysis_unit_cost": 5,  # Unit cost for electrolysis
}

def get_supplier_data_e(data):
    chromium_content = []
    nickel_content = []
    copper_content = []
    max_supply = []
    costs = []

    for supplier, params in data["suppliers"].items():
        chromium_content.append(params[0])
        nickel_content.append(params[1])
        copper_content.append(params[2])
        max_supply.append(params[3])
        costs.append(params[4])

    return (
        data["months"],
        np.array(chromium_content),
        np.array(nickel_content),
        np.array(copper_content),
        np.array(max_supply),
        np.array(costs),
        data["chromium_content_ratio"],
        data["nickel_content_ratio"],
        data["copper_limit"],
        np.array([data["demand"]["18_10"], data["demand"]["18_8"], data["demand"]["18_0"]]),
        np.array(data["storage_costs"]),
        data["max_production"],
        data["electrolysis_fixed_cost"],
        data["electrolysis_unit_cost"],
        data["Product set"],
        data["Supplier set"],
    )

def calculate_detailed_costs(model, months, P, S, X, B, m, storage_costs, electrolysis_fixed_cost, 
                           electrolysis_unit_cost, supplier_costs, num_products, num_suppliers):
    """
    Calculate detailed breakdown of costs from the optimal solution
    """
    # Storage costs calculation
    storage_cost_details = []
    total_storage_cost = 0
    
    for t in range(months):
        month_storage_cost = sum(storage_costs[i] * S[i, t].x for i in range(num_products))
        total_storage_cost += month_storage_cost
        storage_cost_details.append({
            "Month": t + 1,
            "18/10 Storage Cost": storage_costs[0] * S[0, t].x,
            "18/8 Storage Cost": storage_costs[1] * S[1, t].x,
            "18/0 Storage Cost": storage_costs[2] * S[2, t].x,
            "Total Storage Cost": month_storage_cost
        })
    
    # Electrolysis costs calculation
    electrolysis_cost_details = []
    total_electrolysis_cost = 0
    
    for t in range(months):
        fixed_cost = electrolysis_fixed_cost * B[t].x
        variable_cost = sum(electrolysis_unit_cost * m[i, t].x for i in range(num_products))
        month_total = fixed_cost + variable_cost
        total_electrolysis_cost += month_total
        
        electrolysis_cost_details.append({
            "Month": t + 1,
            "Fixed Cost": fixed_cost,
            "Variable Cost": variable_cost,
            "Total Electrolysis Cost": month_total
        })
    
    # Procurement costs calculation
    procurement_cost = sum(supplier_costs[j] * X[i, j, t].x 
                         for i in range(num_products) 
                         for j in range(num_suppliers) 
                         for t in range(months))
    
    return {
        "storage_costs": storage_cost_details,
        "electrolysis_costs": electrolysis_cost_details,
        "total_storage_cost": total_storage_cost,
        "total_electrolysis_cost": total_electrolysis_cost,
        "total_procurement_cost": procurement_cost
    }

def display_optimal_plans(model, months, P, S, X, B, m, num_products, num_suppliers, storage_costs,
                         electrolysis_fixed_cost, electrolysis_unit_cost, supplier_costs):
    """
    Display the optimal production, storage, electrolysis and procurement plans with detailed costs
    """
    if model.status == GRB.OPTIMAL:
        # Calculate detailed costs
        cost_details = calculate_detailed_costs(
            model, months, P, S, X, B, m, storage_costs, 
            electrolysis_fixed_cost, electrolysis_unit_cost, 
            supplier_costs, num_products, num_suppliers
        )
        
        print(f"\nTotal Cost: {model.objVal:.2f} euro")
        print(f"Breakdown:")
        print(f"- Total Storage Cost: {cost_details['total_storage_cost']:.2f} euro")
        print(f"- Total Electrolysis Cost: {cost_details['total_electrolysis_cost']:.2f} euro")
        print(f"- Total Procurement Cost: {cost_details['total_procurement_cost']:.2f} euro")
        
        # Display storage costs by month
        print("\nMonthly Storage Costs:")
        print(pd.DataFrame(cost_details['storage_costs']).to_string(index=False))
        
        # Display electrolysis costs by month
        print("\nMonthly Electrolysis Costs:")
        print(pd.DataFrame(cost_details['electrolysis_costs']).to_string(index=False))
        
        # Original output
        production_data = []
        storage_data = []
        supplier_data = {i: [] for i in range(num_products)}
        electrolysis_data = []

        for t in range(months):
            # Production and storage data
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

            # Supplier data
            for i in range(num_products):
                supplier_data_row = {"Month": t + 1}
                for j in range(num_suppliers):
                    supplier_data_row[f"From Supplier {chr(65 + j)}"] = X[i, j, t].x
                supplier_data[i].append(supplier_data_row)

            # Electrolysis data
            electrolysis_data.append({
                "Month": t + 1,
                "Electrolysis Used": B[t].x,
                "18/10 Electrolysis": m[0, t].x,
                "18/8 Electrolysis": m[1, t].x,
                "18/0 Electrolysis": m[2, t].x,
            })

        # Display settings
        pd.set_option('display.float_format', '{:.2f}'.format)
        pd.set_option('display.max_rows', None)
        pd.set_option('display.max_columns', None)

        # Convert to DataFrames and display
        print("\nProduction Plan:")
        print(pd.DataFrame(production_data).to_string(index=False))

        print("\nStorage Plan:")
        print(pd.DataFrame(storage_data).to_string(index=False))

        print("\nElectrolysis Plan:")
        print(pd.DataFrame(electrolysis_data).to_string(index=False))

        for i in range(num_products):
            product_names = ["18/10", "18/8", "18/0"]
            print(f"\nSupplier Procurement Plan for Product {product_names[i]}:")
            print(pd.DataFrame(supplier_data[i]).to_string(index=False))

def solve_model_with_copper_limit(copper_limit, data):
    """
    Solve the optimization model with a specific copper limit
    """
    months, chromium_content, nickel_content, copper_content, \
        max_supply, costs, chromium_content_ratio, nickel_content_ratio, \
        _, demand, storage_costs, max_production, \
        electrolysis_fixed_cost, electrolysis_unit_cost, \
        num_product, num_supplier = data

    try:
        # Create model
        model = Model("Steel Production")
        model.setParam('OutputFlag', 0)  # Suppress output

        # Variables
        P = model.addVars(num_product, months, vtype=GRB.CONTINUOUS, name="P")
        S = model.addVars(num_product, months, vtype=GRB.CONTINUOUS, name="S")
        X = model.addVars(num_product, num_supplier, months, vtype=GRB.CONTINUOUS, name="X")
        B = model.addVars(months, vtype=GRB.BINARY, name="B")
        m = model.addVars(num_product, months, vtype=GRB.CONTINUOUS, name="m")

        # Objective function
        model.setObjective(
            quicksum(
                costs[j] * X[i, j, t] for i in range(num_product) for j in range(num_supplier) for t in range(months)) +
            quicksum(storage_costs[i] * S[i, t] for i in range(num_product) for t in range(months)) +
            quicksum(electrolysis_fixed_cost * B[t] for t in range(months)) +
            quicksum(electrolysis_unit_cost * m[i, t] for i in range(num_product) for t in range(months)),
            GRB.MINIMIZE
        )

        # Constraints
        for t in range(months):
            if t == 0:
                for i in range(num_product):
                    model.addConstr(P[i, t] - m[i, t] == demand[i, t] + S[i, t])
            else:
                for i in range(num_product):
                    model.addConstr(P[i, t] + S[i, t - 1] - m[i, t] == demand[i, t] + S[i, t])

            model.addConstr(quicksum(P[i, t] for i in range(num_product)) <= max_production)

            for j in range(num_supplier):
                model.addConstr(quicksum(X[i, j, t] for i in range(num_product)) <= max_supply[j])

            for i in range(num_product):
                model.addConstr(P[i, t] == quicksum(X[i, j, t] for j in range(num_supplier)))

                model.addConstr(
                    chromium_content_ratio[i] * (P[i, t] - m[i, t]) ==
                    quicksum(chromium_content[j] * X[i, j, t] for j in range(num_supplier))
                )

                model.addConstr(
                    nickel_content_ratio[i] * (P[i, t] - m[i, t]) ==
                    quicksum(nickel_content[j] * X[i, j, t] for j in range(num_supplier))
                )

                model.addConstr(
                    quicksum(copper_content[j] * X[i, j, t] for j in range(num_supplier)) - m[i, t] <=
                    copper_limit * (P[i, t] - m[i, t])
                )

                model.addConstr(
                    m[i, t] <= B[t] * quicksum(copper_content[j] * X[i, j, t] for j in range(num_supplier))
                )

        # Optimize
        model.optimize()

        if model.status == GRB.OPTIMAL:
            return True, model.objVal, model, (P, S, X, B, m), \
                   (storage_costs, electrolysis_fixed_cost, electrolysis_unit_cost, costs)
        else:
            return False, float('inf'), None, None, None

    except Exception as e:
        print(f"Error solving model: {str(e)}")
        return False, float('inf'), None, None, None

def find_minimum_copper_limit(data, initial_cost=None):
    """
    Find the minimum copper limit that doesn't increase costs
    Uses binary search to find the limit
    """
    # First solve with original copper limit to get baseline cost
    if initial_cost is None:
        is_feasible, baseline_cost, _, _, _ = solve_model_with_copper_limit(0.1, data)
    else:
        baseline_cost = initial_cost

    print(f"Baseline cost: {baseline_cost:.2f}")

    # Binary search parameters
    left = 0.01
    right = 0.5
    tolerance = 0.0000001
    best_limit = right
    best_model = None
    best_vars = None
    best_cost_params = None

    while right - left > tolerance:
        mid = (left + right) / 2
        print(f"\nTesting copper limit: {mid:.8f}")

        is_feasible, current_cost, model, variables, cost_params = solve_model_with_copper_limit(mid, data)

        if is_feasible and abs(current_cost - baseline_cost) < 1e-8:
            best_limit = mid
            best_model = model
            best_vars = variables
            best_cost_params = cost_params
            right = mid
        else:
            left = mid

        print(f"Current feasible: {is_feasible}, Cost: {current_cost:.2f}")

    return best_limit, best_model, best_vars, best_cost_params

# Main execution
if __name__ == "__main__":
    # Get base data
    data = get_supplier_data_e(data_e)
    months = data[0]
    num_product = data[-2]
    num_supplier = data[-1]

    print("Finding minimum copper limit...")
    min_limit, final_model, final_vars, cost_params = find_minimum_copper_limit(data)
    print(f"\nMinimum feasible copper limit: {min_limit:.6f}")

    if final_model and final_vars:
        print("\nOptimal plans for the minimum copper limit:")
        P, S, X, B, m = final_vars
        storage_costs, electrolysis_fixed_cost, electrolysis_unit_cost, supplier_costs = cost_params
        display_optimal_plans(
            final_model, months, P, S, X, B, m, 
            num_product, num_supplier,
            storage_costs, electrolysis_fixed_cost, 
            electrolysis_unit_cost, supplier_costs
        )