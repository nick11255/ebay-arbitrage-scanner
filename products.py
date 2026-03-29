"""Product database for eBay arbitrage scanner - 185 entries with tight filtering."""

from __future__ import annotations

from typing import Optional

from types_ import ProductConfig

PRODUCTS: list[ProductConfig] = [
    # ========== VIDEO GAME CONSOLES (Group 1) ==========
    {"name": "PS5 Disc Edition", "query": "PS5 disc edition console", "exclude": ["digital", "slim", "pro", "controller", "game", "bundle pack"], "category": "gaming", "min_price": 300, "max_price": 500, "model_keywords": ["ps5", "disc"], "group": 1},
    {"name": "PS5 Digital Edition", "query": "PS5 digital edition console", "exclude": ["disc", "slim", "pro", "controller", "game"], "category": "gaming", "min_price": 250, "max_price": 450, "model_keywords": ["ps5", "digital"], "group": 1},
    {"name": "PS5 Slim", "query": "PS5 slim console", "exclude": ["pro", "controller", "game", "skin", "cover"], "category": "gaming", "min_price": 350, "max_price": 550, "model_keywords": ["ps5", "slim"], "group": 1},
    {"name": "Xbox Series X", "query": "Xbox Series X console", "exclude": ["series s", "controller", "game", "broken"], "category": "gaming", "min_price": 280, "max_price": 480, "model_keywords": ["series", "x"], "group": 1},
    {"name": "Xbox Series S", "query": "Xbox Series S console", "exclude": ["series x", "controller", "game"], "category": "gaming", "min_price": 150, "max_price": 300, "model_keywords": ["series", "s"], "group": 1},
    {"name": "Nintendo Switch OLED", "query": "Nintendo Switch OLED console", "exclude": ["lite", "v2", "game", "case", "controller"], "category": "gaming", "min_price": 250, "max_price": 400, "model_keywords": ["switch", "oled"], "group": 1},
    {"name": "Nintendo Switch Lite", "query": "Nintendo Switch Lite console", "exclude": ["oled", "game", "case"], "category": "gaming", "min_price": 100, "max_price": 220, "model_keywords": ["switch", "lite"], "group": 1},
    {"name": "Steam Deck 512GB", "query": "Steam Deck 512GB", "exclude": ["64gb", "256gb", "case", "dock", "skin"], "category": "gaming", "min_price": 300, "max_price": 550, "model_keywords": ["steam", "deck", "512"], "group": 1},
    {"name": "Steam Deck OLED", "query": "Steam Deck OLED", "exclude": ["lcd", "case", "dock", "skin"], "category": "gaming", "min_price": 400, "max_price": 650, "model_keywords": ["steam", "deck", "oled"], "group": 1},
    {"name": "PS4 Pro 1TB", "query": "PS4 Pro 1TB console", "exclude": ["slim", "controller", "game"], "category": "gaming", "min_price": 150, "max_price": 300, "model_keywords": ["ps4", "pro"], "group": 1},
    {"name": "Nintendo 3DS XL", "query": "Nintendo 3DS XL console", "exclude": ["2ds", "game", "case", "charger only"], "category": "gaming", "min_price": 80, "max_price": 250, "model_keywords": ["3ds", "xl"], "group": 1},
    {"name": "Nintendo 2DS XL", "query": "Nintendo 2DS XL console", "exclude": ["3ds", "game", "case"], "category": "gaming", "min_price": 80, "max_price": 200, "model_keywords": ["2ds", "xl"], "group": 1},
    {"name": "PS Vita OLED", "query": "PS Vita OLED 1000", "exclude": ["slim", "2000", "game", "case"], "category": "gaming", "min_price": 100, "max_price": 300, "model_keywords": ["vita", "1000"], "group": 1},
    {"name": "GameCube Console", "query": "Nintendo GameCube console", "exclude": ["game", "controller only", "cable only"], "category": "gaming", "min_price": 60, "max_price": 200, "model_keywords": ["gamecube"], "group": 1},
    {"name": "N64 Console", "query": "Nintendo 64 N64 console", "exclude": ["game", "controller only", "cable"], "category": "gaming", "min_price": 50, "max_price": 180, "model_keywords": ["n64"], "group": 1},
    {"name": "Game Boy Advance SP", "query": "Game Boy Advance SP", "exclude": ["game", "case", "charger only"], "category": "gaming", "min_price": 50, "max_price": 200, "model_keywords": ["advance", "sp"], "group": 1},
    {"name": "Sega Genesis Mini", "query": "Sega Genesis Mini console", "exclude": ["game", "cartridge", "original"], "category": "gaming", "min_price": 40, "max_price": 120, "model_keywords": ["genesis", "mini"], "group": 1},
    {"name": "ROG Ally", "query": "ASUS ROG Ally handheld", "exclude": ["case", "dock", "charger only"], "category": "gaming", "min_price": 350, "max_price": 600, "model_keywords": ["rog", "ally"], "group": 1},
    {"name": "Analogue Pocket", "query": "Analogue Pocket console", "exclude": ["case", "dock", "cartridge"], "category": "gaming", "min_price": 200, "max_price": 400, "model_keywords": ["analogue", "pocket"], "group": 1},
    {"name": "Miyoo Mini Plus", "query": "Miyoo Mini Plus handheld", "exclude": ["case", "card", "screen protector"], "category": "gaming", "min_price": 40, "max_price": 100, "model_keywords": ["miyoo", "mini"], "group": 1},
    {"name": "Xbox One X", "query": "Xbox One X console 1TB", "exclude": ["one s", "controller", "game"], "category": "gaming", "min_price": 120, "max_price": 250, "model_keywords": ["one", "x"], "group": 1},
    {"name": "PS3 Slim", "query": "PS3 Slim console", "exclude": ["super slim", "fat", "controller", "game"], "category": "gaming", "min_price": 50, "max_price": 150, "model_keywords": ["ps3", "slim"], "group": 1},
    {"name": "Wii U Console", "query": "Nintendo Wii U console 32GB", "exclude": ["wii", "game", "controller only"], "category": "gaming", "min_price": 80, "max_price": 200, "model_keywords": ["wii", "u"], "group": 1},

    # ========== VIDEO GAMES (Group 2) ==========
    {"name": "Pokemon HeartGold", "query": "Pokemon HeartGold DS authentic", "exclude": ["reproduction", "repro", "fake", "case only", "manual only"], "category": "games", "min_price": 80, "max_price": 200, "model_keywords": ["heartgold"], "group": 2},
    {"name": "Pokemon SoulSilver", "query": "Pokemon SoulSilver DS authentic", "exclude": ["reproduction", "repro", "fake", "case only"], "category": "games", "min_price": 80, "max_price": 200, "model_keywords": ["soulsilver"], "group": 2},
    {"name": "Pokemon Emerald", "query": "Pokemon Emerald GBA authentic", "exclude": ["reproduction", "repro", "fake"], "category": "games", "min_price": 80, "max_price": 220, "model_keywords": ["emerald"], "group": 2},
    {"name": "Pokemon FireRed", "query": "Pokemon FireRed GBA authentic", "exclude": ["reproduction", "repro", "fake", "leafgreen"], "category": "games", "min_price": 50, "max_price": 150, "model_keywords": ["firered"], "group": 2},
    {"name": "Chrono Trigger SNES", "query": "Chrono Trigger SNES authentic", "exclude": ["reproduction", "repro", "ds", "ps1"], "category": "games", "min_price": 100, "max_price": 350, "model_keywords": ["chrono", "trigger", "snes"], "group": 2},
    {"name": "EarthBound SNES", "query": "EarthBound SNES cartridge", "exclude": ["reproduction", "repro", "guide"], "category": "games", "min_price": 200, "max_price": 600, "model_keywords": ["earthbound", "snes"], "group": 2},
    {"name": "Fire Emblem Path of Radiance", "query": "Fire Emblem Path of Radiance GameCube", "exclude": ["reproduction", "wii"], "category": "games", "min_price": 100, "max_price": 300, "model_keywords": ["path", "radiance"], "group": 2},
    {"name": "Zelda Ocarina of Time N64", "query": "Zelda Ocarina of Time N64", "exclude": ["3ds", "reproduction", "guide"], "category": "games", "min_price": 25, "max_price": 80, "model_keywords": ["ocarina", "n64"], "group": 2},
    {"name": "Zelda Majora's Mask N64", "query": "Zelda Majora's Mask N64", "exclude": ["3ds", "reproduction"], "category": "games", "min_price": 30, "max_price": 100, "model_keywords": ["majora", "n64"], "group": 2},
    {"name": "Super Smash Bros Melee", "query": "Super Smash Bros Melee GameCube", "exclude": ["brawl", "ultimate", "64"], "category": "games", "min_price": 40, "max_price": 100, "model_keywords": ["melee", "gamecube"], "group": 2},
    {"name": "Mario Kart Double Dash", "query": "Mario Kart Double Dash GameCube", "exclude": ["wii", "switch", "8"], "category": "games", "min_price": 40, "max_price": 100, "model_keywords": ["double", "dash"], "group": 2},
    {"name": "Metroid Prime Trilogy Wii", "query": "Metroid Prime Trilogy Wii", "exclude": ["switch", "gamecube"], "category": "games", "min_price": 40, "max_price": 120, "model_keywords": ["prime", "trilogy"], "group": 2},
    {"name": "Conker's Bad Fur Day N64", "query": "Conker's Bad Fur Day N64", "exclude": ["reproduction", "xbox"], "category": "games", "min_price": 60, "max_price": 180, "model_keywords": ["conker", "n64"], "group": 2},
    {"name": "Pikmin 2 GameCube", "query": "Pikmin 2 GameCube", "exclude": ["wii", "switch", "3"], "category": "games", "min_price": 40, "max_price": 120, "model_keywords": ["pikmin", "2", "gamecube"], "group": 2},
    {"name": "Xenoblade Chronicles Wii", "query": "Xenoblade Chronicles Wii", "exclude": ["switch", "3ds", "2", "3"], "category": "games", "min_price": 30, "max_price": 90, "model_keywords": ["xenoblade", "wii"], "group": 2},
    {"name": "Silent Hill 2 PS2", "query": "Silent Hill 2 PS2", "exclude": ["3", "4", "xbox", "pc"], "category": "games", "min_price": 50, "max_price": 180, "model_keywords": ["silent", "hill", "2", "ps2"], "group": 2},
    {"name": "Persona 3 FES PS2", "query": "Persona 3 FES PS2", "exclude": ["4", "5", "portable"], "category": "games", "min_price": 30, "max_price": 80, "model_keywords": ["persona", "3", "fes"], "group": 2},
    {"name": "Castlevania SOTN PS1", "query": "Castlevania Symphony of the Night PS1", "exclude": ["ps4", "xbox", "gba"], "category": "games", "min_price": 50, "max_price": 200, "model_keywords": ["symphony", "night"], "group": 2},
    {"name": "Panzer Dragoon Saga Saturn", "query": "Panzer Dragoon Saga Sega Saturn", "exclude": ["orta", "remake", "xbox"], "category": "games", "min_price": 400, "max_price": 1200, "model_keywords": ["panzer", "dragoon", "saga"], "group": 2},
    {"name": "Mega Man X3 SNES", "query": "Mega Man X3 SNES", "exclude": ["reproduction", "gba", "ps1", "collection"], "category": "games", "min_price": 150, "max_price": 500, "model_keywords": ["mega", "man", "x3"], "group": 2},
    {"name": "Pokemon Platinum DS", "query": "Pokemon Platinum DS authentic", "exclude": ["reproduction", "repro", "fake", "case only"], "category": "games", "min_price": 60, "max_price": 160, "model_keywords": ["platinum"], "group": 2},
    {"name": "Pokemon Black 2 DS", "query": "Pokemon Black 2 DS authentic", "exclude": ["reproduction", "repro", "white", "case only"], "category": "games", "min_price": 60, "max_price": 160, "model_keywords": ["black", "2"], "group": 2},
    {"name": "Pokemon White 2 DS", "query": "Pokemon White 2 DS authentic", "exclude": ["reproduction", "repro", "black", "case only"], "category": "games", "min_price": 60, "max_price": 160, "model_keywords": ["white", "2"], "group": 2},

    # ========== APPLE PRODUCTS (Group 3) ==========
    {"name": "AirPods Pro 2nd Gen", "query": "AirPods Pro 2nd generation", "exclude": ["case only", "1st gen", "fake", "replica", "ear tips only"], "category": "apple", "min_price": 120, "max_price": 250, "model_keywords": ["airpods", "pro", "2nd"], "group": 3},
    {"name": "AirPods Max", "query": "Apple AirPods Max headphones", "exclude": ["case only", "cushion", "replica"], "category": "apple", "min_price": 250, "max_price": 500, "model_keywords": ["airpods", "max"], "group": 3},
    {"name": "iPad Pro 11 M2", "query": "iPad Pro 11 inch M2", "exclude": ["case", "pencil only", "keyboard only", "m1"], "category": "apple", "min_price": 500, "max_price": 900, "model_keywords": ["ipad", "pro", "11", "m2"], "group": 3},
    {"name": "iPad Air M1", "query": "iPad Air M1 5th generation", "exclude": ["case", "pencil only", "keyboard only"], "category": "apple", "min_price": 350, "max_price": 600, "model_keywords": ["ipad", "air", "m1"], "group": 3},
    {"name": "iPad Mini 6", "query": "iPad Mini 6th generation", "exclude": ["case", "5th", "4th", "pencil only"], "category": "apple", "min_price": 300, "max_price": 500, "model_keywords": ["ipad", "mini", "6"], "group": 3},
    {"name": "MacBook Air M2", "query": "MacBook Air M2 laptop", "exclude": ["m1", "case", "charger only"], "category": "apple", "min_price": 700, "max_price": 1200, "model_keywords": ["macbook", "air", "m2"], "group": 3},
    {"name": "MacBook Pro 14 M3", "query": "MacBook Pro 14 M3", "exclude": ["m2", "m1", "case", "charger only"], "category": "apple", "min_price": 1200, "max_price": 2200, "model_keywords": ["macbook", "pro", "14", "m3"], "group": 3},
    {"name": "Apple Watch Ultra 2", "query": "Apple Watch Ultra 2", "exclude": ["band only", "case", "1st gen", "ultra 1"], "category": "apple", "min_price": 500, "max_price": 800, "model_keywords": ["watch", "ultra", "2"], "group": 3},
    {"name": "Apple Watch Series 9", "query": "Apple Watch Series 9", "exclude": ["band only", "case", "series 8", "series 7"], "category": "apple", "min_price": 250, "max_price": 450, "model_keywords": ["watch", "series", "9"], "group": 3},
    {"name": "Apple TV 4K 3rd Gen", "query": "Apple TV 4K 3rd generation", "exclude": ["remote only", "2nd gen", "1st gen"], "category": "apple", "min_price": 80, "max_price": 180, "model_keywords": ["apple", "tv", "4k", "3rd"], "group": 3},
    {"name": "HomePod Mini", "query": "Apple HomePod Mini speaker", "exclude": ["mount", "stand", "cable only"], "category": "apple", "min_price": 50, "max_price": 110, "model_keywords": ["homepod", "mini"], "group": 3},
    {"name": "Magic Keyboard iPad Pro", "query": "Apple Magic Keyboard iPad Pro 11", "exclude": ["mac", "imac", "folio"], "category": "apple", "min_price": 150, "max_price": 300, "model_keywords": ["magic", "keyboard", "ipad"], "group": 3},
    {"name": "iPhone 14 Pro", "query": "iPhone 14 Pro unlocked", "exclude": ["max", "case", "screen protector", "13"], "category": "apple", "min_price": 500, "max_price": 900, "model_keywords": ["iphone", "14", "pro"], "group": 3},
    {"name": "iPhone 15", "query": "iPhone 15 unlocked", "exclude": ["pro", "max", "plus", "case", "14"], "category": "apple", "min_price": 500, "max_price": 850, "model_keywords": ["iphone", "15"], "group": 3},
    {"name": "Mac Mini M2", "query": "Apple Mac Mini M2", "exclude": ["m1", "intel", "stand", "hub"], "category": "apple", "min_price": 350, "max_price": 650, "model_keywords": ["mac", "mini", "m2"], "group": 3},
    {"name": "Apple Pencil 2nd Gen", "query": "Apple Pencil 2nd generation", "exclude": ["1st gen", "tip", "case", "compatible"], "category": "apple", "min_price": 60, "max_price": 130, "model_keywords": ["pencil", "2nd"], "group": 3},
    {"name": "AirTag 4 Pack", "query": "Apple AirTag 4 pack", "exclude": ["case", "holder", "keychain", "single"], "category": "apple", "min_price": 60, "max_price": 110, "model_keywords": ["airtag", "4"], "group": 3},
    {"name": "Beats Studio Pro", "query": "Beats Studio Pro headphones", "exclude": ["case", "ear cushion", "buds"], "category": "apple", "min_price": 150, "max_price": 300, "model_keywords": ["beats", "studio", "pro"], "group": 3},
    {"name": "Beats Fit Pro", "query": "Beats Fit Pro earbuds", "exclude": ["case only", "tips", "studio"], "category": "apple", "min_price": 100, "max_price": 200, "model_keywords": ["beats", "fit", "pro"], "group": 3},
    {"name": "MacBook Pro 16 M2 Pro", "query": "MacBook Pro 16 M2 Pro", "exclude": ["m1", "case", "charger only", "m2 max"], "category": "apple", "min_price": 1400, "max_price": 2500, "model_keywords": ["macbook", "pro", "16", "m2"], "group": 3},
    {"name": "iMac 24 M3", "query": "iMac 24 M3", "exclude": ["m1", "m2", "27", "stand only"], "category": "apple", "min_price": 1000, "max_price": 1800, "model_keywords": ["imac", "24", "m3"], "group": 3},
    {"name": "iPad 10th Gen", "query": "iPad 10th generation", "exclude": ["case", "9th", "8th", "pencil only", "keyboard only"], "category": "apple", "min_price": 250, "max_price": 430, "model_keywords": ["ipad", "10th"], "group": 3},
    {"name": "MacBook Air M1", "query": "MacBook Air M1 laptop", "exclude": ["m2", "case", "charger only", "intel"], "category": "apple", "min_price": 450, "max_price": 800, "model_keywords": ["macbook", "air", "m1"], "group": 3},
    {"name": "Apple Watch SE 2nd Gen", "query": "Apple Watch SE 2nd generation", "exclude": ["band only", "1st gen", "series"], "category": "apple", "min_price": 150, "max_price": 300, "model_keywords": ["watch", "se", "2nd"], "group": 3},

    # ========== GRAPHICS CARDS & PC (Group 4) ==========
    {"name": "RTX 4090", "query": "NVIDIA RTX 4090 GPU", "exclude": ["waterblock", "backplate", "mining", "fan only"], "category": "pc", "min_price": 1200, "max_price": 2200, "model_keywords": ["4090"], "group": 4},
    {"name": "RTX 4080 Super", "query": "RTX 4080 Super GPU", "exclude": ["4080", "waterblock", "mining"], "category": "pc", "min_price": 700, "max_price": 1200, "model_keywords": ["4080", "super"], "group": 4},
    {"name": "RTX 4070 Ti Super", "query": "RTX 4070 Ti Super GPU", "exclude": ["waterblock", "mining"], "category": "pc", "min_price": 500, "max_price": 900, "model_keywords": ["4070", "ti", "super"], "group": 4},
    {"name": "RTX 4070 Super", "query": "RTX 4070 Super GPU", "exclude": ["ti", "waterblock", "mining"], "category": "pc", "min_price": 400, "max_price": 700, "model_keywords": ["4070", "super"], "group": 4},
    {"name": "RTX 4060 Ti", "query": "RTX 4060 Ti GPU", "exclude": ["4060 non-ti", "waterblock", "mining"], "category": "pc", "min_price": 250, "max_price": 500, "model_keywords": ["4060", "ti"], "group": 4},
    {"name": "RX 7900 XTX", "query": "AMD RX 7900 XTX GPU", "exclude": ["7900 xt", "waterblock", "mining"], "category": "pc", "min_price": 600, "max_price": 1100, "model_keywords": ["7900", "xtx"], "group": 4},
    {"name": "RX 7800 XT", "query": "AMD RX 7800 XT GPU", "exclude": ["7900", "waterblock"], "category": "pc", "min_price": 350, "max_price": 600, "model_keywords": ["7800", "xt"], "group": 4},
    {"name": "RTX 3080 10GB", "query": "RTX 3080 10GB GPU", "exclude": ["3080 ti", "12gb", "waterblock", "mining"], "category": "pc", "min_price": 250, "max_price": 500, "model_keywords": ["3080", "10gb"], "group": 4},
    {"name": "Ryzen 7 7800X3D", "query": "AMD Ryzen 7 7800X3D CPU", "exclude": ["motherboard combo", "cooler only"], "category": "pc", "min_price": 280, "max_price": 450, "model_keywords": ["7800x3d"], "group": 4},
    {"name": "Intel i9-14900K", "query": "Intel Core i9 14900K CPU", "exclude": ["motherboard combo", "cooler only", "13900k"], "category": "pc", "min_price": 350, "max_price": 600, "model_keywords": ["14900k"], "group": 4},
    {"name": "Samsung 990 Pro 2TB", "query": "Samsung 990 Pro 2TB NVMe SSD", "exclude": ["1tb", "4tb", "heatsink only"], "category": "pc", "min_price": 120, "max_price": 220, "model_keywords": ["990", "pro", "2tb"], "group": 4},
    {"name": "Corsair Dominator 64GB DDR5", "query": "Corsair Dominator Platinum 64GB DDR5", "exclude": ["32gb", "16gb", "ddr4"], "category": "pc", "min_price": 200, "max_price": 400, "model_keywords": ["dominator", "64gb", "ddr5"], "group": 4},
    {"name": "ASUS ROG Strix Z790", "query": "ASUS ROG Strix Z790 motherboard", "exclude": ["z690", "b760", "cpu combo"], "category": "pc", "min_price": 250, "max_price": 500, "model_keywords": ["strix", "z790"], "group": 4},
    {"name": "Elgato Stream Deck XL", "query": "Elgato Stream Deck XL", "exclude": ["mini", "mk2", "pedal", "faceplates"], "category": "pc", "min_price": 100, "max_price": 250, "model_keywords": ["stream", "deck", "xl"], "group": 4},
    {"name": "Corsair 5000D Airflow", "query": "Corsair 5000D Airflow case", "exclude": ["4000d", "fan only", "panel only"], "category": "pc", "min_price": 80, "max_price": 180, "model_keywords": ["5000d", "airflow"], "group": 4},
    {"name": "NZXT Kraken X73", "query": "NZXT Kraken X73 AIO cooler", "exclude": ["x53", "x63", "fan only", "bracket"], "category": "pc", "min_price": 80, "max_price": 200, "model_keywords": ["kraken", "x73"], "group": 4},
    {"name": "Logitech G Pro X Superlight 2", "query": "Logitech G Pro X Superlight 2 mouse", "exclude": ["1", "keyboard", "headset"], "category": "pc", "min_price": 80, "max_price": 170, "model_keywords": ["superlight", "2"], "group": 4},
    {"name": "Wooting 60HE", "query": "Wooting 60HE keyboard", "exclude": ["keycaps only", "switch only"], "category": "pc", "min_price": 120, "max_price": 250, "model_keywords": ["wooting", "60he"], "group": 4},
    {"name": "RTX 3090", "query": "NVIDIA RTX 3090 GPU", "exclude": ["3090 ti", "waterblock", "mining rig"], "category": "pc", "min_price": 500, "max_price": 1000, "model_keywords": ["3090"], "group": 4},
    {"name": "RTX 4060", "query": "NVIDIA RTX 4060 GPU", "exclude": ["ti", "waterblock", "laptop"], "category": "pc", "min_price": 220, "max_price": 380, "model_keywords": ["4060"], "group": 4},
    {"name": "Intel i7-14700K", "query": "Intel Core i7 14700K CPU", "exclude": ["13700k", "motherboard combo"], "category": "pc", "min_price": 250, "max_price": 420, "model_keywords": ["14700k"], "group": 4},
    {"name": "Ryzen 9 7950X3D", "query": "AMD Ryzen 9 7950X3D CPU", "exclude": ["7900x3d", "motherboard combo"], "category": "pc", "min_price": 400, "max_price": 700, "model_keywords": ["7950x3d"], "group": 4},
    {"name": "Samsung Odyssey G9 49", "query": "Samsung Odyssey G9 49 inch monitor", "exclude": ["g7", "stand only", "arm only"], "category": "pc", "min_price": 600, "max_price": 1200, "model_keywords": ["odyssey", "g9", "49"], "group": 4},

    # ========== CAMERAS & LENSES (Group 5) ==========
    {"name": "Sony A7 IV", "query": "Sony A7 IV camera body", "exclude": ["a7iii", "a7c", "lens", "cage", "grip only"], "category": "camera", "min_price": 1500, "max_price": 2500, "model_keywords": ["a7", "iv"], "group": 5},
    {"name": "Sony A7C II", "query": "Sony A7C II camera body", "exclude": ["a7c", "lens", "case"], "category": "camera", "min_price": 1500, "max_price": 2300, "model_keywords": ["a7c", "ii"], "group": 5},
    {"name": "Canon R6 Mark II", "query": "Canon EOS R6 Mark II body", "exclude": ["r6", "lens", "grip only"], "category": "camera", "min_price": 1600, "max_price": 2600, "model_keywords": ["r6", "ii"], "group": 5},
    {"name": "Canon R5", "query": "Canon EOS R5 camera body", "exclude": ["r5c", "lens", "grip only"], "category": "camera", "min_price": 2000, "max_price": 3500, "model_keywords": ["r5"], "group": 5},
    {"name": "Nikon Z8", "query": "Nikon Z8 camera body", "exclude": ["z9", "z7", "lens", "grip"], "category": "camera", "min_price": 2800, "max_price": 4200, "model_keywords": ["z8"], "group": 5},
    {"name": "Fujifilm X-T5", "query": "Fujifilm X-T5 camera body", "exclude": ["x-t4", "x-t3", "lens", "grip"], "category": "camera", "min_price": 1100, "max_price": 1800, "model_keywords": ["x-t5"], "group": 5},
    {"name": "Fujifilm X100VI", "query": "Fujifilm X100VI camera", "exclude": ["x100v", "case", "filter", "adapter"], "category": "camera", "min_price": 1400, "max_price": 2200, "model_keywords": ["x100vi"], "group": 5},
    {"name": "GoPro Hero 12", "query": "GoPro Hero 12 Black", "exclude": ["11", "10", "mount only", "battery only", "case only"], "category": "camera", "min_price": 200, "max_price": 400, "model_keywords": ["hero", "12"], "group": 5},
    {"name": "DJI Mini 4 Pro", "query": "DJI Mini 4 Pro drone", "exclude": ["mini 3", "mini 2", "battery only", "propeller"], "category": "camera", "min_price": 600, "max_price": 1100, "model_keywords": ["mini", "4", "pro"], "group": 5},
    {"name": "DJI Mavic 3 Classic", "query": "DJI Mavic 3 Classic drone", "exclude": ["cine", "battery only", "propeller"], "category": "camera", "min_price": 800, "max_price": 1500, "model_keywords": ["mavic", "3", "classic"], "group": 5},
    {"name": "Sony 24-70mm f/2.8 GM II", "query": "Sony 24-70mm f2.8 GM II lens", "exclude": ["gm i", "tamron", "sigma", "hood only"], "category": "camera", "min_price": 1500, "max_price": 2300, "model_keywords": ["24-70", "gm", "ii"], "group": 5},
    {"name": "Sony 70-200mm f/2.8 GM II", "query": "Sony 70-200mm f2.8 GM II lens", "exclude": ["gm i", "tamron", "hood only"], "category": "camera", "min_price": 1800, "max_price": 2800, "model_keywords": ["70-200", "gm", "ii"], "group": 5},
    {"name": "Canon RF 50mm f/1.2L", "query": "Canon RF 50mm f1.2L USM lens", "exclude": ["ef", "hood only", "adapter"], "category": "camera", "min_price": 1500, "max_price": 2400, "model_keywords": ["rf", "50mm", "1.2"], "group": 5},
    {"name": "Sigma 35mm f/1.4 Art", "query": "Sigma 35mm f1.4 DG DN Art", "exclude": ["dg hsm", "mount only", "hood"], "category": "camera", "min_price": 500, "max_price": 900, "model_keywords": ["sigma", "35mm", "art"], "group": 5},
    {"name": "DJI Osmo Action 4", "query": "DJI Osmo Action 4 camera", "exclude": ["3", "mount only", "battery only"], "category": "camera", "min_price": 200, "max_price": 350, "model_keywords": ["osmo", "action", "4"], "group": 5},
    {"name": "Insta360 X4", "query": "Insta360 X4 360 camera", "exclude": ["x3", "x2", "stick only", "case only"], "category": "camera", "min_price": 350, "max_price": 550, "model_keywords": ["insta360", "x4"], "group": 5},
    {"name": "Canon RF 100-500mm", "query": "Canon RF 100-500mm f4.5-7.1L lens", "exclude": ["ef", "adapter", "hood only"], "category": "camera", "min_price": 1800, "max_price": 2800, "model_keywords": ["rf", "100-500"], "group": 5},
    {"name": "DJI Air 3", "query": "DJI Air 3 drone", "exclude": ["air 2s", "air 2", "battery only", "propeller"], "category": "camera", "min_price": 700, "max_price": 1200, "model_keywords": ["air", "3"], "group": 5},
    {"name": "Sony ZV-E1", "query": "Sony ZV-E1 camera body", "exclude": ["zv-e10", "lens", "grip", "case"], "category": "camera", "min_price": 1500, "max_price": 2300, "model_keywords": ["zv-e1"], "group": 5},
    {"name": "Nikon Z 50mm f/1.2 S", "query": "Nikon Z 50mm f1.2 S lens", "exclude": ["f1.8", "f1.4", "hood only"], "category": "camera", "min_price": 1500, "max_price": 2200, "model_keywords": ["nikon", "50mm", "1.2"], "group": 5},
    {"name": "Fujifilm XF 56mm f/1.2 R WR", "query": "Fujifilm XF 56mm f1.2 R WR", "exclude": ["old version", "hood only"], "category": "camera", "min_price": 700, "max_price": 1100, "model_keywords": ["fujifilm", "56mm", "1.2"], "group": 5},
    {"name": "DJI Pocket 3", "query": "DJI Osmo Pocket 3 camera", "exclude": ["pocket 2", "mount only", "case only"], "category": "camera", "min_price": 350, "max_price": 600, "model_keywords": ["pocket", "3"], "group": 5},
    {"name": "Rode Wireless GO II", "query": "Rode Wireless GO II microphone", "exclude": ["go i", "case only", "clip only"], "category": "camera", "min_price": 150, "max_price": 300, "model_keywords": ["wireless", "go", "ii"], "group": 5},

    # ========== SNEAKERS & STREETWEAR (Group 6) ==========
    {"name": "Jordan 1 Retro High OG", "query": "Air Jordan 1 Retro High OG new", "exclude": ["mid", "low", "gs", "kid", "used", "rep", "replica"], "category": "sneakers", "min_price": 120, "max_price": 400, "model_keywords": ["jordan", "1", "high", "og"], "group": 6},
    {"name": "Jordan 4 Retro", "query": "Air Jordan 4 Retro new", "exclude": ["gs", "kid", "used", "rep", "replica"], "category": "sneakers", "min_price": 150, "max_price": 500, "model_keywords": ["jordan", "4", "retro"], "group": 6},
    {"name": "Jordan 3 Retro", "query": "Air Jordan 3 Retro new", "exclude": ["gs", "kid", "used", "rep", "replica"], "category": "sneakers", "min_price": 120, "max_price": 400, "model_keywords": ["jordan", "3", "retro"], "group": 6},
    {"name": "Jordan 11 Retro", "query": "Air Jordan 11 Retro new", "exclude": ["low", "gs", "kid", "used", "rep"], "category": "sneakers", "min_price": 150, "max_price": 450, "model_keywords": ["jordan", "11"], "group": 6},
    {"name": "Nike Dunk Low", "query": "Nike Dunk Low new", "exclude": ["high", "mid", "gs", "kid", "used", "rep"], "category": "sneakers", "min_price": 80, "max_price": 300, "model_keywords": ["dunk", "low"], "group": 6},
    {"name": "Nike SB Dunk Low", "query": "Nike SB Dunk Low new", "exclude": ["high", "gs", "kid", "used", "rep"], "category": "sneakers", "min_price": 100, "max_price": 400, "model_keywords": ["sb", "dunk", "low"], "group": 6},
    {"name": "Yeezy 350 V2", "query": "adidas Yeezy Boost 350 V2 new", "exclude": ["v1", "used", "rep", "replica", "kid"], "category": "sneakers", "min_price": 150, "max_price": 400, "model_keywords": ["yeezy", "350", "v2"], "group": 6},
    {"name": "Yeezy Slide", "query": "adidas Yeezy Slide new", "exclude": ["used", "rep", "replica", "kid"], "category": "sneakers", "min_price": 80, "max_price": 250, "model_keywords": ["yeezy", "slide"], "group": 6},
    {"name": "New Balance 550", "query": "New Balance 550 new", "exclude": ["used", "kid", "rep"], "category": "sneakers", "min_price": 80, "max_price": 250, "model_keywords": ["new balance", "550"], "group": 6},
    {"name": "New Balance 2002R", "query": "New Balance 2002R new", "exclude": ["used", "kid", "rep"], "category": "sneakers", "min_price": 100, "max_price": 300, "model_keywords": ["2002r"], "group": 6},
    {"name": "Nike Air Max 1", "query": "Nike Air Max 1 new", "exclude": ["90", "95", "97", "gs", "kid", "used"], "category": "sneakers", "min_price": 80, "max_price": 300, "model_keywords": ["air", "max", "1"], "group": 6},
    {"name": "ASICS Gel-Kayano 14", "query": "ASICS Gel Kayano 14 new", "exclude": ["used", "kid"], "category": "sneakers", "min_price": 80, "max_price": 250, "model_keywords": ["kayano", "14"], "group": 6},
    {"name": "Nike Air Force 1 Low", "query": "Nike Air Force 1 Low limited new", "exclude": ["mid", "high", "gs", "kid", "used", "custom"], "category": "sneakers", "min_price": 80, "max_price": 300, "model_keywords": ["air", "force", "1", "low"], "group": 6},
    {"name": "Adidas Samba OG", "query": "adidas Samba OG new", "exclude": ["used", "kid", "classic"], "category": "sneakers", "min_price": 80, "max_price": 200, "model_keywords": ["samba", "og"], "group": 6},
    {"name": "Nike Zoom Vomero 5", "query": "Nike Zoom Vomero 5 new", "exclude": ["used", "kid"], "category": "sneakers", "min_price": 100, "max_price": 300, "model_keywords": ["vomero", "5"], "group": 6},
    {"name": "Supreme Box Logo Hoodie", "query": "Supreme Box Logo Hoodie", "exclude": ["fake", "replica", "rep", "sticker", "tee"], "category": "streetwear", "min_price": 300, "max_price": 800, "model_keywords": ["supreme", "box", "logo", "hoodie"], "group": 6},
    {"name": "Travis Scott x Nike", "query": "Travis Scott Nike new", "exclude": ["poster", "keychain", "sticker", "used", "rep"], "category": "sneakers", "min_price": 150, "max_price": 600, "model_keywords": ["travis", "scott", "nike"], "group": 6},
    {"name": "Off-White x Nike", "query": "Off-White Nike new", "exclude": ["poster", "keychain", "used", "rep", "replica"], "category": "sneakers", "min_price": 150, "max_price": 600, "model_keywords": ["off-white", "nike"], "group": 6},
    {"name": "Jordan 5 Retro", "query": "Air Jordan 5 Retro new", "exclude": ["gs", "kid", "used", "rep"], "category": "sneakers", "min_price": 120, "max_price": 400, "model_keywords": ["jordan", "5", "retro"], "group": 6},
    {"name": "Salomon XT-6", "query": "Salomon XT-6 new", "exclude": ["used", "kid"], "category": "sneakers", "min_price": 100, "max_price": 250, "model_keywords": ["salomon", "xt-6"], "group": 6},
    {"name": "Nike Kobe 6 Protro", "query": "Nike Kobe 6 Protro new", "exclude": ["used", "rep", "replica", "kid"], "category": "sneakers", "min_price": 150, "max_price": 500, "model_keywords": ["kobe", "6", "protro"], "group": 6},
    {"name": "Adidas Campus 00s", "query": "adidas Campus 00s new", "exclude": ["used", "kid"], "category": "sneakers", "min_price": 70, "max_price": 180, "model_keywords": ["campus", "00s"], "group": 6},
    {"name": "Crocs x Salehe Bembury", "query": "Crocs Salehe Bembury Pollex Clog", "exclude": ["used", "kid", "fake"], "category": "sneakers", "min_price": 80, "max_price": 250, "model_keywords": ["salehe", "bembury"], "group": 6},

    # ========== AUDIO & HEADPHONES (Group 7) ==========
    {"name": "Sony WH-1000XM5", "query": "Sony WH-1000XM5 headphones", "exclude": ["xm4", "xm3", "case only", "ear pad"], "category": "audio", "min_price": 180, "max_price": 350, "model_keywords": ["wh-1000xm5"], "group": 7},
    {"name": "Sony WF-1000XM5", "query": "Sony WF-1000XM5 earbuds", "exclude": ["xm4", "xm3", "case only", "tips only"], "category": "audio", "min_price": 150, "max_price": 300, "model_keywords": ["wf-1000xm5"], "group": 7},
    {"name": "Bose QC Ultra Headphones", "query": "Bose QuietComfort Ultra headphones", "exclude": ["earbuds", "case only", "45", "35"], "category": "audio", "min_price": 250, "max_price": 430, "model_keywords": ["quietcomfort", "ultra"], "group": 7},
    {"name": "Bose QC Ultra Earbuds", "query": "Bose QuietComfort Ultra earbuds", "exclude": ["headphones", "case only", "tips"], "category": "audio", "min_price": 180, "max_price": 330, "model_keywords": ["quietcomfort", "ultra", "earbuds"], "group": 7},
    {"name": "Sennheiser HD 660S2", "query": "Sennheiser HD 660S2 headphones", "exclude": ["660s", "650", "cable only", "pads"], "category": "audio", "min_price": 300, "max_price": 550, "model_keywords": ["660s2"], "group": 7},
    {"name": "Sennheiser Momentum 4", "query": "Sennheiser Momentum 4 wireless headphones", "exclude": ["3", "2", "case only"], "category": "audio", "min_price": 200, "max_price": 380, "model_keywords": ["momentum", "4"], "group": 7},
    {"name": "Beyerdynamic DT 1990 Pro", "query": "Beyerdynamic DT 1990 Pro headphones", "exclude": ["dt 990", "dt 770", "pads only"], "category": "audio", "min_price": 300, "max_price": 550, "model_keywords": ["dt", "1990"], "group": 7},
    {"name": "Shure SM7B", "query": "Shure SM7B microphone", "exclude": ["sm7db", "windscreen only", "mount only"], "category": "audio", "min_price": 250, "max_price": 420, "model_keywords": ["sm7b"], "group": 7},
    {"name": "Shure SM7dB", "query": "Shure SM7dB microphone", "exclude": ["sm7b", "windscreen only", "mount only"], "category": "audio", "min_price": 350, "max_price": 550, "model_keywords": ["sm7db"], "group": 7},
    {"name": "Blue Yeti X", "query": "Blue Yeti X USB microphone", "exclude": ["yeti nano", "stand only", "arm only"], "category": "audio", "min_price": 80, "max_price": 180, "model_keywords": ["yeti", "x"], "group": 7},
    {"name": "Focusrite Scarlett 2i2 4th Gen", "query": "Focusrite Scarlett 2i2 4th gen interface", "exclude": ["3rd gen", "cable only", "solo"], "category": "audio", "min_price": 100, "max_price": 200, "model_keywords": ["scarlett", "2i2", "4th"], "group": 7},
    {"name": "Universal Audio Apollo Twin X", "query": "Universal Audio Apollo Twin X interface", "exclude": ["solo", "rack", "cable only"], "category": "audio", "min_price": 500, "max_price": 1000, "model_keywords": ["apollo", "twin"], "group": 7},
    {"name": "Sonos Era 300", "query": "Sonos Era 300 speaker", "exclude": ["era 100", "mount only", "stand only"], "category": "audio", "min_price": 300, "max_price": 500, "model_keywords": ["era", "300"], "group": 7},
    {"name": "Sonos Arc", "query": "Sonos Arc soundbar", "exclude": ["beam", "ray", "mount only", "sub"], "category": "audio", "min_price": 500, "max_price": 900, "model_keywords": ["sonos", "arc"], "group": 7},
    {"name": "JBL Charge 5", "query": "JBL Charge 5 bluetooth speaker", "exclude": ["charge 4", "case only"], "category": "audio", "min_price": 80, "max_price": 180, "model_keywords": ["charge", "5"], "group": 7},
    {"name": "Marshall Stanmore III", "query": "Marshall Stanmore III speaker", "exclude": ["ii", "i", "cable only"], "category": "audio", "min_price": 250, "max_price": 400, "model_keywords": ["stanmore", "iii"], "group": 7},
    {"name": "Audeze LCD-X", "query": "Audeze LCD-X headphones", "exclude": ["lcd-2", "cable only", "pads only"], "category": "audio", "min_price": 700, "max_price": 1200, "model_keywords": ["lcd-x"], "group": 7},
    {"name": "HiFiMAN Sundara", "query": "HiFiMAN Sundara headphones", "exclude": ["ananda", "cable only", "pads"], "category": "audio", "min_price": 150, "max_price": 350, "model_keywords": ["sundara"], "group": 7},
    {"name": "FiiO M11S", "query": "FiiO M11S DAP player", "exclude": ["m11 plus", "m11 pro", "case only"], "category": "audio", "min_price": 300, "max_price": 500, "model_keywords": ["fiio", "m11s"], "group": 7},
    {"name": "Chord Mojo 2", "query": "Chord Mojo 2 DAC amp", "exclude": ["mojo 1", "poly", "case only"], "category": "audio", "min_price": 400, "max_price": 650, "model_keywords": ["chord", "mojo", "2"], "group": 7},
    {"name": "Schiit Modi Multibit", "query": "Schiit Modi Multibit DAC", "exclude": ["magni", "stack", "cable only"], "category": "audio", "min_price": 150, "max_price": 300, "model_keywords": ["modi", "multibit"], "group": 7},
    {"name": "KEF LS50 Meta", "query": "KEF LS50 Meta speakers pair", "exclude": ["wireless", "stand only", "single"], "category": "audio", "min_price": 800, "max_price": 1400, "model_keywords": ["ls50", "meta"], "group": 7},
    {"name": "Rode PodMic USB", "query": "Rode PodMic USB microphone", "exclude": ["podmic xlr", "arm only"], "category": "audio", "min_price": 100, "max_price": 200, "model_keywords": ["podmic", "usb"], "group": 7},

    # ========== COLLECTIBLES & TRADING CARDS (Group 8) ==========
    {"name": "Pokemon Booster Box 151", "query": "Pokemon 151 booster box sealed", "exclude": ["pack", "single", "etb", "opened", "japanese"], "category": "tcg", "min_price": 150, "max_price": 400, "model_keywords": ["151", "booster", "box"], "group": 8},
    {"name": "Pokemon Obsidian Flames BB", "query": "Pokemon Obsidian Flames booster box sealed", "exclude": ["pack", "single", "etb", "opened"], "category": "tcg", "min_price": 80, "max_price": 200, "model_keywords": ["obsidian", "flames", "booster"], "group": 8},
    {"name": "Pokemon Paldea Evolved BB", "query": "Pokemon Paldea Evolved booster box sealed", "exclude": ["pack", "single", "etb", "opened"], "category": "tcg", "min_price": 80, "max_price": 200, "model_keywords": ["paldea", "evolved", "booster"], "group": 8},
    {"name": "Pokemon Crown Zenith ETB", "query": "Pokemon Crown Zenith Elite Trainer Box sealed", "exclude": ["pack", "single", "opened"], "category": "tcg", "min_price": 40, "max_price": 120, "model_keywords": ["crown", "zenith", "etb"], "group": 8},
    {"name": "Pokemon Charizard UPC", "query": "Pokemon Charizard Ultra Premium Collection sealed", "exclude": ["single", "opened", "card only"], "category": "tcg", "min_price": 100, "max_price": 300, "model_keywords": ["charizard", "ultra", "premium"], "group": 8},
    {"name": "MTG Lord of the Rings Collector BB", "query": "MTG Lord of the Rings collector booster box sealed", "exclude": ["pack", "single", "set", "draft"], "category": "tcg", "min_price": 200, "max_price": 500, "model_keywords": ["lord", "rings", "collector"], "group": 8},
    {"name": "MTG Modern Horizons 3 Collector BB", "query": "MTG Modern Horizons 3 collector booster box sealed", "exclude": ["pack", "single", "play", "draft"], "category": "tcg", "min_price": 200, "max_price": 400, "model_keywords": ["horizons", "3", "collector"], "group": 8},
    {"name": "Yu-Gi-Oh 25th Anniversary Tin", "query": "Yu-Gi-Oh 25th Anniversary Tin sealed", "exclude": ["single", "opened", "card only"], "category": "tcg", "min_price": 20, "max_price": 80, "model_keywords": ["25th", "anniversary", "tin"], "group": 8},
    {"name": "Lorcana Booster Box", "query": "Disney Lorcana booster box sealed", "exclude": ["pack", "single", "opened", "starter"], "category": "tcg", "min_price": 80, "max_price": 200, "model_keywords": ["lorcana", "booster", "box"], "group": 8},
    {"name": "One Piece OP-05 Booster Box", "query": "One Piece OP-05 booster box sealed", "exclude": ["pack", "single", "opened"], "category": "tcg", "min_price": 60, "max_price": 180, "model_keywords": ["one piece", "op-05"], "group": 8},
    {"name": "LEGO Star Wars UCS AT-AT", "query": "LEGO Star Wars UCS AT-AT 75313", "exclude": ["mini", "microfighter", "instructions only"], "category": "collectibles", "min_price": 600, "max_price": 1200, "model_keywords": ["75313", "at-at"], "group": 8},
    {"name": "LEGO Millennium Falcon UCS", "query": "LEGO Millennium Falcon 75192 UCS", "exclude": ["mini", "microfighter", "instructions only"], "category": "collectibles", "min_price": 600, "max_price": 1200, "model_keywords": ["75192", "millennium"], "group": 8},
    {"name": "LEGO Technic Bugatti Chiron", "query": "LEGO Technic Bugatti Chiron 42083", "exclude": ["mini", "speed", "instructions only"], "category": "collectibles", "min_price": 300, "max_price": 700, "model_keywords": ["42083", "bugatti"], "group": 8},
    {"name": "Hot Toys Iron Man MK85", "query": "Hot Toys Iron Man Mark 85 figure", "exclude": ["helmet only", "base only", "accessories only"], "category": "collectibles", "min_price": 300, "max_price": 600, "model_keywords": ["hot toys", "mark", "85"], "group": 8},
    {"name": "Hot Toys Spider-Man", "query": "Hot Toys Spider-Man figure 1/6", "exclude": ["keychain", "base only", "accessories only"], "category": "collectibles", "min_price": 250, "max_price": 550, "model_keywords": ["hot toys", "spider-man"], "group": 8},
    {"name": "Funko Pop Grail Lot", "query": "Funko Pop grail vaulted rare lot", "exclude": ["common", "single common", "oob damaged"], "category": "collectibles", "min_price": 50, "max_price": 300, "model_keywords": ["funko", "pop", "grail"], "group": 8},
    {"name": "Dragon Ball SH Figuarts", "query": "SH Figuarts Dragon Ball Z figure", "exclude": ["stand only", "effect only", "bootleg"], "category": "collectibles", "min_price": 40, "max_price": 150, "model_keywords": ["figuarts", "dragon ball"], "group": 8},
    {"name": "Transformers Masterpiece", "query": "Transformers Masterpiece MP figure", "exclude": ["ko", "knockoff", "3rd party", "accessory only"], "category": "collectibles", "min_price": 80, "max_price": 300, "model_keywords": ["masterpiece", "mp"], "group": 8},
    {"name": "Pokemon PSA 10 Charizard", "query": "Pokemon PSA 10 Charizard graded", "exclude": ["psa 9", "psa 8", "raw", "japanese"], "category": "tcg", "min_price": 50, "max_price": 500, "model_keywords": ["psa", "10", "charizard"], "group": 8},
    {"name": "Sports Card PSA 10 Rookie", "query": "PSA 10 rookie card NBA NFL MLB", "exclude": ["psa 9", "raw", "reprint"], "category": "tcg", "min_price": 30, "max_price": 300, "model_keywords": ["psa", "10", "rookie"], "group": 8},
    {"name": "LEGO Icons Titanic", "query": "LEGO Icons Titanic 10294", "exclude": ["mini", "instructions only", "damaged"], "category": "collectibles", "min_price": 500, "max_price": 900, "model_keywords": ["10294", "titanic"], "group": 8},
    {"name": "Pokemon Temporal Forces BB", "query": "Pokemon Temporal Forces booster box sealed", "exclude": ["pack", "single", "etb", "opened"], "category": "tcg", "min_price": 80, "max_price": 180, "model_keywords": ["temporal", "forces", "booster"], "group": 8},
    {"name": "MTG Murders at Karlov Collector BB", "query": "MTG Murders Karlov Manor collector booster box sealed", "exclude": ["pack", "single", "play"], "category": "tcg", "min_price": 100, "max_price": 250, "model_keywords": ["karlov", "collector", "booster"], "group": 8},
]


def get_products_by_group(group: int) -> list[ProductConfig]:
    """Get all products in a specific scan group."""
    return [p for p in PRODUCTS if p["group"] == group]


def get_all_groups() -> dict[int, list[ProductConfig]]:
    """Get products organized by group number."""
    groups: dict[int, list[ProductConfig]] = {}
    for p in PRODUCTS:
        g: int = p["group"]
        if g not in groups:
            groups[g] = []
        groups[g].append(p)
    return groups


def get_product_by_name(name: str) -> Optional[ProductConfig]:
    """Find a product by exact or partial name match."""
    name_lower: str = name.lower()
    for p in PRODUCTS:
        if p["name"].lower() == name_lower:
            return p
    for p in PRODUCTS:
        if name_lower in p["name"].lower():
            return p
    return None


def get_products_by_category(category: str) -> list[ProductConfig]:
    """Get all products in a category."""
    return [p for p in PRODUCTS if p["category"] == category]


def get_group_summary() -> str:
    """Get a summary of products per group."""
    groups: dict[int, list[ProductConfig]] = get_all_groups()
    lines: list[str] = []
    for g in sorted(groups.keys()):
        products: list[ProductConfig] = groups[g]
        categories: set[str] = set(p["category"] for p in products)
        lines.append(
            f"Group {g}: {len(products)} products ({', '.join(sorted(categories))})"
        )
    lines.append(f"\nTotal: {len(PRODUCTS)} products")
    return "\n".join(lines)
