from gurobipy import Model, GRB, quicksum
import numpy as np
import pandas as pd
import os
import matplotlib.pyplot as plt


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
    "copper_limit": 0.018335,  # Copper content limit
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

def calculate_costs(model, months, P, S, X, B, m, storage_costs, electrolysis_fixed_cost, 
                   electrolysis_unit_cost, supplier_costs, num_products, num_suppliers):
    """Calculate detailed costs from the optimal solution"""
    
    # Storage costs
    total_storage_cost = sum(storage_costs[i] * S[i, t].x 
                           for i in range(num_products) 
                           for t in range(months))
    
    # Electrolysis costs
    total_electrolysis_cost = sum(electrolysis_fixed_cost * B[t].x +
                                 sum(electrolysis_unit_cost * m[i, t].x 
                                     for i in range(num_products))
                                 for t in range(months))
    
    # Procurement costs
    total_procurement_cost = sum(supplier_costs[j] * X[i, j, t].x 
                               for i in range(num_products) 
                               for j in range(num_suppliers) 
                               for t in range(months))
    
    return {
        "total_cost": model.objVal,
        "storage_cost": total_storage_cost,
        "electrolysis_cost": total_electrolysis_cost,
        "procurement_cost": total_procurement_cost
    }

def solve_model_with_copper_limit(copper_limit, data):
    """Solve the optimization model with a specific copper limit"""
    months, chromium_content, nickel_content, copper_content, \
        max_supply, costs, chromium_content_ratio, nickel_content_ratio, \
        _, demand, storage_costs, max_production, \
        electrolysis_fixed_cost, electrolysis_unit_cost, \
        num_product, num_supplier = data

    try:
        # Create model
        model = Model("Steel Production")
        model.setParam('OutputFlag', 0)

        # Variables
        P = model.addVars(num_product, months, vtype=GRB.CONTINUOUS, name="P")
        S = model.addVars(num_product, months, vtype=GRB.CONTINUOUS, name="S")
        X = model.addVars(num_product, num_supplier, months, vtype=GRB.CONTINUOUS, name="X")
        B = model.addVars(months, vtype=GRB.BINARY, name="B")
        m = model.addVars(num_product, months, vtype=GRB.CONTINUOUS, name="m")

        # Objective function
        model.setObjective(
            quicksum(costs[j] * X[i, j, t] 
                    for i in range(num_product) 
                    for j in range(num_supplier) 
                    for t in range(months)) +
            quicksum(storage_costs[i] * S[i, t] 
                    for i in range(num_product) 
                    for t in range(months)) +
            quicksum(electrolysis_fixed_cost * B[t] 
                    for t in range(months)) +
            quicksum(electrolysis_unit_cost * m[i, t] 
                    for i in range(num_product) 
                    for t in range(months)),
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
                      m[i, t] <= B[t] * 999999
                )

        # Optimize
        model.optimize()

        if model.status == GRB.OPTIMAL:
            cost_breakdown = calculate_costs(
                model, months, P, S, X, B, m, 
                storage_costs, electrolysis_fixed_cost, 
                electrolysis_unit_cost, costs, 
                num_product, num_supplier
            )
            return True, cost_breakdown
        else:
            return False, None

    except Exception as e:
        print(f"Error solving model with copper limit {copper_limit}: {str(e)}")
        return False, None

def scan_copper_limits(data, start=0.000, end=0.03, step=0.001):
    """Scan through different copper limits and save results to Excel"""
    results = []
    copper_limits = np.arange(start, end + step, step)
    
    for copper_limit in copper_limits:
        print(f"Testing copper limit: {copper_limit:.3f}")
        is_feasible, cost_breakdown = solve_model_with_copper_limit(copper_limit, data)
        
        if is_feasible and cost_breakdown:
            results.append({
                "Copper Limit": copper_limit,
                "Total Cost": cost_breakdown["total_cost"],
                "Storage Cost": cost_breakdown["storage_cost"],
                "Electrolysis Cost": cost_breakdown["electrolysis_cost"],
                "Procurement Cost": cost_breakdown["procurement_cost"]
            })
    
    # Convert results to DataFrame
    results_df = pd.DataFrame(results)
    
    # Save to Excel
    excel_path = os.path.join(os.path.dirname(__file__), "copper_limit_analysis.xlsx")
    results_df.to_excel(excel_path, index=False)
    print(f"\nResults saved to: {excel_path}")
    
    return results_df

# Main execution
if __name__ == "__main__":
    # Get base data
    data = get_supplier_data_e(data_e)
    
    # Scan copper limits and save results
    results_df = scan_copper_limits(data)
    
    # Display summary
    print("\nSummary of results:")
    print(results_df.to_string(index=False))

    df = pd.read_excel('copper_limit_analysis.xlsx')

    # Set the columns to be plotted against 'Copper Limit'
    columns_to_plot = ['Total Cost', 'Storage Cost', 'Electrolysis Cost', 'Procurement Cost']

    # Create a scatter plot with lines connecting the points
    plt.figure(figsize=(10, 6))

    for column in columns_to_plot:
        plt.plot(df['Copper Limit'], df[column], marker='o', label=column)

    # Adding labels and title
    plt.xlabel('Copper Limit')
    plt.ylabel('Cost Values')
    plt.title('Costs based on Copper Limit')
    plt.legend(loc='center left', bbox_to_anchor=(1, 0.5))
    plt.grid(True)

    # Adjust layout to make room for the legend
    plt.tight_layout()
    # Show the plot
    plt.show()
