import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

# Ensure the save directory exists
save_dir = 'plots'
if not os.path.exists(save_dir):
    os.makedirs(save_dir)

# Load the data
df = pd.read_excel('steel_production_experiment_results.xlsx')

# Convert 'Storage Costs' from string to numpy array
df['Storage Costs'] = df['Storage Costs'].apply(lambda x: np.array(eval(x)))

# Create new columns for each product's storage cost
df['Storage Cost 18/10'] = df['Storage Costs'].apply(lambda x: x[0])
df['Storage Cost 18/8'] = df['Storage Costs'].apply(lambda x: x[1])
df['Storage Cost 18/0'] = df['Storage Costs'].apply(lambda x: x[2])


# Function to create a line plot for a specific metric across different max production values
def plot_metric_by_production(df, metric, title):
    plt.figure(figsize=(12, 6))
    for max_prod in df['Max Production'].unique():
        data = df[df['Max Production'] == max_prod]
        plt.plot(data['Storage Cost 18/10'], data[metric], label=f'Max Prod: {max_prod}')

    plt.xlabel('Storage Cost 18/10')
    plt.ylabel(metric)
    plt.title(title)
    plt.legend()
    plt.savefig(f'{title.replace(" ", "_")}.png')
    plt.close()


# # Function to create a heatmap for a 18/10
# def plot_heatmap_10(df, metric, title):
#     pivot = df.pivot_table(values=metric,
#                            index='Storage Cost 18/10',
#                            columns='Max Production',
#                            aggfunc='mean')

#     plt.figure(figsize=(12, 8))
#     sns.heatmap(pivot, annot=True, fmt='.0f', cmap='YlOrRd')
#     plt.title(title)

#      # Save the plot to the specified directory
#     save_path = os.path.join(save_dir, f'{title.replace(" ", "_")}.png')
#     plt.savefig(save_path)
#     plt.close()

# Function to create a heatmap for a specific metric and storage cost
def plot_heatmap(ax, df, metric, storage_cost, title):
    pivot = df.pivot_table(values=metric,
                           index=storage_cost,
                           columns='Max Production',
                           aggfunc='mean')
    sns.heatmap(pivot, annot=True, fmt='.0f', cmap='YlOrRd', ax=ax)
    ax.set_title(title)

# Create a 3x3 subplot
fig, axes = plt.subplots(3, 3, figsize=(18, 18))

# Plot each heatmap in the corresponding subplot
plot_heatmap(axes[0, 0], df, 'Total Cost', 'Storage Cost 18/10', 'Total Cost 18_10')
plot_heatmap(axes[0, 1], df, 'Total Storage Cost', 'Storage Cost 18/10', 'Total Storage Cost 18_10')
plot_heatmap(axes[0, 2], df, 'Total Procurement Cost', 'Storage Cost 18/10', 'Total Procurement Cost 18_10')

plot_heatmap(axes[1, 0], df, 'Total Cost', 'Storage Cost 18/8', 'Total Cost 18_8')
plot_heatmap(axes[1, 1], df, 'Total Storage Cost', 'Storage Cost 18/8', 'Total Storage Cost 18_8')
plot_heatmap(axes[1, 2], df, 'Total Procurement Cost', 'Storage Cost 18/8', 'Total Procurement Cost 18_8')

plot_heatmap(axes[2, 0], df, 'Total Cost', 'Storage Cost 18/0', 'Total Cost 18_0')
plot_heatmap(axes[2, 1], df, 'Total Storage Cost', 'Storage Cost 18/0', 'Total Storage Cost 18_0')
plot_heatmap(axes[2, 2], df, 'Total Procurement Cost', 'Storage Cost 18/0', 'Total Procurement Cost 18_0')

# Adjust layout
plt.tight_layout()

# Save the combined plot to the specified directory
save_path = os.path.join(save_dir, 'Combined_Heatmaps.png')
plt.savefig(save_path)
plt.close()

# Function to create a scatter plot for two metrics
def plot_scatter(df, x_metric, y_metric, title):
    plt.figure(figsize=(12, 8))
    scatter = plt.scatter(df[x_metric], df[y_metric],
                          c=df['Max Production'], cmap='viridis')
    plt.colorbar(scatter, label='Max Production')
    plt.xlabel(x_metric)
    plt.ylabel(y_metric)
    plt.title(title)

    # Save the plot to the specified directory
    save_path = os.path.join(save_dir, f'{title.replace(" ", "_")}.png')
    plt.savefig(save_path)    
    plt.close()


# Create various plots
# plot_metric_by_production(df, 'Total Cost', 'Total Cost vs Storage Cost')
# plot_metric_by_production(df, 'Total Storage Cost', 'Total Storage Cost vs Storage Cost')
# plot_metric_by_production(df, 'Total Procurement Cost', 'Total Procurement Cost vs Storage Cost')

# plot_heatmap_10(df, 'Total Cost', 'Heatmap of Total Cost 18_10')
# plot_heatmap_10(df, 'Total Storage Cost', 'Heatmap of Total Storage Cost 18_10')
# plot_heatmap_10(df, 'Total Procurement Cost', 'Heatmap of Total Procurement Cost 18_10')

# plot_heatmap_8(df, 'Total Cost', 'Heatmap of Total Cost 18_8')
# plot_heatmap_8(df, 'Total Storage Cost', 'Heatmap of Total Storage Cost 18_8')
# plot_heatmap_8(df, 'Total Procurement Cost', 'Heatmap of Total Procurement Cost 18_8')

# plot_heatmap_0(df, 'Total Cost', 'Heatmap of Total Cost 18_0')
# plot_heatmap_0(df, 'Total Storage Cost', 'Heatmap of Total Storage Cost 18_0')
# plot_heatmap_0(df, 'Total Procurement Cost', 'Heatmap of Total Procurement Cost 18_0')

plot_scatter(df, 'Total Storage Cost', 'Total Procurement Cost', 'Storage Cost vs Procurement Cost')
plot_scatter(df, 'Total Storage Cost', 'Total Cost', 'Total Storage Cost vs Total Cost')
plot_scatter(df, 'Total Procurement Cost', 'Total Cost', 'Total Procurement Cost vs Total Cost')

# Box plot to show distribution of Total Cost for each Max Production value
plt.figure(figsize=(12, 6))
sns.boxplot(x='Max Production', y='Total Cost', data=df)
plt.title('Distribution of Total Cost for each Max Production Value')

# Save the plot to the specified directory
save_path = os.path.join(save_dir, 'Total_Cost_Distribution_by_Max_Production.png')
plt.savefig(save_path)
plt.close()

print("All plots have been generated and saved as PNG files.")