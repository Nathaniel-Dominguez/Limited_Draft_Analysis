import requests
import pandas as pd
import random
import time
import json
from tqdm import tqdm

class DraftSimulator:
    """
    A class to simulate MTG sealed deck building and analyze the results.
    Uses the Scryfall API to get card data.
    """
    
    def __init__(self, set_code="tdm"):
        self.set_code = set_code
        self.cards_in_set = []
        self.card_data = {}
        self.sealed_pool_size = 90  # 6 boosters × 15 cards
        self.deck_size = 40
        self.basic_lands = ["Plains", "Island", "Swamp", "Mountain", "Forest"]
        # Define common archetypes
        self.archetypes = {
            # "auto": "Automatically determine best colors",
            # "WU": "Azorius (White-Blue)",
            # "UB": "Dimir (Blue-Black)",
            # "BR": "Rakdos (Black-Red)",
            # "RG": "Gruul (Red-Green)",
            # "GW": "Selesnya (Green-White)",
            "WB": "Orzhov (White-Black)",
            "UR": "Izzet (Blue-Red)",
            "BG": "Golgari (Black-Green)",
            "RW": "Boros (Red-White)",
            "GU": "Simic (Green-Blue)",
            # "WUB": "Esper (White-Blue-Black)",
            # "UBR": "Grixis (Blue-Black-Red)",
            # "BRG": "Jund (Black-Red-Green)",
            # "RGW": "Naya (Red-Green-White)",
            # "GWU": "Bant (Green-White-Blue)",
            "WBG": "Abzan (White-Black-Green)",
            "URW": "Jeskai (Blue-Red-White)",
            "BGU": "Sultai (Black-Green-Blue)",
            "RWB": "Mardu (Red-White-Black)",
            "GUR": "Temur (Green-Blue-Red)",
            "MONO_W": "Mono White",
            "MONO_U": "Mono Blue",
            "MONO_B": "Mono Black",
            "MONO_R": "Mono Red",
            "MONO_G": "Mono Green",
            "5C": "Five Color"
        }
        # Define archetype weights for card evaluation
        self.archetype_weights = {
            # TWO-COLOR ARCHETYPES (GUILDS)
            
            # Azorius (WU) - Flying and control
            # "WU": {
            #     "keywords": ["flying", "vigilance", "counter", "exile", "tap", "draw", "flicker", "spirit", "bird"],
            #     "creature_weight": 0.7,
            #     "noncreature_weight": 1.3,
            #     "min_creatures": 14
            # },
            
            # Dimir (UB) - Card advantage and graveyard interaction
            # "UB": {
            #     "keywords": ["surveil", "draw", "discard", "mill", "graveyard", "return", "zombie", "rogue", "flash"],
            #     "creature_weight": 0.8,
            #     "noncreature_weight": 1.2,
            #     "min_creatures": 13
            # },
            
            # Rakdos (BR) - Aggression and sacrifice
            # "BR": {
            #     "keywords": ["sacrifice", "damage", "destroy", "devil", "demon", "attack", "haste", "vampire", "madness"],
            #     "creature_weight": 1.2,
            #     "noncreature_weight": 0.8,
            #     "min_creatures": 16
            # },
            
            # Gruul (RG) - Big creatures and combat tricks
            # "RG": {
            #     "keywords": ["trample", "fight", "+1/+1", "beast", "dinosaur", "power", "riot", "wolf", "warrior"],
            #     "creature_weight": 1.4,
            #     "noncreature_weight": 0.6,
            #     "min_creatures": 18
            # },
            
            # Selesnya (GW) - Go wide and +1/+1 counters
            # "GW": {
            #     "keywords": ["token", "populate", "counter", "life", "enchantment", "citizen", "elf", "convoke", "human"],
            #     "creature_weight": 1.2,
            #     "noncreature_weight": 0.8,
            #     "min_creatures": 17
            # },
            
            # Orzhov (WB) - Life drain and aristocrats
            "WB": {
                "keywords": ["drain", "lifegain", "sacrifice", "afterlife", "cleric", "vampire", "knight", "extort", "token"],
                "creature_weight": 1.0,
                "noncreature_weight": 1.0,
                "min_creatures": 15
            },
            
            # Izzet (UR) - Spells matter and tempo
            "UR": {
                "keywords": ["instant", "sorcery", "prowess", "draw", "wizard", "phoenix", "elemental", "flash", "copy"],
                "creature_weight": 0.6,
                "noncreature_weight": 1.4,
                "min_creatures": 12
            },
            
            # Golgari (BG) - Graveyard recursion and value
            "BG": {
                "keywords": ["graveyard", "deathtouch", "dredge", "scavenge", "insect", "fungus", "elf", "sacrifice", "undergrowth"],
                "creature_weight": 1.1,
                "noncreature_weight": 0.9,
                "min_creatures": 16
            },
            
            # Boros (RW) - Aggressive and go wide
            "RW": {
                "keywords": ["mentor", "attack", "equipment", "first strike", "double strike", "soldier", "warrior", "samurai", "haste"],
                "creature_weight": 1.3,
                "noncreature_weight": 0.7,
                "min_creatures": 18
            },
            
            # Simic (GU) - +1/+1 counters and card advantage
            "GU": {
                "keywords": ["adapt", "evolve", "counter", "flash", "mutate", "crab", "merfolk", "draw", "clone"],
                "creature_weight": 1.1,
                "noncreature_weight": 0.9,
                "min_creatures": 16
            },
            
            # THREE-COLOR ARCHETYPES (SHARDS/WEDGES)
            
            # Esper (WUB) - Control and artifacts
            # "WUB": {
            #     "keywords": ["artifact", "control", "exile", "draw", "thopter", "sphinx", "zombie", "counter", "vigilance"],
            #     "creature_weight": 0.7,
            #     "noncreature_weight": 1.3,
            #     "min_creatures": 12
            # },
            
            # Grixis (UBR) - Value and sacrifice
            # "UBR": {
            #     "keywords": ["discard", "sacrifice", "draw", "amass", "zombie", "devil", "dragon", "value", "damage"],
            #     "creature_weight": 0.9,
            #     "noncreature_weight": 1.1,
            #     "min_creatures": 14
            # },
            
            # Jund (BRG) - Midrange value
            # "BRG": {
            #     "keywords": ["devour", "fight", "sacrifice", "dragon", "shaman", "beast", "jund", "cascade", "value"],
            #     "creature_weight": 1.2,
            #     "noncreature_weight": 0.8,
            #     "min_creatures": 16
            # },
            
            # Naya (RGW) - Big creatures
            # "RGW": {
            #     "keywords": ["domain", "naya", "beast", "dinosaur", "cat", "trample", "vigilance", "haste", "+1/+1"],
            #     "creature_weight": 1.3,
            #     "noncreature_weight": 0.7,
            #     "min_creatures": 17
            # },
            
            # Bant (GWU) - Exalted and control
            # "GWU": {
            #     "keywords": ["exalted", "bant", "knight", "bird", "soldier", "counter", "flash", "enchantment", "flying"],
            #     "creature_weight": 1.0,
            #     "noncreature_weight": 1.0,
            #     "min_creatures": 15
            # },
            
            # Abzan (WBG) - Midrange +1/+1 counters
            "WBG": {
                "keywords": ["outlast", "abzan", "lifelink", "deathtouch", "vigilance", "counter", "toughness", "spirit", "value"],
                "creature_weight": 1.1,
                "noncreature_weight": 0.9,
                "min_creatures": 16
            },
            
            # Jeskai (URW) - Spellslinger tempo
            "URW": {
                "keywords": ["prowess", "jeskai", "monk", "flying", "first strike", "noncreature", "instant", "sorcery", "trigger"],
                "creature_weight": 0.8,
                "noncreature_weight": 1.2,
                "min_creatures": 13
            },
            
            # Sultai (BGU) - Graveyard value
            "BGU": {
                "keywords": ["delve", "sultai", "zombie", "snake", "naga", "self-mill", "graveyard", "deathtouch", "value"],
                "creature_weight": 0.9,
                "noncreature_weight": 1.1,
                "min_creatures": 14
            },
            
            # Mardu (RWB) - Aggressive warriors
            "RWB": {
                "keywords": ["dash", "mardu", "warrior", "knight", "goblin", "haste", "first strike", "lifelink", "raid"],
                "creature_weight": 1.2,
                "noncreature_weight": 0.8,
                "min_creatures": 17
            },
            
            # Temur (GUR) - Big spells and creatures
            "GUR": {
                "keywords": ["ferocious", "temur", "flash", "elemental", "shaman", "draw", "power", "trample", "instants"],
                "creature_weight": 1.0,
                "noncreature_weight": 1.0,
                "min_creatures": 15
            },
            
            # MONO-COLOR ARCHETYPES
            
            # Mono White - Go wide
            "MONO_W": {
                "keywords": ["vigilance", "lifelink", "enchantment", "soldier", "knight", "cleric", "human", "angel", "equipment"],
                "creature_weight": 1.2,
                "noncreature_weight": 0.8,
                "min_creatures": 18
            },
            
            # Mono Blue - Tempo and control
            "MONO_U": {
                "keywords": ["counter", "draw", "flash", "flying", "bounce", "wizard", "merfolk", "illusion", "artifact"],
                "creature_weight": 0.7,
                "noncreature_weight": 1.3,
                "min_creatures": 12
            },
            
            # Mono Black - Sacrifice and removal
            "MONO_B": {
                "keywords": ["destroy", "sacrifice", "discard", "zombie", "vampire", "demon", "deathtouch", "drain", "removal"],
                "creature_weight": 1.0,
                "noncreature_weight": 1.0,
                "min_creatures": 15
            },
            
            # Mono Red - Aggro
            "MONO_R": {
                "keywords": ["damage", "haste", "goblin", "elemental", "dragon", "devil", "burn", "sacrifice", "attack"],
                "creature_weight": 1.3,
                "noncreature_weight": 0.7,
                "min_creatures": 19
            },
            
            # Mono Green - Ramp and big creatures
            "MONO_G": {
                "keywords": ["trample", "reach", "elf", "beast", "hydra", "wolf", "mana", "ramp", "+1/+1"],
                "creature_weight": 1.4,
                "noncreature_weight": 0.6,
                "min_creatures": 20
            },
            
            # FIVE-COLOR ARCHETYPE
            
            # Five-Color - Good stuff
            "5C": {
                "keywords": ["domain", "converge", "gate", "fixng", "ramp", "multicolor", "draw", "removal", "value"],
                "creature_weight": 1.0,
                "noncreature_weight": 1.0,
                "min_creatures": 14
            }
        }
        self.load_set_data()
    
    def load_set_data(self):
        """Load all cards from the specified set via Scryfall API"""
        url = f"https://api.scryfall.com/cards/search?q=set:{self.set_code}+is:booster"
        response = requests.get(url)
        
        if response.status_code == 200:
            data = response.json()
            self.cards_in_set = data.get("data", [])
            
            # Get all pages if there are more
            while data.get("has_more", False):
                next_page = data.get("next_page")
                response = requests.get(next_page)
                if response.status_code == 200:
                    data = response.json()
                    self.cards_in_set.extend(data.get("data", []))
                else:
                    break
                    
            # Create a more efficient data structure for the cards
            for card in self.cards_in_set:
                self.card_data[card["name"]] = {
                    "name": card["name"],
                    "mana_cost": card.get("mana_cost", ""),
                    "type_line": card.get("type_line", ""),
                    "oracle_text": card.get("oracle_text", ""),
                    "colors": card.get("colors", []),
                    "color_identity": card.get("color_identity", []),
                    "rarity": card.get("rarity", ""),
                    "cmc": card.get("cmc", 0)
                }
            
            print(f"Loaded {len(self.cards_in_set)} cards from set {self.set_code}")
        else:
            print(f"Error loading set data: {response.status_code}")
    
    def generate_sealed_pool(self):
        """Generate a sealed pool of 90 cards (6 boosters)"""
        if not self.cards_in_set:
            raise ValueError("No cards loaded. Please load set data first.")
        
        sealed_pool = []
        
        # Simplified booster pack generation - in reality, this would be more complex
        # with proper rarity distribution, but this is a reasonable approximation
        for _ in range(6):  # 6 booster packs
            commons = [card for card in self.cards_in_set if card["rarity"] == "common"]
            uncommons = [card for card in self.cards_in_set if card["rarity"] == "uncommon"]
            rares = [card for card in self.cards_in_set if card["rarity"] in ["rare", "mythic"]]
            
            # Each pack has roughly: 10 commons, 3 uncommons, 1 rare/mythic, 1 land
            pack = (
                random.sample(commons, 10) +
                random.sample(uncommons, 3) +
                random.sample(rares, 1) +
                [random.choice(self.cards_in_set)]  # Simplified land slot
            )
            
            sealed_pool.extend(pack)
        
        return sealed_pool
    
    def build_deck(self, sealed_pool, archetype="auto"):
        """
        Simulate building a 40-card deck from a sealed pool
        This method can build decks using different archetypal strategies
        
        Parameters:
        - sealed_pool: list of cards in the sealed pool
        - archetype: string identifying the deck archetype to build
                    - "auto": automatically determine best colors (default)
                    - "WU", "UB", etc: two-color archetypes
                    - "WUB", "UBR", etc: three-color archetypes
                    - "MONO_W", "MONO_U", etc: mono-color archetypes
                    - "5C": five-color archetype
        """
        # Extract only the necessary card information
        pool_data = [{
            "name": card["name"],
            "colors": card.get("colors", []),
            "cmc": card.get("cmc", 0),
            "type_line": card.get("type_line", ""),
            "rarity": card.get("rarity", ""),
            "oracle_text": card.get("oracle_text", ""),
            "mana_cost": card.get("mana_cost", "")
        } for card in sealed_pool]
        
        # Count cards by color
        color_counts = {"W": 0, "U": 0, "B": 0, "R": 0, "G": 0, "colorless": 0, "multicolor": 0}
        for card in pool_data:
            colors = card["colors"]
            if len(colors) == 0:
                color_counts["colorless"] += 1
            elif len(colors) > 1:
                color_counts["multicolor"] += 1
                # Also increment individual colors
                for color in colors:
                    color_counts[color] += 1
            else:
                color_counts[colors[0]] += 1
        
        # Determine primary colors based on archetype
        primary_colors = []
        
        if archetype == "auto":
            # Find the two colors with the most cards
            sorted_colors = sorted(
                [c for c in color_counts.keys() if c not in ["colorless", "multicolor"]],
                key=lambda c: color_counts[c], 
                reverse=True
            )
            primary_colors = sorted_colors[:2]
        elif archetype in ["WU", "UB", "BR", "RG", "GW", "WB", "UR", "BG", "RW", "GU"]:
            # Two-color archetype
            primary_colors = list(archetype)
        elif archetype in ["WUB", "UBR", "BRG", "RGW", "GWU", "WBG", "URW", "BGU", "RWB", "GUR"]:
            # Three-color archetype
            primary_colors = list(archetype)
        elif archetype.startswith("MONO_"):
            # Mono-color archetype
            primary_colors = [archetype[-1]]  # Get the color code (last character)
        elif archetype == "5C":
            # Five-color archetype
            primary_colors = ["W", "U", "B", "R", "G"]
        else:
            # Default to auto if archetype not recognized
            sorted_colors = sorted(
                [c for c in color_counts.keys() if c not in ["colorless", "multicolor"]],
                key=lambda c: color_counts[c], 
                reverse=True
            )
            primary_colors = sorted_colors[:2]
            
        print(f"Building {self.archetypes.get(archetype, 'Unknown')} deck with colors: {', '.join(primary_colors)}")
        
        # Score cards based on archetype preferences
        for card in pool_data:
            # Start with base score
            card["score"] = 0
            
            # Higher score for cards in our primary colors
            if any(color in primary_colors for color in card.get("colors", [])):
                card["score"] += 5
            
            # Even higher score if card is exactly in our colors
            if set(card.get("colors", [])) == set(primary_colors):
                card["score"] += 3
                
            # Colorless cards are good in any deck
            if len(card.get("colors", [])) == 0 and "Land" not in card["type_line"]:
                card["score"] += 3
                
            # Rarity bonus - generally rarer cards are better
            rarity_bonus = {"common": 0, "uncommon": 1, "rare": 2, "mythic": 3}
            card["score"] += rarity_bonus.get(card.get("rarity", "common"), 0)
            
            # Lower cost is generally better
            if card.get("cmc", 0) <= 3:
                card["score"] += 2
            elif card.get("cmc", 0) <= 5:
                card["score"] += 1
                
            # Card type considerations
            if "Creature" in card["type_line"]:
                card["score"] += 1  # We need creatures
            if "Removal" in card["type_line"] or any(term in card.get("oracle_text", "").lower() 
                                                   for term in ["destroy", "exile", "damage", "-", "fight"]):
                card["score"] += 2  # Removal is valuable
                
            # Archetype-specific keywords
            if archetype in self.archetype_weights:
                keywords = self.archetype_weights[archetype]["keywords"]
                oracle_text = card.get("oracle_text", "").lower()
                
                # Check for archetype-specific keywords
                for keyword in keywords:
                    if keyword in oracle_text:
                        card["score"] += 1
                
                # Apply archetype-specific weights
                if "Creature" in card["type_line"]:
                    card["score"] *= self.archetype_weights[archetype]["creature_weight"]
                else:
                    card["score"] *= self.archetype_weights[archetype]["noncreature_weight"]
            
        # Select cards in our primary colors plus colorless cards
        playable_cards = []
        for card in pool_data:
            # Include lands that produce our colors
            if "Land" in card["type_line"]:
                # For simplicity, assuming most lands in the pool are usable
                playable_cards.append(card)
                continue
                
            # Include cards of our primary colors or colorless cards
            if (len(card["colors"]) == 0 or 
                any(color in primary_colors for color in card["colors"]) or
                (all(color in primary_colors for color in card["colors"]))):
                playable_cards.append(card)
        
        # Sort by score (highest first)
        playable_cards.sort(key=lambda c: c["score"], reverse=True)
        
        # Ensure we have enough creatures (aim for 14-18 creatures typically)
        min_creatures = 14
        if archetype in self.archetype_weights:
            min_creatures = self.archetype_weights[archetype].get("min_creatures", 14)
            
        # First, take the highest scored cards up to 23
        if len(playable_cards) > 23:
            potential_cards = playable_cards[:23]
        else:
            potential_cards = playable_cards
            
        # Count creatures
        creature_count = sum(1 for card in potential_cards if "Creature" in card["type_line"])
        
        # If we don't have enough creatures, try to add more
        if creature_count < min_creatures:
            needed_creatures = min_creatures - creature_count
            
            # Find creatures in our playable cards that weren't selected
            additional_creatures = [card for card in playable_cards[23:] 
                                  if "Creature" in card["type_line"]][:needed_creatures]
            
            # Remove lowest scored non-creatures to make room for creatures
            non_creatures = [card for card in potential_cards 
                           if "Creature" not in card["type_line"]]
            non_creatures.sort(key=lambda c: c["score"])
            
            # Remove lowest scored non-creatures
            for _ in range(min(len(additional_creatures), len(non_creatures))):
                potential_cards.remove(non_creatures.pop(0))
                
            # Add better creatures
            potential_cards.extend(additional_creatures)
        
        # These are our 23 non-land cards
        selected_cards = potential_cards[:23] if len(potential_cards) > 23 else potential_cards
        
        # Add basic lands based on color distribution
        lands_needed = 40 - len(selected_cards)
        lands = []
        
        # Count mana symbols in selected cards to determine land distribution
        mana_symbols = {"W": 0, "U": 0, "B": 0, "R": 0, "G": 0}
        for card in selected_cards:
            # Look at mana costs to count color requirements
            mana_cost = card.get("mana_cost", "")
            for color in primary_colors:
                # Count color symbols in mana cost (approximate)
                mana_symbols[color] += mana_cost.count(color)
        
        # Distribute lands based on color requirements
        total_colored_symbols = sum(mana_symbols[color] for color in primary_colors)
        
        if total_colored_symbols == 0:  # Failsafe if no colored symbols
            # Equal distribution for primary colors
            if len(primary_colors) == 1:
                # Mono-color deck
                lands.extend([{"name": self.basic_land_name(primary_colors[0]), 
                              "type_line": "Basic Land"}] * lands_needed)
            else:
                # Multi-color deck, distribute evenly
                lands_per_color = lands_needed // len(primary_colors)
                for color in primary_colors:
                    lands.extend([{"name": self.basic_land_name(color), 
                                  "type_line": "Basic Land"}] * lands_per_color)
        else:
            # Distribute according to color requirements
            for color in primary_colors:
                color_ratio = mana_symbols[color] / total_colored_symbols if total_colored_symbols > 0 else 1/len(primary_colors)
                land_count = int(lands_needed * color_ratio)
                lands.extend([{"name": self.basic_land_name(color), 
                              "type_line": "Basic Land"}] * land_count)
        
        # Adjust if we don't have exactly lands_needed lands
        while len(lands) < lands_needed:
            # Add lands of the color with the most mana symbols
            most_demanding_color = max(primary_colors, key=lambda c: mana_symbols[c])
            lands.append({"name": self.basic_land_name(most_demanding_color), "type_line": "Basic Land"})
            
        while len(lands) > lands_needed:
            # Remove lands of the color with the least mana symbols
            least_demanding_color = min(primary_colors, key=lambda c: mana_symbols[c])
            for i, land in enumerate(lands):
                if land["name"] == self.basic_land_name(least_demanding_color):
                    lands.pop(i)
                    break
        
        # Combine lands and selected cards for final deck
        final_deck = selected_cards + lands
        return final_deck
    
    def basic_land_name(self, color):
        """Return the basic land name for a given color"""
        if color == "W": return "Plains"
        if color == "U": return "Island"
        if color == "B": return "Swamp"
        if color == "R": return "Mountain"
        if color == "G": return "Forest"
        return "Wastes"  # Colorless basic land
    
    def simulate_drafts(self, num_drafts=100, archetype="auto", archetype_distribution=None):
        """
        Simulate multiple drafts and collect data
        
        Parameters:
        - num_drafts: number of drafts to simulate
        - archetype: specific archetype to use for all decks
        - archetype_distribution: dict mapping archetype names to percentages 
                                (e.g., {"WU": 0.25, "UB": 0.25, "RG": 0.5})
        """
        all_decks = []
        
        # If using a distribution, validate it sums to approximately 1
        if archetype_distribution:
            total = sum(archetype_distribution.values())
            if not 0.99 <= total <= 1.01:
                print(f"Warning: Archetype distribution sums to {total}, not 1.0. Values will be normalized.")
                # Normalize values
                archetype_distribution = {k: v/total for k, v in archetype_distribution.items()}
        
        for i in tqdm(range(num_drafts), desc="Simulating Drafts"):
            sealed_pool = self.generate_sealed_pool()
            
            # Determine which archetype to use for this draft
            current_archetype = archetype
            if archetype_distribution:
                # Choose a random archetype based on the distribution
                r = random.random()
                cumulative = 0
                for arch, prob in archetype_distribution.items():
                    cumulative += prob
                    if r <= cumulative:
                        current_archetype = arch
                        break
            
            deck = self.build_deck(sealed_pool, current_archetype)
            
            # Add metadata about the deck
            for card in deck:
                card["archetype"] = current_archetype
                card["draft_number"] = i
                
            all_decks.append(deck)
            # No need for sleep here since we're not making API calls during simulation
        
        return all_decks
    
    def analyze_drafts(self, decks):
        """Analyze the drafted decks using pandas"""
        # Flatten the data for analysis
        card_records = []
        
        for deck_index, deck in enumerate(decks):
            for card in deck:
                # Skip basic lands for analysis
                if card["name"] in ["Plains", "Island", "Swamp", "Mountain", "Forest", "Wastes"]:
                    continue
                    
                record = {
                    "deck_id": deck_index,
                    "card_name": card["name"],
                    "type_line": card.get("type_line", "Unknown"),
                    "archetype": card.get("archetype", "auto"),
                    "draft_number": card.get("draft_number", 0)
                }
                
                # Add color information if available
                if "colors" in card:
                    record["colors"] = ",".join(card["colors"]) if card["colors"] else "Colorless"
                    record["color_count"] = len(card["colors"])
                else:
                    record["colors"] = "Basic Land" if "Land" in card.get("type_line", "") else "Unknown"
                    record["color_count"] = 0
                
                # Add other card attributes if available
                for attr in ["cmc", "rarity", "score"]:
                    if attr in card:
                        record[attr] = card[attr]
                
                card_records.append(record)
        
        # Create DataFrame
        df = pd.DataFrame(card_records)
        
        # Analyze the data
        analysis = {}
        
        # Card frequency
        card_counts = df["card_name"].value_counts()
        analysis["most_common_cards"] = card_counts.head(20).to_dict()
        
        # Color distribution
        if "colors" in df.columns:
            color_counts = df["colors"].value_counts()
            analysis["color_distribution"] = color_counts.to_dict()
        
        # Card type distribution
        df["main_type"] = df["type_line"].apply(lambda x: x.split("—")[0].strip() if isinstance(x, str) else "Unknown")
        type_counts = df["main_type"].value_counts()
        analysis["type_distribution"] = type_counts.to_dict()
        
        # Mana curve analysis
        if "cmc" in df.columns:
            mana_curve = df.groupby("cmc").size()
            analysis["mana_curve"] = mana_curve.to_dict()
        
        # Rarity distribution
        if "rarity" in df.columns:
            rarity_counts = df["rarity"].value_counts()
            analysis["rarity_distribution"] = rarity_counts.to_dict()
            
        # Archetype analysis (if we used multiple archetypes)
        if "archetype" in df.columns and df["archetype"].nunique() > 1:
            archetype_counts = df.groupby(["deck_id", "archetype"]).size().reset_index(name="count")
            archetype_counts = archetype_counts["archetype"].value_counts()
            analysis["archetype_distribution"] = archetype_counts.to_dict()
            
            # Analyze each archetype separately
            for archetype in df["archetype"].unique():
                archetype_df = df[df["archetype"] == archetype]
                
                # Most common cards in this archetype
                arch_card_counts = archetype_df["card_name"].value_counts()
                analysis[f"most_common_cards_{archetype}"] = arch_card_counts.head(10).to_dict()
                
                # Mana curve for this archetype
                if "cmc" in archetype_df.columns:
                    arch_mana_curve = archetype_df.groupby("cmc").size()
                    analysis[f"mana_curve_{archetype}"] = arch_mana_curve.to_dict()
        
        return df, analysis

def main():
    # Set code for the set you want to analyze
    # Example: "ONE" for Phyrexia: All Will Be One
    set_code = "tdm"
    
    # Choose an archetype or use "auto" for automatic color selection
    # Options include: "auto", "WU", "UB", "BR", "RG", "GW", "WB", "UR", "BG", "RW", "GU", 
    # "WUB", "UBR", "BRG", "RGW", "GWU", "MONO_W", "MONO_U", "MONO_B", "MONO_R", "MONO_G", "5C"
    archetype = "auto"
    
    # Or use a distribution of archetypes
    # Example: simulate 25% WU, 25% UB, 50% RG decks
    # archetype_distribution = None
    # Create a complete archetype distribution with all available archetypes
    # Comment out the ones you don't want to use
    archetype_distribution = {
        # Two-color pairs (Guilds)
        # "WU": 0.04,  # Azorius
        # "UB": 0.04,  # Dimir
        # "BR": 0.04,  # Rakdos
        # "RG": 0.04,  # Gruul
        # "GW": 0.04,  # Selesnya
        "WB": 0.04,  # Orzhov
        "UR": 0.04,  # Izzet
        "BG": 0.04,  # Golgari
        "RW": 0.04,  # Boros
        "GU": 0.04,  # Simic
        
        # Three-color combinations (Shards/Wedges)
        # "WUB": 0.03,  # Esper
        # "UBR": 0.03,  # Grixis
        # "BRG": 0.03,  # Jund
        # "RGW": 0.03,  # Naya
        # "GWU": 0.03,  # Bant
        "WBG": 0.03,  # Abzan
        "URW": 0.03,  # Jeskai
        "BGU": 0.03,  # Sultai
        "RWB": 0.03,  # Mardu
        "GUR": 0.03,  # Temur
        
        # Mono-color
        "MONO_W": 0.03,  # Mono White
        "MONO_U": 0.03,  # Mono Blue
        "MONO_B": 0.03,  # Mono Black
        "MONO_R": 0.03,  # Mono Red
        "MONO_G": 0.03,  # Mono Green
        
        # Five-color
        "5C": 0.02,  # Five Color
        
        # Auto-determine
        # "auto": 0.05   # Automatically determine best colors
    }
    
    # Initialize simulator
    simulator = DraftSimulator(set_code=set_code)
    
    # Show available archetypes
    print("Available archetypes:")
    for code, name in simulator.archetypes.items():
        print(f"- {code}: {name}")
    
    # Simulate 100 drafts
    print("Simulating 100 drafts...")
    decks = simulator.simulate_drafts(
        num_drafts=100, 
        archetype=archetype,
        archetype_distribution=archetype_distribution
    )
    
    # Analyze the results
    print("Analyzing draft data...")
    df, analysis = simulator.analyze_drafts(decks)
    
    # Save results
    df.to_csv(f"draft_data_{set_code}.csv", index=False)
    
    with open(f"draft_analysis_{set_code}.json", "w") as f:
        json.dump(analysis, f, indent=2)
    
    # Print some interesting findings
    print("\n--- Draft Analysis Results ---")
    print(f"Analyzed {len(decks)} simulated sealed decks")
    
    print("\nTop 10 Most Drafted Cards:")
    for card, count in list(analysis["most_common_cards"].items())[:10]:
        print(f"- {card}: {count} occurrences")
    
    if "color_distribution" in analysis:
        print("\nColor Distribution:")
        for color, count in analysis["color_distribution"].items():
            print(f"- {color}: {count} cards")
    
    if "mana_curve" in analysis:
        print("\nAverage Mana Curve:")
        for cmc, count in sorted(analysis["mana_curve"].items()):
            print(f"- {cmc} CMC: {count/len(decks):.1f} cards per deck")
            
    if "archetype_distribution" in analysis:
        print("\nArchetype Distribution:")
        for archetype, count in analysis["archetype_distribution"].items():
            print(f"- {archetype}: {count} decks")
    
    print(f"\nFull results saved to draft_data_{set_code}.csv and draft_analysis_{set_code}.json")

if __name__ == "__main__":
    main() 