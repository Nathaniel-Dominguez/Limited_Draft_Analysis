import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import json
import os
import numpy as np
import argparse

def load_data(set_code="ONE"):
    """Load the CSV and JSON data files"""
    csv_path = f"draft_data_{set_code}.csv"
    json_path = f"draft_analysis_{set_code}.json"
    
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"CSV file not found: {csv_path}")
    
    if not os.path.exists(json_path):
        raise FileNotFoundError(f"JSON file not found: {json_path}")
    
    # Load the data
    df = pd.read_csv(csv_path)
    
    with open(json_path, 'r') as f:
        analysis = json.load(f)
    
    return df, analysis

def create_output_dir():
    """Create output directory for visualizations"""
    output_dir = "draft_visualizations"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    return output_dir

def plot_mana_curve(analysis, output_dir):
    """Plot the average mana curve from the draft analysis using NumPy for binning"""
    if "mana_curve" not in analysis:
        print("Mana curve data not found in analysis")
        return
    
    # Convert keys to numeric and sort
    mana_values = sorted([(float(k), v) for k, v in analysis["mana_curve"].items()])
    
    # Convert to NumPy arrays for better performance
    x = np.array([pair[0] for pair in mana_values])
    y = np.array([pair[1]/100 for pair in mana_values]) # Normalize by number of decks
    
    # Calculate statistics using NumPy
    mean_cmc = np.average(x, weights=y)  # Use np.average instead of np.mean for weighted mean
    median_cmc = np.median(x)
    std_cmc = np.sqrt(np.average((x - mean_cmc)**2, weights=y))
    
    # Set up the figure
    plt.figure(figsize=(12, 6))
    
    plt.bar(x, y, color='skyblue', edgecolor='navy', alpha=0.7)
    
    # Add a line showing the wieghted average (mean)
    plt.axvline(x=mean_cmc, color='red', linestyle='--',
                label=f'Weighted Mean = {mean_cmc:.2f}')
    
    # Add labels and title
    plt.xlabel('Mana Value')
    plt.ylabel('Average Cards per Deck')
    plt.title(f'Average Mana Curve (σ = {std_cmc:.2f})')  # Fix f-string
    
    # Adjust x axis to be integers
    plt.xticks(x)
    
    # Add grid for readability
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.legend()
    
    # Save the figure
    plt.tight_layout()
    plt.savefig(f"{output_dir}/mana_curve.png", dpi=300)
    plt.close()
    
    print(f"Mana curve visualization saved to {output_dir}/mana_curve.png")

def plot_color_distribution(analysis, output_dir):
    """Plot the color distribution from the draft analysis with NumPy for calculations"""
    if "color_distribution" not in analysis:
        print("Color distribution data not found in analysis")
        return
    
    # Set up the figure
    plt.figure(figsize=(12, 6))
    
    # Create a DataFrame from the color distribution
    colors_df = pd.DataFrame({
        'Color': list(analysis["color_distribution"].keys()),
        'Count': list(analysis["color_distribution"].values())
    })
    
    # Sort by count in descending order
    colors_df = colors_df.sort_values('Count', ascending=False)

    # Convert counts to NumPy array for calculations
    counts = np.array(colors_df['Count'])
    total = np.sum(counts)
    percentages = 100 * counts / total
    
    # Get color palettes for MTG colors
    color_map = {
        'W': '#F8F6D8',  # White
        'U': '#0E68AB',  # Blue
        'B': '#150B00',  # Black
        'R': '#D3202A',  # Red
        'G': '#00733E',  # Green
        'Colorless': '#CBC5C0',  # Colorless
        'Basic Land': '#DED5C0',  # Land
        'multicolor': '#D8C091'   # Gold/multicolor
    }
    
    # If we have combined strings like "W,U", use a default color
    bar_colors = []
    for color_name in colors_df['Color']:
        # Default color for combinations
        if ',' in color_name:
            bar_colors.append('#D8C091')  # Gold for multicolor
        else:
            # Look up the color in our map, default to gray
            bar_colors.append(color_map.get(color_name, '#808080'))
    
    # Create the bar chart
    bars = plt.bar(colors_df['Color'], colors_df['Count'], color=bar_colors, edgecolor='black')
    
    # Add labels and title
    plt.xlabel('Color')
    plt.ylabel('Total Cards')
    plt.title('Color Distribution Across All Simulated Decks')
    
    # Add total number and percentage annotations
    for i, (v, p) in enumerate(zip(counts, percentages)):
        plt.text(i, v + 0.5, f"{v} ({p:.1f}%)", ha='center')
    
    # Rotate x-axis labels for readability
    plt.xticks(rotation=45, ha='right')
    
    # Add grid for readability
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    
    # Save the figure
    plt.tight_layout()
    plt.savefig(f"{output_dir}/color_distribution.png", dpi=300)
    plt.close()
    
    print(f"Color distribution visualization saved to {output_dir}/color_distribution.png")

def plot_card_frequency(analysis, output_dir, top_n=20):
    """Plot the most frequent cards from the draft analysis"""
    if "most_common_cards" not in analysis:
        print("Card frequency data not found in analysis")
        return
    
    # Set up the figure
    plt.figure(figsize=(14, 8))
    
    # Create a DataFrame from the card frequency
    cards_df = pd.DataFrame({
        'Card': list(analysis["most_common_cards"].keys()),
        'Count': list(analysis["most_common_cards"].values())
    })
    
    # Sort by count in descending order and take top N
    cards_df = cards_df.sort_values('Count', ascending=False).head(top_n)
    
    # Reverse the order for horizontal bar chart (to have highest at top)
    cards_df = cards_df.iloc[::-1]
    
    # Create the horizontal bar chart
    plt.barh(cards_df['Card'], cards_df['Count'], color='lightblue', edgecolor='navy', alpha=0.8)
    
    # Add labels and title
    plt.xlabel('Count')
    plt.ylabel('Card Name')
    plt.title(f'Top {top_n} Most Frequently Drafted Cards')
    
    # Add total number annotations
    for i, v in enumerate(cards_df['Count']):
        plt.text(v + 0.5, i, str(v), va='center')
    
    # Add grid for readability
    plt.grid(axis='x', linestyle='--', alpha=0.7)
    
    # Save the figure
    plt.tight_layout()
    plt.savefig(f"{output_dir}/card_frequency_top_{top_n}.png", dpi=300)
    plt.close()
    
    print(f"Card frequency visualization saved to {output_dir}/card_frequency_top_{top_n}.png")

def plot_type_distribution(analysis, output_dir):
    """Plot the card type distribution from the draft analysis"""
    if "type_distribution" not in analysis:
        print("Type distribution data not found in analysis")
        return
    
    # Set up the figure
    plt.figure(figsize=(12, 8))
    
    # Create a DataFrame from the type distribution
    types_df = pd.DataFrame({
        'Type': list(analysis["type_distribution"].keys()),
        'Count': list(analysis["type_distribution"].values())
    })
    
    # Sort by count in descending order
    types_df = types_df.sort_values('Count', ascending=False)
    
    # Create the bar chart - Fix for seaborn deprecation warning
    sns.barplot(x='Count', y='Type', data=types_df, hue='Type', palette='viridis', legend=False)
    
    # Add labels and title
    plt.xlabel('Count')
    plt.ylabel('Card Type')
    plt.title('Card Type Distribution Across All Simulated Decks')
    
    # Add total number annotations
    for i, v in enumerate(types_df['Count']):
        plt.text(v + 0.5, i, str(v), va='center')
    
    # Add grid for readability
    plt.grid(axis='x', linestyle='--', alpha=0.7)
    
    # Save the figure
    plt.tight_layout()
    plt.savefig(f"{output_dir}/type_distribution.png", dpi=300)
    plt.close()
    
    print(f"Type distribution visualization saved to {output_dir}/type_distribution.png")

def plot_rarity_distribution(analysis, output_dir):
    """Plot the rarity distribution from the draft analysis using NumPy for calculations"""
    if "rarity_distribution" not in analysis:
        print("Rarity distribution data not found in analysis")
        return
    
    # Set up the figure
    plt.figure(figsize=(10, 6))
    
    # Create a DataFrame from the rarity distribution
    rarity_df = pd.DataFrame({
        'Rarity': list(analysis["rarity_distribution"].keys()),
        'Count': list(analysis["rarity_distribution"].values())
    })
    
    # Sort by traditional rarity order
    rarity_order = ['common', 'uncommon', 'rare', 'mythic']
    rarity_df['Order'] = rarity_df['Rarity'].apply(lambda x: rarity_order.index(x) if x in rarity_order else 999)
    rarity_df = rarity_df.sort_values('Order')

    # Convert to numpy array for calculations
    counts = np.array(rarity_df['Count'])
    total = np.sum(counts)
    percentages = 100 * counts / total
    
    # Define colors for each rarity
    rarity_colors = {
        'common': 'black',
        'uncommon': 'silver',
        'rare': 'gold',
        'mythic': 'orangered'
    }
    colors = [rarity_colors.get(r, 'gray') for r in rarity_df['Rarity']]
    
    # Create the pie chart with percentages
    plt.pie(counts, labels=rarity_df['Rarity'], autopct='%1.1f%%', 
            colors=colors, startangle=90, shadow=True)
    
    # Add title with total card count
    plt.title(f'Rarity Distribution Across All Simulated Decks ({total} cards)')

    # Add a table showing exact counts and percentages
    cell_text = [[f"{c} ({p:.1f}%)" for c, p in zip(counts, percentages)]]
    plt.table(cellText=cell_text,
              rowLabels=['Count (%)'],
              colLabels=rarity_df['Rarity'],
              loc='bottom',
              bbox=[0, -0.3, 1, 0.2])
    
    # Save the figure
    plt.subplots_adjust(bottom=0.3)
    plt.savefig(f"{output_dir}/rarity_distribution.png", dpi=300)
    plt.close()
    
    print(f"Rarity distribution visualization saved to {output_dir}/rarity_distribution.png")

def plot_deck_color_pairs(df, output_dir):
    """Plot frequency of two-color combinations used in decks"""
    # This requires some calculation since we need to analyze each deck
    
    # Group by deck_id
    deck_groups = df.groupby('deck_id')
    
    # Track color pairs for each deck
    color_pairs = []
    
    # Loop through each deck
    for deck_id, deck_data in deck_groups:
        # Get non-land cards to determine deck colors
        # First exclude basic lands by name
        non_basic_lands = ~deck_data['card_name'].isin(['Plains', 'Island', 'Swamp', 'Mountain', 'Forest', 'Wastes'])
        # Then exclude other lands by type
        non_lands = deck_data[non_basic_lands & ~deck_data['type_line'].str.contains('Land', na=False)]
        
        # Count cards of each color in the deck (excluding lands)
        if 'colors' in non_lands.columns:
            # Skip if colors column has NaN or is not properly formatted
            if non_lands['colors'].isna().all():
                continue
                
            # Split comma-separated colors and count each color
            color_counts = {}
            
            for _, row in non_lands.iterrows():
                if pd.isna(row['colors']) or row['colors'] == 'Colorless' or row['colors'] == 'Basic Land':
                    continue
                    
                colors = row['colors'].split(',')
                for color in colors:
                    color = color.strip()
                    if color in ['W', 'U', 'B', 'R', 'G']:
                        color_counts[color] = color_counts.get(color, 0) + 1
            
            # Find the top two colors
            if len(color_counts) >= 2:
                top_colors = sorted(color_counts.items(), key=lambda x: x[1], reverse=True)[:2]
                top_color_pair = ''.join(sorted([c[0] for c in top_colors]))
                color_pairs.append(top_color_pair)
    
    # Count the frequency of each color pair
    if color_pairs:
        pair_counts = {}
        for pair in color_pairs:
            pair_counts[pair] = pair_counts.get(pair, 0) + 1
        
        # Create DataFrame for visualization
        pair_df = pd.DataFrame({
            'Color Pair': list(pair_counts.keys()),
            'Count': list(pair_counts.values())
        })
        
        # Sort by count in descending order
        pair_df = pair_df.sort_values('Count', ascending=False)
        
        # Set up the figure
        plt.figure(figsize=(12, 8))
        
        # Define color mapping for the pairs
        color_mapping = {
            'WU': '#EAF2FA',  # Azorius
            'UB': '#2A4E6E',  # Dimir
            'BR': '#5E2B28',  # Rakdos
            'RG': '#94703E',  # Gruul
            'GW': '#A3C095',  # Selesnya
            'WB': '#D1D1D1',  # Orzhov
            'UR': '#7C4778',  # Izzet
            'BG': '#3B584F',  # Golgari
            'RW': '#E49977',  # Boros
            'GU': '#229987'   # Simic
        }
        
        # Get colors for the bars
        bar_colors = [color_mapping.get(pair, '#808080') for pair in pair_df['Color Pair']]
        
        # Plot
        plt.bar(pair_df['Color Pair'], pair_df['Count'], color=bar_colors, edgecolor='black')
        
        # Add labels and title
        plt.xlabel('Color Pair')
        plt.ylabel('Number of Decks')
        plt.title('Frequency of Two-Color Combinations in Simulated Decks')
        
        # Add grid for readability
        plt.grid(axis='y', linestyle='--', alpha=0.7)
        
        # Add count annotations
        for i, v in enumerate(pair_df['Count']):
            plt.text(i, v + 0.5, str(v), ha='center')
        
        # Save the figure
        plt.tight_layout()
        plt.savefig(f"{output_dir}/color_pair_distribution.png", dpi=300)
        plt.close()
        
        print(f"Color pair distribution visualization saved to {output_dir}/color_pair_distribution.png")
    else:
        print("Couldn't determine deck color pairs from the data")

def plot_archetype_distribution(analysis, output_dir):
    """Plot the distribution of archetypes"""
    if "archetype_distribution" not in analysis:
        print("Archetype distribution data not found in analysis")
        return
    
    # Set up the figure
    plt.figure(figsize=(14, 8))
    
    # Create a DataFrame from the archetype distribution
    arch_df = pd.DataFrame({
        'Archetype': list(analysis["archetype_distribution"].keys()),
        'Count': list(analysis["archetype_distribution"].values())
    })
    
    # Sort by count in descending order
    arch_df = arch_df.sort_values('Count', ascending=False)
    
    # Define color mapping for guild names
    archetype_color_mapping = {
        'WU': '#EAF2FA',  # Azorius
        'UB': '#2A4E6E',  # Dimir
        'BR': '#5E2B28',  # Rakdos
        'RG': '#94703E',  # Gruul
        'GW': '#A3C095',  # Selesnya
        'WB': '#D1D1D1',  # Orzhov
        'UR': '#7C4778',  # Izzet
        'BG': '#3B584F',  # Golgari
        'RW': '#E49977',  # Boros
        'GU': '#229987',  # Simic
        'auto': '#808080',  # Gray for auto
        'WUB': '#7891C4',  # Esper
        'UBR': '#531C54',  # Grixis
        'BRG': '#5E3A22',  # Jund
        'RGW': '#9A7E4F',  # Naya
        'GWU': '#4D8B7C',  # Bant
        'WBG': '#4D5645',  # Abzan
        'URW': '#815487',  # Jeskai
        'BGU': '#2D5D4B',  # Sultai
        'RWB': '#8E534A',  # Mardu
        'GUR': '#507660',  # Temur
        'MONO_W': '#F9FAF5',  # Mono White
        'MONO_U': '#0F75BB',  # Mono Blue
        'MONO_B': '#2D2A26',  # Mono Black
        'MONO_R': '#E24A33',  # Mono Red
        'MONO_G': '#00844A',  # Mono Green
        '5C': '#D8C091'  # Five Color
    }
    
    # Get colors for the bars
    bar_colors = [archetype_color_mapping.get(arch, '#808080') for arch in arch_df['Archetype']]
    
    # Create the bar chart
    plt.bar(arch_df['Archetype'], arch_df['Count'], color=bar_colors, edgecolor='black')
    
    # Add labels and title
    plt.xlabel('Archetype')
    plt.ylabel('Number of Decks')
    plt.title('Distribution of Deck Archetypes')
    
    # Rotate x-axis labels for readability
    plt.xticks(rotation=45, ha='right')
    
    # Add grid for readability
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    
    # Add count annotations
    for i, v in enumerate(arch_df['Count']):
        plt.text(i, v + 0.5, str(v), ha='center')
    
    # Save the figure
    plt.tight_layout()
    plt.savefig(f"{output_dir}/archetype_distribution.png", dpi=300)
    plt.close()
    
    print(f"Archetype distribution visualization saved to {output_dir}/archetype_distribution.png")

def plot_archetype_performance(df, output_dir):
    """Plot performance metrics by archetype"""
    if 'archetype' not in df.columns:
        print("Archetype data not found in dataframe")
        return
    
    # First check if we have enough archetypes to analyze
    if df['archetype'].nunique() <= 1:
        print("Only one archetype found, skipping archetype performance comparison")
        return
    
    # Create a figure
    plt.figure(figsize=(15, 10))
    
    # Create a grid of subplots
    fig, axes = plt.subplots(nrows=2, ncols=2, figsize=(16, 14))
    
    # 1. Average CMC by archetype
    if 'cmc' in df.columns:
        # Calculate average CMC by archetype
        avg_cmc = df.groupby('archetype')['cmc'].mean().reset_index()
        avg_cmc = avg_cmc.sort_values('cmc')
        
        # Plot - Fix for seaborn deprecation warning
        ax = axes[0, 0]
        sns.barplot(x='archetype', y='cmc', data=avg_cmc, ax=ax, hue='archetype', legend=False)
        ax.set_title('Average Mana Value by Archetype')
        ax.set_xlabel('Archetype')
        ax.set_ylabel('Average Mana Value')
        ax.tick_params(axis='x', rotation=45)
        ax.grid(axis='y', linestyle='--', alpha=0.7)
    
    # 2. Creature Count by archetype
    # Create a creature count column
    df['is_creature'] = df['type_line'].str.contains('Creature', case=False, na=False)
    
    # Group by deck_id and archetype, count creatures
    creature_counts = df[df['is_creature']].groupby(['deck_id', 'archetype']).size().reset_index(name='creature_count')
    
    # Average creature count by archetype
    avg_creatures = creature_counts.groupby('archetype')['creature_count'].mean().reset_index()
    avg_creatures = avg_creatures.sort_values('creature_count', ascending=False)
    
    # Plot - Fix for seaborn deprecation warning
    ax = axes[0, 1]
    sns.barplot(x='archetype', y='creature_count', data=avg_creatures, ax=ax, hue='archetype', legend=False)
    ax.set_title('Average Creature Count by Archetype')
    ax.set_xlabel('Archetype')
    ax.set_ylabel('Average Creatures per Deck')
    ax.tick_params(axis='x', rotation=45)
    ax.grid(axis='y', linestyle='--', alpha=0.7)
    
    # 3. Color distribution within each archetype
    # Get non-land cards
    # First exclude basic lands by name
    non_basic_lands = ~df['card_name'].isin(['Plains', 'Island', 'Swamp', 'Mountain', 'Forest', 'Wastes'])
    # Then exclude other lands by type
    non_lands = df[non_basic_lands & ~df['type_line'].str.contains('Land', na=False)]
    
    # Count unique colors in each archetype
    if 'colors' in non_lands.columns:
        # Prepare data: expand color string into separate rows
        color_data = []
        for _, row in non_lands.iterrows():
            if pd.isna(row['colors']) or row['colors'] in ['Colorless', 'Basic Land']:
                continue
                
            colors = row['colors'].split(',')
            for color in colors:
                color = color.strip()
                if color in ['W', 'U', 'B', 'R', 'G']:
                    color_data.append({
                        'archetype': row['archetype'],
                        'color': color
                    })
        
        if color_data:
            # Create DataFrame from expanded data
            color_df = pd.DataFrame(color_data)
            
            # Count colors in each archetype
            color_counts = color_df.groupby(['archetype', 'color']).size().reset_index(name='count')
            
            # Plot
            ax = axes[1, 0]
            sns.barplot(x='color', y='count', hue='archetype', data=color_counts, ax=ax, palette='deep')
            ax.set_title('Color Distribution by Archetype')
            ax.set_xlabel('Color')
            ax.set_ylabel('Card Count')
            ax.grid(axis='y', linestyle='--', alpha=0.7)
            ax.legend(title='Archetype', bbox_to_anchor=(1.05, 1), loc='upper left')
    
    # 4. Card Type distribution by archetype
    # Extract main type from type_line
    df['main_type'] = df['type_line'].apply(lambda x: x.split('—')[0].strip() if isinstance(x, str) else 'Unknown')
    
    # Count card types in each archetype
    type_counts = df.groupby(['archetype', 'main_type']).size().reset_index(name='count')
    
    # Filter to include only common card types
    common_types = type_counts.groupby('main_type')['count'].sum().nlargest(5).index
    type_counts = type_counts[type_counts['main_type'].isin(common_types)]
    
    # Plot
    ax = axes[1, 1]
    sns.barplot(x='main_type', y='count', hue='archetype', data=type_counts, ax=ax, palette='muted')
    ax.set_title('Card Type Distribution by Archetype')
    ax.set_xlabel('Card Type')
    ax.set_ylabel('Card Count')
    ax.tick_params(axis='x', rotation=45)
    ax.grid(axis='y', linestyle='--', alpha=0.7)
    ax.legend(title='Archetype', bbox_to_anchor=(1.05, 1), loc='upper left')
    
    # Adjust layout and save
    plt.tight_layout()
    plt.savefig(f"{output_dir}/archetype_performance.png", dpi=300)
    plt.close()
    
    print(f"Archetype performance visualization saved to {output_dir}/archetype_performance.png")

def plot_archetype_top_cards(analysis, output_dir):
    """Plot the top cards for each archetype"""
    # Look for archetype-specific card frequencies
    archetype_card_keys = [key for key in analysis.keys() if key.startswith("most_common_cards_")]
    
    if not archetype_card_keys:
        print("No archetype-specific card frequency data found")
        return
    
    # Get list of archetypes
    archetypes = [key.replace("most_common_cards_", "") for key in archetype_card_keys]
    
    # Create a directory for archetype card charts
    arch_dir = os.path.join(output_dir, "archetype_cards")
    if not os.path.exists(arch_dir):
        os.makedirs(arch_dir)
    
    # Create a figure to compare top cards across archetypes
    plt.figure(figsize=(16, 10))
    
    # For each archetype, plot its top cards
    for archetype in archetypes:
        key = f"most_common_cards_{archetype}"
        
        # Create a DataFrame from the card data
        cards_df = pd.DataFrame({
            'Card': list(analysis[key].keys()),
            'Count': list(analysis[key].values())
        })
        
        # Sort by count
        cards_df = cards_df.sort_values('Count', ascending=False)
        
        # Take top 10
        top_cards = cards_df.head(10)
        
        # Reverse for horizontal bar chart
        top_cards = top_cards.iloc[::-1]
        
        # Set up figure for this archetype
        plt.figure(figsize=(12, 8))
        
        # Plot horizontal bar chart
        plt.barh(top_cards['Card'], top_cards['Count'])
        
        # Add labels and title
        plt.xlabel('Count')
        plt.ylabel('Card Name')
        archetype_name = get_archetype_name(archetype)
        plt.title(f'Top 10 Cards in {archetype_name} Decks')
        
        # Add count annotations
        for i, v in enumerate(top_cards['Count']):
            plt.text(v + 0.1, i, str(v), va='center')
        
        # Add grid
        plt.grid(axis='x', linestyle='--', alpha=0.7)
        
        # Save individual archetype chart
        plt.tight_layout()
        plt.savefig(f"{arch_dir}/top_cards_{archetype}.png", dpi=300)
        plt.close()
        
    # Create a combined visualization showing top 5 cards from each archetype
    # Set up grid of subplots based on number of archetypes
    n_archetypes = len(archetypes)
    cols = min(3, n_archetypes)
    rows = (n_archetypes + cols - 1) // cols  # Ceiling division
    
    fig, axes = plt.subplots(rows, cols, figsize=(18, 5*rows))
    axes = axes.flatten() if n_archetypes > 1 else [axes]
    
    for i, archetype in enumerate(archetypes):
        if i < len(axes):
            key = f"most_common_cards_{archetype}"
            
            # Create a DataFrame from the card data
            cards_df = pd.DataFrame({
                'Card': list(analysis[key].keys()),
                'Count': list(analysis[key].values())
            })
            
            # Sort and take top 5
            top_cards = cards_df.sort_values('Count', ascending=False).head(5)
            top_cards = top_cards.iloc[::-1]  # Reverse for horizontal bar
            
            # Plot
            ax = axes[i]
            ax.barh(top_cards['Card'], top_cards['Count'])
            
            # Add title and labels
            archetype_name = get_archetype_name(archetype)
            ax.set_title(f'{archetype_name}')
            ax.set_xlabel('Count')
            
            # Add count annotations
            for j, v in enumerate(top_cards['Count']):
                ax.text(v + 0.1, j, str(v), va='center')
                
            # Add grid
            ax.grid(axis='x', linestyle='--', alpha=0.7)
    
    # Hide unused subplots
    for j in range(i+1, len(axes)):
        fig.delaxes(axes[j])
    
    plt.tight_layout()
    plt.savefig(f"{output_dir}/archetype_top_cards_comparison.png", dpi=300)
    plt.close()
    
    print(f"Archetype top cards visualizations saved to {arch_dir} and comparison saved to {output_dir}")

def get_archetype_name(code):
    """Convert archetype code to readable name"""
    archetype_names = {
        'WU': 'Azorius (WU)',
        'UB': 'Dimir (UB)',
        'BR': 'Rakdos (BR)',
        'RG': 'Gruul (RG)',
        'GW': 'Selesnya (GW)',
        'WB': 'Orzhov (WB)',
        'UR': 'Izzet (UR)',
        'BG': 'Golgari (BG)',
        'RW': 'Boros (RW)',
        'GU': 'Simic (GU)',
        'auto': 'Auto-Selected',
        'WUB': 'Esper (WUB)',
        'UBR': 'Grixis (UBR)',
        'BRG': 'Jund (BRG)',
        'RGW': 'Naya (RGW)',
        'GWU': 'Bant (GWU)',
        'WBG': 'Abzan (WBG)',
        'URW': 'Jeskai (URW)',
        'BGU': 'Sultai (BGU)',
        'RWB': 'Mardu (RWB)',
        'GUR': 'Temur (GUR)',
        'MONO_W': 'Mono White',
        'MONO_U': 'Mono Blue',
        'MONO_B': 'Mono Black',
        'MONO_R': 'Mono Red',
        'MONO_G': 'Mono Green',
        '5C': 'Five Color'
    }
    return archetype_names.get(code, code)

def plot_archetype_mana_curves(analysis, output_dir):
    """Plot mana curves for different archetypes"""
    # Find archetype-specific mana curve data
    mana_curve_keys = [key for key in analysis.keys() if key.startswith("mana_curve_")]
    
    if not mana_curve_keys:
        print("No archetype-specific mana curve data found")
        return
    
    # Get list of archetypes
    archetypes = [key.replace("mana_curve_", "") for key in mana_curve_keys]
    
    # Create a directory for mana curve charts
    curves_dir = os.path.join(output_dir, "archetype_curves")
    if not os.path.exists(curves_dir):
        os.makedirs(curves_dir)
    
    # Prepare data for combined plot
    combined_data = []
    
    # For each archetype, plot its mana curve
    for archetype in archetypes:
        key = f"mana_curve_{archetype}"
        
        # Create sorted pairs of (cmc, count)
        mana_values = sorted([(float(k), v) for k, v in analysis[key].items()])
        
        # Set up figure for this archetype
        plt.figure(figsize=(10, 6))
        
        # Plot bar chart for this archetype
        x = [pair[0] for pair in mana_values]
        y = [pair[1]/100 for pair in mana_values]  # Normalize by approximate deck count
        
        plt.bar(x, y, alpha=0.7)
        
        # Add labels and title
        plt.xlabel('Mana Value')
        plt.ylabel('Average Cards per Deck')
        archetype_name = get_archetype_name(archetype)
        plt.title(f'Mana Curve for {archetype_name} Decks')
        
        # Adjust x axis
        plt.xticks(x)
        
        # Add grid
        plt.grid(axis='y', linestyle='--', alpha=0.7)
        
        # Save individual archetype chart
        plt.tight_layout()
        plt.savefig(f"{curves_dir}/mana_curve_{archetype}.png", dpi=300)
        plt.close()
        
        # Add to combined data
        for cmc, count in mana_values:
            combined_data.append({
                'archetype': archetype,
                'cmc': cmc,
                'count': count/100  # Normalize
            })
    
    # Create combined mana curve chart
    if combined_data:
        combined_df = pd.DataFrame(combined_data)
        
        # Set up figure
        plt.figure(figsize=(14, 8))
        
        # Plot lines for each archetype
        for archetype in archetypes:
            arch_data = combined_df[combined_df['archetype'] == archetype]
            if not arch_data.empty:
                plt.plot(arch_data['cmc'], arch_data['count'], marker='o', linewidth=2, 
                         label=get_archetype_name(archetype))
        
        # Add labels and title
        plt.xlabel('Mana Value')
        plt.ylabel('Average Cards per Deck')
        plt.title('Mana Curves by Archetype')
        
        # Add legend
        plt.legend(title='Archetype')
        
        # Add grid
        plt.grid(linestyle='--', alpha=0.7)
        
        # Save combined chart
        plt.tight_layout()
        plt.savefig(f"{output_dir}/combined_mana_curves.png", dpi=300)
        plt.close()
        
        print(f"Mana curve visualizations saved to {curves_dir} and combined chart saved to {output_dir}")

def analyze_deck_statistics(df, output_dir):
    """New function using NumPy to calculate and visualize deck statistics"""
    if 'type_line' not in df.columns or 'cmc' not in df.columns:
        print("Required columns not found for deck statistics analysis")
        return
    
    # Create card type flags
    df['is_creature'] = df['type_line'].str.contains('Creature', case=False, na=False)
    df['is_sorcery'] = df['type_line'].str.contains('Sorcery', case=False, na=False)
    df['is_instant'] = df['type_line'].str.contains('Instant', case=False, na=False)
    
    # Group by deck_id and calculate statistics
    deck_stats = []
    for deck_id, deck_data in df.groupby('deck_id'):
        # Basic metrics
        creature_count = np.sum(deck_data['is_creature'])
        sorcery_count = np.sum(deck_data['is_sorcery'])
        instant_count = np.sum(deck_data['is_instant'])
        
        # CMC metrics
        cmcs = np.array(deck_data['cmc'].fillna(0))
        mean_cmc = np.mean(cmcs)
        median_cmc = np.median(cmcs)
        std_cmc = np.std(cmcs) 
        
        # Calculate creature/sorcery/instant ratio
        if sorcery_count + instant_count > 0:
            creature_sorcery_instant_ratio = creature_count / (sorcery_count + instant_count)
        else:
            creature_sorcery_instant_ratio = float('inf')
            
        deck_stats.append({
            'deck_id': deck_id,
            'creature_count': creature_count,
            'sorcery_count': sorcery_count,
            'instant_count': instant_count,
            'mean_cmc': mean_cmc,
            'median_cmc': median_cmc,
            'std_cmc': std_cmc,
            'creature_sorcery_instant_ratio': creature_sorcery_instant_ratio,
            'archetype': deck_data['archetype'].iloc[0] if 'archetype' in deck_data.columns else 'unknown'
        })
    
    if not deck_stats:
        print("No valid deck statistics found")
        return
    
    # Create DataFrame from deck stats
    stats_df = pd.DataFrame(deck_stats)

    # Create visualizations for deck statistics
    plt.figure(figsize=(12, 10))

    # 1. Creature count distribution
    plt.subplot(2, 2, 1)
    counts = stats_df['creature_count']
    bins = np.arange(np.min(counts), np.max(counts) + 2) - 0.5
    plt.hist(counts, bins=bins, alpha=0.7)
    plt.axvline(x=np.mean(counts), color='red', linestyle='--',
                label=f'Mean = {np.mean(counts):.1f}')
    plt.axvline(x=np.median(counts), color='green', linestyle='-',
               label=f'Median = {np.median(counts):.1f}')
    plt.axvline(x=np.std(counts), color='purple', linestyle='-',
                label=f'Standard Deviation = {np.std(counts):.1f}')
    plt.xlabel('Creature Count')
    plt.ylabel('Number of Decks')
    plt.title('Creature Count Distribution')
    plt.legend()
    plt.grid(linestyle='--', alpha=0.7)
    plt.tight_layout()

    # 2. Average CMC distribution
    plt.subplot(2, 2, 2)
    mean_cmcs = stats_df['mean_cmc']
    plt.hist(mean_cmcs, bins=20, alpha=0.7)
    plt.axvline(x=np.mean(mean_cmcs), color='red', linestyle='--',
                label=f'Mean = {np.mean(mean_cmcs):.2f}')
    plt.axvline(x=np.median(mean_cmcs), color='green', linestyle='-',
                label=f'Median = {np.median(mean_cmcs):.2f}')
    plt.axvline(x=np.std(mean_cmcs), color='purple', linestyle='-',
                label=f'Standard Deviation = {np.std(mean_cmcs):.2f}')
    plt.xlabel('Average Mana Value')
    plt.ylabel('Number of Decks')
    plt.title('Average Mana Value Distribution')
    plt.legend()
    plt.grid(linestyle='--', alpha=0.7)
    plt.tight_layout()

    # 3. Creature/Sorcery/Instant ratio distribution
    plt.subplot(2, 2, 3)
    ratios = stats_df['creature_sorcery_instant_ratio'].replace([np.inf, -np.inf], np.nan).dropna()
    plt.hist(ratios, bins=20, alpha=0.7, range=(0, 5))
    plt.axvline(x=np.mean(ratios), color='red', linestyle='--',
                label=f'Mean = {np.mean(ratios):.2f}')
    plt.axvline(x=np.median(ratios), color='green', linestyle='-',
                label=f'Median = {np.median(ratios):.2f}')
    plt.axvline(x=np.std(ratios), color='purple', linestyle='-',
                label=f'Standard Deviation = {np.std(ratios):.2f}')
    plt.xlabel('Creature/Sorcery/Instant Ratio')
    plt.ylabel('Number of Decks')
    plt.title('Creature/Sorcery/Instant Ratio Distribution')
    plt.legend()
    plt.grid(linestyle='--', alpha=0.7)
    plt.tight_layout()

    # 4. Archetype by Average CMC
    if 'archetype' in stats_df.columns and stats_df['archetype'].nunique() > 1:
        plt.subplot(2, 2, 4)
        arch_cmc = stats_df.groupby('archetype')['mean_cmc'].agg(['mean', 'median', 'std', 'count']).reset_index()
        arch_cmc = arch_cmc.sort_values('mean', ascending=False)

        # only include archetypes with sufficient sample size
        arch_cmc = arch_cmc[arch_cmc['count'] >= 10]

        # Plot bars for each archetype
        x = np.arange(len(arch_cmc))
        plt.bar(x, arch_cmc['mean'], alpha=0.7, label='Mean CMC', capsize=5)
        plt.bar(x, arch_cmc['median'], alpha=0.7, label='Median CMC', capsize=5)
        plt.bar(x, arch_cmc['std'], alpha=0.7, label='Standard Deviation', capsize=5)

        # Add labels and title
        plt.xlabel('Archetype')
        plt.ylabel('Average Mana Value')
        plt.title('Average Mana Value by Archetype')
        plt.xticks(x, arch_cmc['archetype'], rotation=45, ha='right')
        plt.legend()
        plt.grid(axis='y', linestyle='--', alpha=0.7)
        
    plt.tight_layout()
    plt.savefig(f"{output_dir}/deck_statistics.png", dpi=300)
    plt.close()

    print(f"Deck statistics visualizations saved to {output_dir}/deck_statistics.png")
    
    
def main():
    parser = argparse.ArgumentParser(description='Visualize MTG draft data analysis')
    parser.add_argument('--set', dest='set_code', default='tdm',
                        help='Set code for the draft data (default: tdm)')
    
    args = parser.parse_args()
    
    try:
        # Load the data
        df, analysis = load_data(args.set_code)
        
        # Create output directory
        output_dir = create_output_dir()
        
        # Generate standard visualizations
        plot_mana_curve(analysis, output_dir)
        plot_color_distribution(analysis, output_dir)
        plot_card_frequency(analysis, output_dir)
        plot_type_distribution(analysis, output_dir)
        plot_rarity_distribution(analysis, output_dir)
        plot_deck_color_pairs(df, output_dir)
        
        # Generate archetype-specific visualizations
        plot_archetype_distribution(analysis, output_dir)
        plot_archetype_performance(df, output_dir)
        plot_archetype_top_cards(analysis, output_dir)
        plot_archetype_mana_curves(analysis, output_dir)

        # New NumPy based analysis
        analyze_deck_statistics(df, output_dir)
        
        print(f"All visualizations have been saved to the '{output_dir}' directory")
        print("To view these visualizations, open the PNG files in any image viewer")
    
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main() 