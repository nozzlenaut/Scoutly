from __future__ import annotations

import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any


def money(value: Any) -> str:
    number = float(value or 0.0)
    if abs(number - round(number)) < 0.005:
        return f"${number:,.0f}"
    return f"${number:,.2f}"


def pct(value: Any) -> str:
    number = float(value or 0.0)
    return f"{abs(number):.1f}%"


def spoken_model(text: str) -> str:
    text = re.sub(r"\bRTX\b", "R T X", text, flags=re.I)
    text = re.sub(r"\bRX\b", "R X", text, flags=re.I)
    text = re.sub(r"\bPS5\b", "P S five", text, flags=re.I)
    text = re.sub(r"\bPS4\b", "P S four", text, flags=re.I)
    text = re.sub(r"\bA(7\d0)\b", lambda m: f"[A](/ˈA/) seven {int(m.group(1)[1:])}", text)

    def four_digit(match: re.Match[str]) -> str:
        raw = match.group(0)
        first = int(raw[:2])
        last = int(raw[2:])
        if 20 <= first <= 60 and last % 10 == 0:
            return f"{first} {last}"
        return raw

    text = re.sub(r"\b[2-6]\d[0-9]0\b", four_digit, text)
    text = re.sub(r"\b(\d+)GB\b", r"\1 gigabyte", text, flags=re.I)
    return text


def scene(eyebrow: str, headline: str, subhead: str, narration: str, *, visual: str, values: dict[str, Any] | None = None, tts: str | None = None) -> dict[str, Any]:
    return {
        "eyebrow": eyebrow,
        "headline": headline,
        "subhead": subhead,
        "narration": narration,
        "tts": tts or narration,
        "visual": visual,
        "values": values or {},
    }


def build_story(selection: dict[str, Any]) -> dict[str, Any]:
    signal = selection["signal"]
    story_type = selection["story_type"]
    label = str(signal.get("product_label") or signal.get("product_id") or "Used tech")
    spoken = spoken_model(label)
    category = str(signal.get("category") or "used tech")
    current = float(signal.get("latest_median_price") or 0.0)
    prior = float(signal.get("baseline_median_price") or 0.0)
    best = float(signal.get("latest_best_price") or 0.0)
    inventory = int(signal.get("latest_eligible_count") or 0)
    move = float(signal.get("median_change_percent") or 0.0)
    inv_move = float(signal.get("inventory_change_percent") or 0.0)

    base_values = {
        "productLabel": label,
        "category": category,
        "priorMedian": prior,
        "currentMedian": current,
        "bestPrice": best,
        "inventory": inventory,
        "medianMove": move,
        "inventoryMove": inv_move,
    }

    if story_type == "price_spike_with_bargain":
        title = f"{label} Used Prices Jumped {pct(move)}... But There's a Catch"
        hook = f"{label} used prices got weird"
        scenes = [
            scene("PRICESIFT MARKET ALERT", hook.upper(), label, f"PriceSift just flagged something weird with the {label}.", visual="product", values=base_values, tts=f"PriceSift just flagged something weird with the {spoken}."),
            scene("CLEAN USED MEDIAN", f"{money(prior)}  →  {money(current)}", f"+{pct(move)}", f"Its clean used median moved from about {money(prior)} to {money(current)}. That's up {pct(move)}.", visual="price_move", values=base_values),
            scene("BUT HERE'S THE WEIRD PART", money(best), "best clean listing", f"But the cheapest clean listing is still {money(best)}.", visual="best_price", values=base_values),
            scene("NOT A ONE-LISTING FLUKE", f"{inventory} CLEAN LISTINGS", "currently observed", f"And PriceSift currently sees {inventory} clean listings, so this isn't just one random listing.", visual="inventory", values=base_values),
            scene("WHAT THE DATA ACTUALLY SAYS", "THE MEDIAN MOVED.\nTHE FLOOR DIDN'T.", "higher typical asks, cheaper inventory remains", f"So I wouldn't call this a {money(current)} product yet. Typical asking prices moved up, while cheaper inventory is still sitting underneath them.", visual="comparison", values=base_values),
            scene("BUYER TAKEAWAY", "SHOP THE LISTINGS,\nNOT THE MEDIAN.", "PriceSift tracks the clean ones.", "If you're buying one used, shop the listings, not the median. PriceSift tracks the clean ones so you don't have to sort through the junk.", visual="takeaway", values=base_values),
        ]
    elif story_type == "price_drop":
        title = f"{label} Used Prices Just Dropped {pct(move)}"
        scenes = [
            scene("PRICESIFT PRICE DROP", f"{label.upper()}\nJUST GOT CHEAPER", category, f"PriceSift just caught a real used-price drop on the {label}.", visual="product", values=base_values, tts=f"PriceSift just caught a real used-price drop on the {spoken}."),
            scene("CLEAN USED MEDIAN", f"{money(prior)}  →  {money(current)}", f"DOWN {pct(move)}", f"The clean used median fell from about {money(prior)} to {money(current)}, a drop of {pct(move)}.", visual="price_move", values=base_values),
            scene("CHEAPEST CLEAN", money(best), "best listing currently observed", f"The cheapest clean listing PriceSift sees right now is {money(best)}.", visual="best_price", values=base_values),
            scene("MARKET DEPTH", f"{inventory} CLEAN LISTINGS", "currently observed", f"There are {inventory} clean listings in the current sample, so there's enough inventory to actually shop around.", visual="inventory", values=base_values),
            scene("BUYER TAKEAWAY", "THIS ONE IS\nWORTH RECHECKING", "prices moved enough to matter", "If this was already on your used-buy list, it's worth checking again. The market moved enough to matter.", visual="comparison", values=base_values),
            scene("PRICESIFT", "CHECK THE CLEAN\nLISTINGS FIRST", "skip broken and misleading results", "PriceSift tracks clean used listings and filters out the junk before comparing price.", visual="takeaway", values=base_values),
        ]
    elif story_type == "price_spike":
        title = f"{label} Used Prices Jumped {pct(move)}"
        scenes = [
            scene("PRICESIFT PRICE SPIKE", f"{label.upper()}\nJUST GOT PRICIER", category, f"Used {label} asking prices just moved sharply higher.", visual="product", values=base_values, tts=f"Used {spoken} asking prices just moved sharply higher."),
            scene("CLEAN USED MEDIAN", f"{money(prior)}  →  {money(current)}", f"UP {pct(move)}", f"The clean used median moved from about {money(prior)} to {money(current)}, up {pct(move)}.", visual="price_move", values=base_values),
            scene("CHEAPEST CLEAN", money(best), "best listing currently observed", f"The cheapest clean listing PriceSift sees is still {money(best)}.", visual="best_price", values=base_values),
            scene("MARKET DEPTH", f"{inventory} CLEAN LISTINGS", "currently observed", f"PriceSift currently sees {inventory} clean listings in the sample.", visual="inventory", values=base_values),
            scene("BUYER TAKEAWAY", "DON'T CHASE\nTHE SPIKE", "check the floor before paying the median", "A higher median doesn't automatically mean every listing is expensive. Check the actual floor before paying up.", visual="comparison", values=base_values),
            scene("PRICESIFT", "SHOP THE CLEAN\nLISTINGS", "not the headline number", "PriceSift tracks the clean listings so you can see what buyers can actually get right now.", visual="takeaway", values=base_values),
        ]
    elif story_type == "hidden_bargain":
        title = f"A Clean {label} Is Way Below the Recent Used Median"
        gap = ((best - prior) / prior * 100.0) if prior > 0 else 0.0
        scenes = [
            scene("PRICESIFT HIDDEN BARGAIN", f"{label.upper()}\nHAS A BIG GAP", category, f"PriceSift found a clean {label} listing sitting well below its recent market level.", visual="product", values=base_values, tts=f"PriceSift found a clean {spoken} listing sitting well below its recent market level."),
            scene("RECENT MEDIAN", money(prior), "prior clean asking-price baseline", f"The recent clean median has been about {money(prior)}.", visual="price_move", values=base_values),
            scene("CURRENT BEST", money(best), f"{pct(gap)} below that baseline", f"But the current best clean listing is {money(best)}, about {pct(gap)} below that recent median.", visual="best_price", values=base_values),
            scene("MARKET DEPTH", f"{inventory} CLEAN LISTINGS", "currently observed", f"There are {inventory} clean listings in the current sample.", visual="inventory", values=base_values),
            scene("BUYER TAKEAWAY", "THIS IS WHY\nYOU CHECK THE FLOOR", "medians can hide the actual deal", "This is exactly why the cheapest trustworthy listing can matter more than the headline median.", visual="comparison", values=base_values),
            scene("PRICESIFT", "FIND THE CLEAN\nLOW PRICE", "without sorting through junk", "PriceSift filters the misleading listings first, then compares what's left.", visual="takeaway", values=base_values),
        ]
    elif story_type in {"inventory_surge", "inventory_squeeze"}:
        surge = story_type == "inventory_surge"
        direction = "UP" if surge else "DOWN"
        verb = "jumped" if surge else "dropped"
        title = f"Clean Used {label} Inventory Just {verb.title()} {pct(inv_move)}"
        scenes = [
            scene("PRICESIFT INVENTORY ALERT", f"{label.upper()}\nSUPPLY JUST MOVED", category, f"Something changed in clean used {label} inventory.", visual="product", values=base_values, tts=f"Something changed in clean used {spoken} inventory."),
            scene("CLEAN INVENTORY", f"{inventory} LISTINGS", f"{direction} {pct(inv_move)} vs recent level", f"PriceSift currently sees {inventory} clean listings, {direction.lower()} about {pct(inv_move)} versus its recent level.", visual="inventory", values=base_values),
            scene("CURRENT MEDIAN", money(current), "clean used asking price", f"The current clean used median is {money(current)}.", visual="price_move", values=base_values),
            scene("CURRENT BEST", money(best), "cheapest clean listing", f"And the cheapest clean listing currently observed is {money(best)}.", visual="best_price", values=base_values),
            scene("BUYER TAKEAWAY", "MORE SUPPLY HELPS" if surge else "LESS SUPPLY\nCAN TIGHTEN PRICES", "watch price and inventory together", "Inventory moves don't guarantee a price move, but they can change how much room buyers have to shop around.", visual="comparison", values=base_values),
            scene("PRICESIFT", "WATCH THE MARKET\nTHAT'S ACTUALLY THERE", "clean listings only", "PriceSift tracks clean used listings so supply changes don't get buried under junk results.", visual="takeaway", values=base_values),
        ]
    else:
        raise ValueError(f"Unsupported story type: {story_type}")

    return {
        "product_id": signal.get("product_id"),
        "product_label": label,
        "category": category,
        "story_type": story_type,
        "title": title,
        "description": f"PriceSift tracks clean used listings for {label} and filters out broken, misleading, wrong-model, and accessory-only results before comparing price.\n\nCurrent signal based on asking-price observations, not completed sales.\n\n#PriceSift #UsedTech",
        "selection_score": selection.get("selection_score"),
        "source_observed_at": signal.get("last_observed_at"),
        "scenes": scenes,
    }


def main() -> None:
    project = Path(__file__).resolve().parents[1]
    selection_path = project / "work" / "selection.json"
    story_path = project / "work" / "story.json"
    selection = json.loads(selection_path.read_text(encoding="utf-8"))
    story = build_story(selection)
    story_path.parent.mkdir(parents=True, exist_ok=True)
    story_path.write_text(json.dumps(story, indent=2), encoding="utf-8")
    print(f"story: {story['story_type']} | {story['title']}")


if __name__ == "__main__":
    main()
