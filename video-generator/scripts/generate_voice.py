from __future__ import annotations

import json
from pathlib import Path

import soundfile as sf
from kokoro import KPipeline

FPS = 30
SPEED = 1.08
VOICE = "af_heart"

SCENES = [
    {
        "eyebrow": "PRICESIFT MARKET ALERT",
        "headline": "A770 USED PRICES\nGOT WEIRD",
        "subhead": "Intel Arc A770 16GB",
        "narration": "PriceSift just flagged something weird with the Intel Arc A seven seventy, sixteen gigabyte.",
    },
    {
        "eyebrow": "CLEAN USED MEDIAN",
        "headline": "$345.96  →  $420",
        "subhead": "+21.4%",
        "narration": "Its clean used median jumped from about three hundred forty-six dollars to four hundred twenty. That's up twenty-one point four percent.",
    },
    {
        "eyebrow": "BUT HERE'S THE WEIRD PART",
        "headline": "$299.99",
        "subhead": "best clean listing",
        "narration": "But here's the part that matters. The cheapest clean listing is still just two hundred ninety-nine dollars and ninety-nine cents.",
    },
    {
        "eyebrow": "NOT A ONE-LISTING FLUKE",
        "headline": "17 CLEAN LISTINGS",
        "subhead": "currently observed",
        "narration": "And this isn't one random listing. PriceSift currently sees seventeen clean A seven seventy listings.",
    },
    {
        "eyebrow": "WHAT THE DATA ACTUALLY SAYS",
        "headline": "THE MEDIAN MOVED.\nTHE FLOOR DIDN'T.",
        "subhead": "higher typical asks, cheaper inventory remains",
        "narration": "So I wouldn't say this suddenly became a four hundred twenty dollar card. The typical asking price moved up, while cheaper inventory is still sitting underneath it.",
    },
    {
        "eyebrow": "BUYER TAKEAWAY",
        "headline": "SHOP THE LISTINGS,\nNOT THE MEDIAN.",
        "subhead": "PriceSift tracks the clean ones.",
        "narration": "If you're buying one used, shop the listings, not the median. PriceSift tracks the clean ones so you don't have to sort through the junk.",
    },
]


def synthesize_one(pipeline: KPipeline, text: str, destination: Path) -> float:
    chunks = []
    for _graphemes, _phonemes, audio in pipeline(text, voice=VOICE, speed=SPEED, split_pattern=r"\n+"):
        chunks.append(audio)
    if not chunks:
        raise RuntimeError(f"Kokoro returned no audio for: {text}")

    import numpy as np

    combined = np.concatenate(chunks)
    sf.write(destination, combined, 24000)
    return len(combined) / 24000.0


def main() -> None:
    project = Path(__file__).resolve().parents[1]
    audio_dir = project / "public" / "audio"
    audio_dir.mkdir(parents=True, exist_ok=True)
    generated = project / "src" / "generated.ts"
    pipeline = KPipeline(lang_code="a")

    rows = []
    for index, scene in enumerate(SCENES):
        path = audio_dir / f"scene-{index}.wav"
        duration_seconds = synthesize_one(pipeline, scene["narration"], path)
        # A tiny visual tail prevents abrupt cuts without creating noticeable dead air.
        frames = max(1, round((duration_seconds + 0.08) * FPS))
        rows.append({**scene, "frames": frames, "audio": f"audio/scene-{index}.wav"})
        print(f"scene {index}: {duration_seconds:.2f}s -> {frames} frames")

    lines = [
        "export type GeneratedScene = {",
        "  eyebrow: string;",
        "  headline: string;",
        "  subhead: string;",
        "  narration: string;",
        "  frames: number;",
        "  audio: string;",
        "};",
        "",
        "export const generatedScenes: GeneratedScene[] = " + json.dumps(rows, ensure_ascii=False) + ";",
        "",
        "export const totalFrames = generatedScenes.reduce((sum, scene) => sum + scene.frames, 0);",
        "",
    ]
    generated.parent.mkdir(parents=True, exist_ok=True)
    generated.write_text("\n".join(lines), encoding="utf-8")
    print(f"total: {sum(row['frames'] for row in rows) / FPS:.2f}s")


if __name__ == "__main__":
    main()
