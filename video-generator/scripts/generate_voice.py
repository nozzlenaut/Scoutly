from __future__ import annotations

import json
from pathlib import Path

import soundfile as sf
from kokoro import KPipeline

FPS = 30
SPEED = 1.25
VOICE = "af_heart"


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
    story_path = project / "work" / "story.json"
    story = json.loads(story_path.read_text(encoding="utf-8"))
    scenes = story.get("scenes") or []
    if not scenes:
        raise RuntimeError("story.json contains no scenes")

    pipeline = KPipeline(lang_code="a")
    rows = []
    for index, scene in enumerate(scenes):
        path = audio_dir / f"scene-{index}.wav"
        duration_seconds = synthesize_one(pipeline, str(scene.get("tts") or scene["narration"]), path)
        frames = max(1, round((duration_seconds + 0.08) * FPS))
        row = {key: value for key, value in scene.items() if key != "tts"}
        row.update({"frames": frames, "audio": f"audio/scene-{index}.wav"})
        rows.append(row)
        print(f"scene {index}: {duration_seconds:.2f}s -> {frames} frames")

    lines = [
        "export type GeneratedScene = {",
        "  eyebrow: string;",
        "  headline: string;",
        "  subhead: string;",
        "  narration: string;",
        "  visual: string;",
        "  values: Record<string, string | number | null>;",
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
