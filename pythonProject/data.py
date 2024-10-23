import numpy as np
import itertools


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


# Data for experimental test
data_exp = {
    "months": 12,  # Number of months
    "storage_costs": np.array([20, 10, 5]),  # Storage costs for 18/10, 18/8, and 18/0
    "max_production": 100,  # Maximum production capacity per month
    "demand": {  # Demand for each type (18/10, 18/8, 18/0)
        "18_10": np.array([10, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]),
        "18_8": np.array([10, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]),
        "18_0": np.array([10, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]),
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


# Data used in question c verification
# Objective function parameter: Increase the storage cost of 18/0 product from 5 to 20
data_c1 = {
    "months": 12,  # Number of months
    "storage_costs": np.array([20, 10, 20]),  # Storage costs for 18/10, 18/8, and 18/0
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


# Objective function parameter: Decrease the supplier procurement cost of supplier B from 10 to 1
data_c2 = {
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
        "B": [0.25, 0.15, 0.04, 30, 1],
        "C": [0.15, 0.10, 0.02, 50, 9],
        "D": [0.14, 0.16, 0.05, 70, 7],
        "E": [0.00, 0.10, 0.03, 20, 8.5],
    },  # Supplier matrix
    "chromium_content_ratio": np.array([0.18, 0.18, 0.18]),  # Chromium content ratio
    "nickel_content_ratio": np.array([0.1, 0.08, 0]),  # Nickel content ratio
    "Product set": 3,  # Kinds of products
    "Supplier set": 5,  # Kinds of suppliers
}


# Functional parameter test: Produce only 1kg 25/0 product in the first month \
#                       to test whether the model can output pure chromium
data_c3 = {
    "months": 12,  # Number of months
    "storage_costs": np.array([20, 10, 5]),  # Storage costs for 18/10, 18/8, and 18/0
    "max_production": 100,  # Maximum production capacity per month
    "demand": {  # Demand for each type (18/10, 18/8, 18/0)
        "18_10": np.array([0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]),
        "18_8": np.array([0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]),
        "18_0": np.array([1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]),
    },
    "suppliers": {
        "A": [0.18, 0.00, 0.00, 90, 5],
        "B": [0.25, 0.15, 0.04, 30, 10],
        "C": [0.15, 0.10, 0.02, 50, 9],
        "D": [0.14, 0.16, 0.05, 70, 7],
        "E": [0.00, 0.10, 0.03, 20, 8.5],
    },  # Supplier matrix
    "chromium_content_ratio": np.array([0.18, 0.18, 0.25]),  # Chromium content ratio
    "nickel_content_ratio": np.array([0.1, 0.08, 0]),  # Nickel content ratio
    "Product set": 3,  # Kinds of products
    "Supplier set": 5,  # Kinds of suppliers
}


# Functional parameter test: Adjust supply to have only two suppliers supplying pure metal material \
# (25% chromium for supplier A and 18% nickel for supplier E)
data_c4 = {
    "months": 12,  # Number of months
    "storage_costs": np.array([20, 10, 5]),  # Storage costs for 18/10, 18/8, and 18/0
    "max_production": 100,  # Maximum production capacity per month
    "demand": {  # Demand for each type (18/10, 18/8, 18/0)
        "18_10": np.array([25, 25, 0, 0, 0, 50, 12, 0, 10, 10, 45, 99]),
        "18_8": np.array([10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10]),
        "18_0": np.array([5, 20, 80, 25, 50, 125, 150, 80, 40, 35, 3, 100]),
    },
    "suppliers": {
        "A": [0.25, 0.00, 0.00, 100, 5],
        "B": [0, 0, 0.04, 30, 10],
        "C": [0, 0, 0.02, 50, 9],
        "D": [0, 0, 0.05, 70, 7],
        "E": [0.00, 0.18, 0, 100, 8.5],
    },  # Supplier matrix
    "chromium_content_ratio": np.array([0.18, 0.18, 0.18]),  # Chromium content ratio
    "nickel_content_ratio": np.array([0.1, 0.08, 0]),  # Nickel content ratio
    "Product set": 3,  # Kinds of products
    "Supplier set": 5,  # Kinds of suppliers
}


# RHS parameter test: Increase the maximum production capacity from 100 to 1000
data_c5 = {
    "months": 12,  # Number of months
    "storage_costs": np.array([20, 10, 5]),  # Storage costs for 18/10, 18/8, and 18/0
    "max_production": 1000,  # Maximum production capacity per month
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


# RHS parameter test: Increase the maximum supply from supplier A from 90 to 900
data_c6 = {
    "months": 12,  # Number of months
    "storage_costs": np.array([20, 10, 5]),  # Storage costs for 18/10, 18/8, and 18/0
    "max_production": 100,  # Maximum production capacity per month
    "demand": {  # Demand for each type (18/10, 18/8, 18/0)
        "18_10": np.array([25, 25, 0, 0, 0, 50, 12, 0, 10, 10, 45, 99]),
        "18_8": np.array([10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10, 10]),
        "18_0": np.array([5, 20, 80, 25, 50, 125, 150, 80, 40, 35, 3, 100]),
    },
    "suppliers": {
        "A": [0.18, 0.00, 0.00, 900, 5],
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


# RHS parameter test: Verification with a demand of Jan [10,10,10] and Feb-Dec zero
data_c7 = {
    "months": 12,  # Number of months
    "storage_costs": np.array([20, 10, 5]),  # Storage costs for 18/10, 18/8, and 18/0
    "max_production": 100,  # Maximum production capacity per month
    "demand": {  # Demand for each type (18/10, 18/8, 18/0)
        "18_10": np.array([10, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]),
        "18_8": np.array([10, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]),
        "18_0": np.array([10, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]),
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


# d: experiment
# Experimental scenarios
experimental_scenarios = []

# Define experiment parameters
max_production_values = [95, 100, 120, 150, 200]
storage_cost_base = np.array([20, 10, 5])
storage_cost_multipliers = [0.1, 0.5, 1.0, 2.0, 5.0]

# Generate scenarios
for max_prod in max_production_values:
    for cost_multipliers in itertools.product(storage_cost_multipliers, repeat=3):
        scenario = data_b.copy()
        scenario['max_production'] = max_prod
        scenario['storage_costs'] = np.array([
            storage_cost_base[0] * cost_multipliers[0],
            storage_cost_base[1] * cost_multipliers[1],
            storage_cost_base[2] * cost_multipliers[2]
        ])
        experimental_scenarios.append(scenario)


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
        np.array([data["demand"]["18_10"], data["demand"]["18_8"], data["demand"]["18_0"]]),  # Demand for each type
        np.array(data["storage_costs"]),  # Storage costs for each type
        data["max_production"],  # Max production
        data["electrolysis_fixed_cost"],
        data["electrolysis_unit_cost"],
        data["Product set"],
        data["Supplier set"],
    )

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
    "copper_limit": 0.001,  # Copper content limit
    "electrolysis_fixed_cost": 100,  # Fixed cost for electrolysis
    "electrolysis_unit_cost": 5,  # Unit cost for electrolysis
}