import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# Load the data
file_path = "SNP-distances.matrix.tsv"
df = pd.read_csv(file_path, sep='\t')

# Print column names to check
print("Column names in the dataframe:", df.columns.tolist())

# Rename first column to 'Sample' (Ensure it's properly named)
df.rename(columns={df.columns[0]: "Sample"}, inplace=True)

# Melt the DataFrame to long format
df_melted = df.melt(id_vars=["Sample"], var_name="Sample_Column", value_name="Value")

# Print melted DataFrame head for debugging
print(df_melted.head())

# Pivot the melted DataFrame to a wide format for the heatmap
pivot_df = df_melted.pivot(index="Sample", columns="Sample_Column", values="Value")

# Check if pivot worked correctly
print("Pivot table shape:", pivot_df.shape)

# Create heatmap
plt.figure(figsize=(12, 8))
heatmap = sns.heatmap(
    pivot_df, 
    cmap="viridis", linewidths=0.5
)

plt.title("SNP Distance Heatmap")
plt.xticks(rotation=45, ha='right')
plt.xlabel("Sample")
plt.ylabel("Sample_Column")

# Save plot as PNG
output_file = "snp_distance_heatmap.png"
plt.savefig(output_file, dpi=300, bbox_inches='tight')
plt.close()

print(f"Heatmap saved as {output_file}")
