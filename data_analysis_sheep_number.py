import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import sys
from mpl_toolkits.mplot3d import Axes3D

def main():
    if len(sys.argv) < 3:
        print("Usage: python data_analysis_sheep_number_v2.py <input.csv> <output_plot.png>")
        sys.exit(1)

    file_path = sys.argv[1]
    output_plot_path = sys.argv[2]

    try:
        df = pd.read_csv(file_path, skiprows=6)
    except:
        df = pd.read_csv(file_path)

    df.columns = [c.strip().replace('[', '').replace(']', '') for c in df.columns]
    df = df.loc[:, ~df.columns.duplicated()]

    cols = ['num-sheep', 'dog-speed', 'get-success-percentage', 'num-dogs', 
            'get-tick-50pct', 'get-tick-80pct', 'get-tick-100pct']
    for c in cols:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors='coerce')

    sns.set_theme(style="whitegrid")
    # Increased height to fit 4 rows
    fig = plt.figure(figsize=(24, 24))

    # success by herd size overall
    ax1 = fig.add_subplot(4, 3, 1)
    sns.lineplot(data=df, x='num-sheep', y='get-success-percentage', 
                 marker='o', color='crimson', ax=ax1)
    ax1.set_title('Impact of Flock Size on Success Rate', fontweight='bold')

    # success by herd size by dog speed
    ax2 = fig.add_subplot(4, 3, 2)
    sns.lineplot(data=df, x='num-sheep', y='get-success-percentage', 
                 hue='dog-speed', palette='viridis', marker='o', ax=ax2)
    ax2.set_title('Success by Flock Size & Speed', fontweight='bold')
    ax2.legend(title='Dog Speed', loc='upper right', fontsize='small')

    # success by dog speed by herd size
    ax3 = fig.add_subplot(4, 3, 3)
    sns.lineplot(data=df, x='dog-speed', y='get-success-percentage', 
                 hue='num-sheep', palette='magma', marker='o', ax=ax3)
    ax3.set_title('Success by Speed & Flock Size', fontweight='bold')
    ax3.legend(title='Num Sheep', loc='lower right', fontsize='small')

    # heatmap
    ax4 = fig.add_subplot(4, 3, 4)
    try:
        pivot = df.pivot_table(index='num-sheep', columns='dog-speed', values='get-success-percentage')
        sns.heatmap(pivot, cmap="RdYlGn", annot=True, fmt=".1f", ax=ax4)
        ax4.set_title('Stability Map (Success %)')
        ax4.invert_yaxis()
    except:
        ax4.text(0.5, 0.5, "Data error", ha='center')

    # efficiency of dogs to get sheep in target
    ax5 = fig.add_subplot(4, 3, 5)
    time_cols = ['get-tick-50pct', 'get-tick-80pct', 'get-tick-100pct']
    if all(c in df.columns for c in time_cols):
        valid_times = df[df['get-tick-100pct'] > 0].copy()
        valid_times = valid_times.groupby('num-sheep')[time_cols].mean().reset_index()
        valid_times = valid_times.melt('num-sheep', var_name='Milestone', value_name='Ticks')
        sns.lineplot(data=valid_times, x='num-sheep', y='Ticks', hue='Milestone', ax=ax5, marker='s')
        ax5.set_title('Task Completion Time Scaling')
    else:
        ax5.text(0.5, 0.5, "Missing time columns", ha='center')

    # success per total sheep
    ax6 = fig.add_subplot(4, 3, 6)
    df['eff'] = df['get-success-percentage'] / df['num-sheep']
    sns.lineplot(data=df, x='num-sheep', y='eff', hue='dog-speed', ax=ax6, legend=False)
    ax6.set_title('Efficiency (Success % / Sheep Count)')

    # sheep per dog ratio
    ax7 = fig.add_subplot(4, 3, 7)
    if 'num-dogs' in df.columns and df['num-dogs'].nunique() > 1:
        df['ratio'] = df['num-sheep'] / df['num-dogs']
        sns.scatterplot(data=df, x='ratio', y='get-success-percentage', hue='dog-speed', ax=ax7)
    else:
        sns.scatterplot(data=df, x='num-sheep', y='get-success-percentage', hue='dog-speed', ax=ax7)
    ax7.set_title('Performance vs Scaling Ratio')

    # 3D plot
    ax8 = fig.add_subplot(4, 3, 8, projection='3d')
    try:
        surf_data = df.groupby(['num-sheep', 'dog-speed'])['get-success-percentage'].mean().reset_index()
        x_u, y_u = surf_data['num-sheep'].unique(), surf_data['dog-speed'].unique()
        X, Y = np.meshgrid(x_u, y_u)
        Z = np.zeros(X.shape)
        for i in range(len(y_u)):
            for j in range(len(x_u)):
                val = surf_data[(surf_data['dog-speed']==y_u[i]) & (surf_data['num-sheep']==x_u[j])]['get-success-percentage']
                Z[i, j] = val.values[0] if not val.empty else 0
        ax8.plot_surface(X, Y, Z, cmap='viridis', alpha=0.8)
        ax8.set_title('3D Performance Landscape')
    except:
        pass

    # boxplot variance
    ax9 = fig.add_subplot(4, 3, 9)
    sns.boxplot(data=df, x='num-sheep', y='get-success-percentage', ax=ax9, palette='Pastel1')
    ax9.set_title('Success Variance per Herd Size')

    # heatmap of sheep number per dog number
    ax10 = fig.add_subplot(4, 3, 10)
    try:
        # Pivot table for Sheep vs Dogs
        pivot2 = df.pivot_table(index='num-sheep', columns='num-dogs', values='get-success-percentage')
        sns.heatmap(pivot2, cmap="YlGnBu", annot=True, fmt=".1f", ax=ax10)
        ax10.set_title('Success %: Sheep Count vs Dog Count', fontweight='bold')
        ax10.invert_yaxis()
    except:
        ax10.text(0.5, 0.5, "Variation not found in Dogs/Sheep", ha='center')
    
    plt.tight_layout()
    plt.savefig(output_plot_path)
    print(f"Full suite of plots saved to: {output_plot_path}")

if __name__ == "__main__":
    main()