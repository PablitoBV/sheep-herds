import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import sys 

if len(sys.argv) < 3:
    print("Error: Please provide input CSV and output filename.")
    print("Usage: python data_analysis.py <input.csv> <output_plot.png>")
    sys.exit(1)

file_path = sys.argv[1]
output_plot_path = sys.argv[2]

print(f"Loading data from: {file_path}")

# We read from row 7 (netlogo formatting).
try:
    df = pd.read_csv(file_path, skiprows=6)
except:
    df = pd.read_csv(file_path)


# Remove brackets from NetLogo column names
df.columns = [c.strip().replace('[', '').replace(']', '') for c in df.columns]
 
df = df.loc[:, ~df.columns.duplicated()]

cols_to_numeric = ['num-dogs', 'dog-speed', 'get-success-percentage']
for col in cols_to_numeric:
    if col in df.columns:
        df[col] = pd.to_numeric(df[col], errors='coerce')

print(f"Data Loaded: {df.shape[0]} rows")
print("-" * 60)



########## Analysis ##############

def print_stats(grouped_df, title):
    print(f"\n📊 {title}")
    print("-" * 60)
    print(grouped_df)
    print("-" * 60)

stats_speed = df.groupby('dog-speed')['get-success-percentage'].agg(
    ['mean', 'median', 'std', 'count']
).round(2)
print_stats(stats_speed, "Success by Dog Speed")

stats_dogs = df.groupby('num-dogs')['get-success-percentage'].agg(
    ['mean', 'median', 'std', 'count']
).round(2)
print_stats(stats_dogs, "Success by Number of Dogs")

stats_both = df.groupby(['num-dogs', 'dog-speed'])['get-success-percentage'].agg(
    ['mean', 'std']
).round(2)


# print_stats(stats_both, "Success by both (Num Dogs & Speed)")




##### Plots #############

sns.set_theme(style="whitegrid")
fig = plt.figure(figsize=(20, 12))
layout = (2, 2)

# succes VS dog speed
ax1 = plt.subplot2grid(layout, (0, 0))
sns.lineplot(data=df, x='dog-speed', y='get-success-percentage', ax=ax1, marker='o', color='teal')
ax1.set_title('Overall success vs. dog speed', fontsize=14)
ax1.set_ylabel('Success %')

# success vs num dogs
ax2 = plt.subplot2grid(layout, (0, 1))
sns.lineplot(data=df, x='num-dogs', y='get-success-percentage', ax=ax2, marker='o', color='orange')
ax2.set_title('Overall success vs. number of dogs', fontsize=14)
ax2.set_ylabel('Success %')

# heatmap success vs num dogs vs dog speeds
ax3 = plt.subplot2grid(layout, (1, 0))
pivot_table = df.pivot_table(
    index='dog-speed', 
    columns='num-dogs', 
    values='get-success-percentage', 
    aggfunc='mean'
)
sns.heatmap(pivot_table, ax=ax3, cmap="viridis", annot=False, cbar_kws={'label': 'Success %'})
ax3.set_title('Heatmap: Success % by speed and dog number', fontsize=14)
ax3.invert_yaxis()


plt.tight_layout()



print(f"Saving plot to: {output_plot_path}")
plt.savefig(output_plot_path)
print("----------- plots generated!! ------")