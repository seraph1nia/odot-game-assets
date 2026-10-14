"""Per-role decisions for the authorized saved-source Whisperwood overhaul.

Pure metadata, not another catalog. Names are existing source landmarks; asset
identifiers/selection remain owned by the catalog. Factors are intentional art
choices, not ratios measured from the supplied illustration.
"""
BUILDINGS = {
    'archery_range': {'signature': 'rangy open lookout, oversized target/bow and arrow fletching', 'scale': (.95, 1, 1.13), 'feature': ('Lookout', 'Target', 'Arrow rack'), 'detail': 'bow_rack'},
    'arrow_tower': {'signature': 'needle-tall arrow watch, large fletched parapet and hanging supply basket', 'scale': (.91, .94, 1.15), 'feature': ('Arrow', 'Lookout'), 'detail': 'watch_basket'},
    'bakery': {'signature': 'broad low bread shelter, mushroom-like porch cap and wheat bundles', 'scale': (1.12, 1, .91), 'feature': ('Hero golden bread', 'Oven bread', 'Bread sign'), 'detail': 'bread_cap'},
    'barracks': {'signature': 'squat armored gate, broad sword shield and bundled spear standard', 'scale': (1.12, 1.04, .94), 'feature': ('Barracks heraldic', 'Raised sword', 'Spear rack'), 'detail': 'spear_standard'},
    'bombarding_tower': {'signature': 'heavy low artillery fort, broad muzzle and hooped ammunition cradle', 'scale': (1.12, 1.06, .94), 'feature': ('Cannon', 'Iron cannon', 'Thick annular', 'Muzzle', 'Recessed bore'), 'detail': 'ammo_cradle'},
    'gold_mine': {'signature': 'wide crouching portal, prominent gold cart and thick winding root arch', 'scale': (1.1, 1, .90), 'feature': ('Cart', 'Minecart', 'Gold mine raised'), 'detail': 'portal_roots'},
    'magic_academy': {'signature': 'crooked crystal scholarship tower, branching arcane crown and book shelf', 'scale': (.98, 1, 1.09), 'feature': ('Academy purple crystal', 'Academy glowing orb'), 'detail': 'arcane_crown'},
    'metal_mine': {'signature': 'tall dark ore escarpment, angular rail/cart and hoist framing', 'scale': (.99, 1.05, 1.1), 'feature': ('Iron ore load', 'Ore hoist', 'Mine cart'), 'detail': 'ore_stack'},
    'research_tower': {'signature': 'round scholarly observatory, enlarged telescope and dangling star chart', 'scale': (1.04, 1, 1.06), 'feature': ('Telescope', 'Armillary'), 'detail': 'star_chart'},
    'stone_cutter': {'signature': 'working stone crane and monumental standing-cut blocks, open wheel', 'scale': (1.02, 1.02, .98), 'feature': ('Hoist', 'Circular grindstone', 'Grinding wheel'), 'detail': 'standing_blocks'},
    'tavern': {'signature': 'wide cozy inn, oversized foamy mug and stacked hooped brewing casks', 'scale': (1.08, 1.03, .94), 'feature': ('Foamy mug', 'Sign mug', 'Sign foam'), 'detail': 'brewing_casks'},
    'town_hall': {'signature': 'tall civic bell/flanking wings, branching antler crown and processional lanterns', 'scale': (1.04, 1, 1.08), 'feature': ('Golden civic bell', 'Crown emblem'), 'detail': 'civic_crown'},
    'trade_market': {'signature': 'spreading peaked canvas stalls, large balanced scales and tied parcels', 'scale': (1.1, 1.06, .94), 'feature': ('Scale', 'Canvas canopy'), 'detail': 'market_tents'},
    'tree_house': {'signature': 'tall asymmetric living trunk, layered canopy, suspended seed baskets', 'scale': (1.05, 1, 1.11), 'feature': ('Twisting canopy', 'Faceted broadleaf'), 'detail': 'tree_baskets'},
    'weaver': {'signature': 'flowing asymmetric textile canopy, open loom and bobbin/dye arrangement', 'scale': (1.04, 1, .96), 'feature': ('Loom', 'Woven striped'), 'detail': 'flowing_cloth'},
    'woodcutter_hut': {'signature': 'industrial saw wheel and log hoist, broad lumber racks, branching roof roots', 'scale': (1.04, 1.08, 1), 'feature': ('Hero axe', 'Raised log', 'Log sign'), 'detail': 'saw_wheel'},
}
UNITS = {
    'knight': {'signature': 'proud swept plume, wide defensive shield, layered pilgrim bedroll', 'feature': ('Blue sweeping helmet plume',), 'factor': (1.16, 1.1, 1.12), 'detail': 'bedroll'},
    'mage': {'signature': 'crooked scholarly hat, low scroll satchel, brass-bound spell folio', 'feature': ('Bent purple wizard hat',), 'factor': (1.05, 1.03, 1.18), 'detail': 'scrolls'},
    'archer': {'signature': 'rangy hood/quiver, field arrows and forager seed pouches', 'feature': ('Leather arrow quiver', 'Quiver spare arrow', 'Quiver white fletching'), 'factor': (1.16, 1.08, 1.12), 'detail': 'forager'},
    'berserker': {'signature': 'broad shaggy fur, sweeping beard, bone-and-wood trophy necklace', 'feature': ('Shaggy cream fur', 'Faceted tapered orange beard', 'Swept side beard'), 'factor': (1.18, 1.09, 1.1), 'detail': 'trophies'},
    'evil_melee_unit': {'signature': 'bone-faced sentry, high angular shield, battered layered war mantle', 'feature': ('Heavy shoulder plate',), 'factor': (1.13, 1.12, 1.13), 'detail': 'war_mantle'},
    'evil_mage_unit': {'signature': 'lean horned occultist, narrow ember flame, talisman chain and vial girdle', 'feature': ('Bent dark helmet horn', 'Red horn tip'), 'factor': (1.12, 1.03, 1.18), 'detail': 'talismans'},
    'evil_ranged_unit': {'signature': 'deep skull hood, long ragged ambusher scarf, bolt case and wire bindings', 'feature': ('Open cloth hood',), 'factor': (1.05, 1.09, 1.1), 'detail': 'ambusher'},
    'evil_berserker_unit': {'signature': 'massive horned raider, broad exposed chest, jawbone trophies and fur belt', 'feature': ('Bent dark helmet horn', 'Bare barbarian chest'), 'factor': (1.2, 1.1, 1.14), 'detail': 'jaw_trophies'},
}
