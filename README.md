# 🎴 MTG Sealed Deck Analyzer

This Python script simulates and analyzes Magic: The Gathering sealed deck drafts using the Scryfall API.

## 🎯 Features

- Simulates 100 sealed decks with 23 non-land cards each (17 basic lands assumed to be added separately)
- Supports multiple deck archetypes (guild pairs, three-color combinations, mono-color)
- Analyzes card frequency, color distribution, mana curve, and more
- Compares performance across different archetypes
- Uses NumPy for efficient statistical analysis and visualization
- Excludes basic lands from analysis for clearer insights
- Saves results to CSV and JSON files for further analysis
- Visualizes draft data with interactive charts and graphs

## 📦 Requirements

- Python 3.6+
- Required packages:
  - pandas (data manipulation and analysis)
  - matplotlib (base plotting library)
  - seaborn (statistical visualizations)
  - requests (API calls to Scryfall)
  - tqdm (progress bars)
  - numpy (numerical operations)
  - argparse (command line arguments)

## 👷 Installation

1. Clone this repository
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

## :godmode: Usage

### 💻 Simulation

Run the simulation script with:

```
python mtg_draft_analysis.py
```

By default, the script uses the "tdm" set code. To change the set:

1. Open `mtg_draft_analysis.py`
2. Modify the `set_code` variable in the `main()` function
3. Use the three-letter set code of your preferred MTG set

#### Deck Construction

The simulator builds decks with 23 non-land cards following standard Limited format guidelines, with the understanding that 17 basic lands would be added to make a complete 40-card deck. The land distribution is calculated based on the color requirements of the selected cards but not included in the final output.

#### Adjusting Archetypes

You can customize which deck archetypes are built by:

1. Using a specific archetype for all decks by setting the `archetype` variable:
   ```python
   archetype = "WU"  # All decks will be Azorius (White-Blue)
   ```

2. Using a realistic meta distribution by setting up the `archetype_distribution` variable:
   ```python
   archetype_distribution = {
       "WU": 0.12,  # 12% Azorius
       "UB": 0.13,  # 13% Dimir
       # ... and so on
   }
   ```

Available archetypes include:
- Two-color pairs: "WU", "UB", "BR", "RG", "GW", "WB", "UR", "BG", "RW", "GU"
- Three-color combinations: "WUB", "UBR", "BRG", "RGW", "GWU", etc.
- Mono-color: "MONO_W", "MONO_U", "MONO_B", "MONO_R", "MONO_G"
- Five-color: "5C"
- Auto-determine: "auto"

### 📊 Data Analysis Workflow

The simulator follows these steps:
1. Fetches card data from the Scryfall API for the specified set
2. Generates 100 sealed pools (6 boosters of 15 cards each)
3. Builds 40-card decks following archetype-specific strategies
4. Analyzes card distribution, mana values, colors, and more
5. Exports results to two complementary file formats:
   - CSV file: Contains detailed card-level data from all simulated drafts
   - JSON file: Contains pre-aggregated analysis metrics (frequencies, distributions, etc.)

Basic lands are excluded from the analysis to provide clearer insights into card choices and archetypes, but are still added to decks in appropriate quantities during deck construction.

### 📊 Visualization

After running the simulation, visualize the results with:

```
python visualize_draft_data.py --set tdm
```

Replace `tdm` with the set code you used for simulation.

The visualization script requires both output files from the simulation:
- `draft_data_[SET_CODE].csv`: Used for detailed card-by-card and deck-level analysis
- `draft_analysis_[SET_CODE].json`: Used for pre-calculated metrics and distributions

Different visualizations use different data sources:
- JSON data powers: mana curve, color distribution, card frequency, type distribution, and rarity visualizations
- CSV data powers: color pair distributions, archetype performance metrics
- Some visualizations use both sources for comprehensive analysis

The visualization script generates the following charts:

- **Mana Curve**: Average number of cards at each mana value
- **Color Distribution**: Distribution of cards by color
- **Card Frequency**: Top 20 most frequently drafted cards
- **Type Distribution**: Distribution of cards by card type
- **Rarity Distribution**: Breakdown of cards by rarity
- **Color Pair Distribution**: Frequency of two-color combinations in decks
- **Deck Statistics**: NumPy-powered analysis of deck construction metrics including creature counts, mana value distributions, and card type ratios

#### Archetype Visualization

When using multiple archetypes, additional visualizations are generated:

- **Archetype Distribution**: Percentage of decks for each archetype
- **Archetype Performance**: Comparative analysis of archetypes including:
  - Average mana value by archetype
  - Average creature count by archetype
  - Color distribution within each archetype
  - Card type distribution by archetype
- **Top Cards by Archetype**: Most common cards in each archetype
- **Mana Curves by Archetype**: Comparison of mana curves across archetypes

All visualizations are saved as PNG files in the `draft_visualizations` directory.

## 📦 Output

The scripts generate several files:
- `draft_data_[SET_CODE].csv`: Raw data of all simulated decks
- `draft_analysis_[SET_CODE].json`: Aggregated analysis results
- `draft_visualizations/*.png`: Visual charts of the analysis results
- `draft_visualizations/archetype_cards/*.png`: Archetype-specific card charts
- `draft_visualizations/archetype_curves/*.png`: Archetype-specific mana curves

The simulation script also prints key findings to the console.

## 🔧 Customization

You can modify:
- The number of simulated drafts (change `num_drafts` parameter)
- The deck building algorithm in the `build_deck()` method
- The archetype weights to optimize draft picks for specific strategies
- The analysis metrics in the `analyze_drafts()` method
- The visualization styles in the visualization script

## 🧰 Technologies Used

- **Pandas**: Used for data manipulation, transformation, and analysis
- **NumPy**: Powers efficient numerical operations, statistical calculations, and data processing
- **Seaborn**: Built on Matplotlib, provides enhanced statistical visualizations
- **Matplotlib**: Creates the base plots and charts
- **Scryfall API**: Source of card data and metadata

## 📝 Notes

This is a simplified simulation and doesn't perfectly replicate:
- Actual booster pack distribution rules (collation)
- Expert draft pick selections
- Optimal deck building strategies

For best results, customize the deck building algorithm to better match your preferences.

## 🙏 Acknowledgments

- [Pandas](https://pandas.pydata.org/) for data manipulation and analysis
- [NumPy](https://numpy.org/) for efficient numerical operations
- [Seaborn](https://seaborn.pydata.org/) for the statistical visualizations
- [Matplotlib](https://matplotlib.org/) for the base plotting library 
- [Scryfall API](https://scryfall.com/docs/api) for providing the card data
- :shipit:

## 📚 References

- [Pandas Documentation](https://pandas.pydata.org/docs/)
- [Numpy Documentation](https://numpy.org/doc/stable/)
- [Seaborn Documentation](https://seaborn.pydata.org/examples/index.html)
- [Matplotlib Documentation](https://matplotlib.org/stable/users/index.html)
- [Scryfall API Documentation](https://scryfall.com/docs/api)

## License

This project is licensed under the Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International License (CC BY-NC-SA 4.0).

## You are free to:
- Share — copy and redistribute the material in any medium or format
- Adapt — remix, transform, and build upon the material

## Under the following terms:
- Attribution — You must give appropriate credit, provide a link to the license, and indicate if changes were made.
- NonCommercial — You may not use the material for commercial purposes.
- ShareAlike — If you remix, transform, or build upon the material, you must distribute your contributions under the same license as the original.

## Attribution:
- This project uses data from the Scryfall API (https://scryfall.com/docs/api) which is licensed under CC BY-NC-SA 4.0.
- Card information provided by Scryfall © Scryfall LLC.
- Magic: The Gathering is © Wizards of the Coast LLC.

Full license text: https://creativecommons.org/licenses/by-nc-sa/4.0/legalcode
