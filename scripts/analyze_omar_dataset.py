#!/usr/bin/env python3
"""Measure speaking rate and corpus health for every Omar transcript JSON."""

from __future__ import annotations

import argparse
import json
import math
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd


DEFAULT_SOURCE = Path("/Users/mali/ai/sod-audio/processed/omar")
DEFAULT_PUNCTUATION_SUMMARY = Path(
    "/Users/mali/ai/sod-audio/pause-alignment/omar-punctuated-v1/summary.json"
)


def finite_number(value: object) -> float | None:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    return number if math.isfinite(number) else None


def percentile(values: list[float], q: float) -> float:
    return float(np.percentile(np.asarray(values, dtype=float), q))


def rounded(value: float | int | None, digits: int = 3) -> float | int | None:
    if value is None:
        return None
    return round(float(value), digits)


def audio_info(path: Path) -> dict[str, object] | None:
    try:
        import soundfile as sf

        info = sf.info(str(path))
    except (ImportError, RuntimeError):
        return None
    return {
        "samplerate": int(info.samplerate),
        "channels": int(info.channels),
        "subtype": str(info.subtype),
        "format": str(info.format),
        "duration": float(info.duration),
        "bytes": path.stat().st_size,
    }


def analyse(source_root: Path, scan_audio: bool) -> tuple[pd.DataFrame, dict[str, object]]:
    transcript_paths = sorted(source_root.glob("*/transcripts/*.json"))
    rows: list[dict[str, object]] = []
    errors: list[dict[str, str]] = []
    all_gaps: list[float] = []
    all_logprobs: list[float] = []
    audio_sample_rates: Counter[str] = Counter()
    audio_channels: Counter[str] = Counter()
    audio_subtypes: Counter[str] = Counter()
    audio_formats: Counter[str] = Counter()
    audio_bytes = 0
    audio_duration_deltas: list[float] = []
    audio_found = 0
    audio_scanned = 0
    discovered_duration_seconds = 0.0

    for transcript_path in transcript_paths:
        try:
            payload = json.loads(transcript_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            errors.append({"path": str(transcript_path), "reason": str(exc)})
            continue

        duration = finite_number(payload.get("audio_duration_secs"))
        if duration is not None and duration > 0:
            discovered_duration_seconds += duration

        recording = transcript_path.parent.parent.name
        utterance = transcript_path.stem
        audio_path = transcript_path.parent.parent / f"{utterance}.flac"
        has_audio = audio_path.is_file()
        audio_found += int(has_audio)
        if has_audio and scan_audio:
            info = audio_info(audio_path)
            if info is not None:
                audio_scanned += 1
                audio_sample_rates[str(info["samplerate"])] += 1
                audio_channels[str(info["channels"])] += 1
                audio_subtypes[str(info["subtype"])] += 1
                audio_formats[str(info["format"])] += 1
                audio_bytes += int(info["bytes"])
                if duration is not None and duration > 0:
                    audio_duration_deltas.append(abs(float(info["duration"]) - duration))

        timed_words = []
        for item in payload.get("words", []):
            if item.get("type") != "word":
                continue
            start = finite_number(item.get("start"))
            end = finite_number(item.get("end"))
            if start is None or end is None or end < start:
                continue
            timed_words.append((start, end, item))

        if duration is None or duration <= 0 or not timed_words:
            errors.append({"path": str(transcript_path), "reason": "missing duration or timed words"})
            continue

        timed_words.sort(key=lambda entry: (entry[0], entry[1]))
        word_count = len(timed_words)
        word_span = max(timed_words[-1][1] - timed_words[0][0], 0.001)
        active_word_seconds = sum(max(end - start, 0) for start, end, _ in timed_words)
        gaps = [max(0.0, current[0] - previous[1]) for previous, current in zip(timed_words, timed_words[1:])]
        logprobs = [
            value
            for _, _, item in timed_words
            if (value := finite_number(item.get("logprob"))) is not None
        ]
        all_gaps.extend(gaps)
        all_logprobs.extend(logprobs)

        transcript_text = str(payload.get("text", "")).strip()
        row = {
            "recording": recording,
            "utterance": utterance,
            "relative_json": str(transcript_path.relative_to(source_root)),
            "audio_present": has_audio,
            "duration_seconds": duration,
            "word_count": word_count,
            "wpm": word_count / duration * 60,
            "span_wpm": word_count / word_span * 60,
            "articulation_wpm": word_count / active_word_seconds * 60 if active_word_seconds else None,
            "aligned_word_seconds": active_word_seconds,
            "aligned_word_occupancy": active_word_seconds / duration,
            "pause_seconds": sum(gaps),
            "pause_0_30_count": sum(gap >= 0.30 for gap in gaps),
            "pause_0_75_count": sum(gap >= 0.75 for gap in gaps),
            "pause_1_40_count": sum(gap >= 1.40 for gap in gaps),
            "max_pause_seconds": max(gaps, default=0),
            "mean_word_logprob": float(np.mean(logprobs)) if logprobs else None,
            "low_confidence_word_count": sum(value < -1.0 for value in logprobs),
            "language_code": str(payload.get("language_code") or "unknown"),
            "language_probability": finite_number(payload.get("language_probability")),
            "text_character_count": len(transcript_text),
            "question_mark_count": transcript_text.count("?"),
            "comma_count": transcript_text.count(","),
            "period_count": transcript_text.count("."),
        }
        rows.append(row)

    frame = pd.DataFrame(rows)
    if frame.empty:
        raise RuntimeError(f"No valid transcript JSON files found beneath {source_root}")

    wpm_values = frame["wpm"].astype(float).tolist()
    q25 = percentile(wpm_values, 25)
    q75 = percentile(wpm_values, 75)
    frame["wpm_tier"] = np.select(
        [frame["wpm"] < q25, frame["wpm"] > q75],
        ["Low", "High"],
        default="Medium",
    )

    q1, q3 = q25, q75
    iqr = q3 - q1
    lower_fence = max(0.0, q1 - 1.5 * iqr)
    upper_fence = q3 + 1.5 * iqr
    frame["wpm_outlier"] = (frame["wpm"] < lower_fence) | (frame["wpm"] > upper_fence)

    tier_summary = []
    for tier in ("Low", "Medium", "High"):
        subset = frame[frame["wpm_tier"] == tier]
        tier_summary.append(
            {
                "tier": tier,
                "clips": int(len(subset)),
                "hours": rounded(subset["duration_seconds"].sum() / 3600),
                "words": int(subset["word_count"].sum()),
                "min_wpm": rounded(subset["wpm"].min(), 1),
                "median_wpm": rounded(subset["wpm"].median(), 1),
                "max_wpm": rounded(subset["wpm"].max(), 1),
            }
        )

    recording_rows = []
    for recording, subset in frame.groupby("recording", sort=False):
        recording_rows.append(
            {
                "recording": recording,
                "clips": int(len(subset)),
                "hours": rounded(subset["duration_seconds"].sum() / 3600),
                "words": int(subset["word_count"].sum()),
                "median_wpm": rounded(subset["wpm"].median(), 1),
            }
        )
    recording_rows.sort(key=lambda item: float(item["hours"]), reverse=True)

    language_rows = []
    for language, subset in frame.groupby("language_code", sort=False):
        language_rows.append(
            {
                "language": language,
                "clips": int(len(subset)),
                "hours": rounded(subset["duration_seconds"].sum() / 3600),
                "median_wpm": rounded(subset["wpm"].median(), 1),
            }
        )
    language_rows.sort(key=lambda item: item["clips"], reverse=True)

    quantiles = {
        str(q): rounded(percentile(wpm_values, q), 1)
        for q in (1, 5, 10, 25, 50, 75, 90, 95, 99)
    }
    summary: dict[str, object] = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "source_root": str(source_root),
        "methodology": {
            "wpm": "count(words where type == 'word') / audio_duration_secs * 60",
            "articulation_wpm": "timed word count / sum(word end - word start) * 60",
            "tiers": "Low is below the 25th percentile; Medium is the 25th–75th percentile; High is above the 75th percentile.",
            "outliers": "Outside Tukey fences (Q1 - 1.5×IQR, Q3 + 1.5×IQR).",
        },
        "corpus": {
            "json_files_discovered": len(transcript_paths),
            "valid_clips": int(len(frame)),
            "invalid_clips": len(errors),
            "recording_sources": int(frame["recording"].nunique()),
            "total_hours": rounded(discovered_duration_seconds / 3600),
            "wpm_eligible_hours": rounded(frame["duration_seconds"].sum() / 3600),
            "total_words": int(frame["word_count"].sum()),
            "mean_clip_seconds": rounded(frame["duration_seconds"].mean(), 2),
            "median_clip_seconds": rounded(frame["duration_seconds"].median(), 2),
            "clips_20_to_30_seconds": int(frame["duration_seconds"].between(20, 30, inclusive="both").sum()),
            "clips_20_to_30_percentage": rounded(frame["duration_seconds"].between(20, 30, inclusive="both").mean() * 100, 2),
        },
        "speaking_rate": {
            "mean_wpm": rounded(frame["wpm"].mean(), 1),
            "median_wpm": rounded(frame["wpm"].median(), 1),
            "std_wpm": rounded(frame["wpm"].std(), 1),
            "min_wpm": rounded(frame["wpm"].min(), 1),
            "max_wpm": rounded(frame["wpm"].max(), 1),
            "quantiles": quantiles,
            "low_boundary_wpm": rounded(q25, 1),
            "high_boundary_wpm": rounded(q75, 1),
            "lower_outlier_fence_wpm": rounded(lower_fence, 1),
            "upper_outlier_fence_wpm": rounded(upper_fence, 1),
            "outlier_clips": int(frame["wpm_outlier"].sum()),
            "mean_articulation_wpm": rounded(frame["articulation_wpm"].mean(), 1),
            "median_articulation_wpm": rounded(frame["articulation_wpm"].median(), 1),
        },
        "pauses": {
            "median_interword_gap_seconds": rounded(percentile(all_gaps, 50), 3) if all_gaps else None,
            "p90_interword_gap_seconds": rounded(percentile(all_gaps, 90), 3) if all_gaps else None,
            "p95_interword_gap_seconds": rounded(percentile(all_gaps, 95), 3) if all_gaps else None,
            "p99_interword_gap_seconds": rounded(percentile(all_gaps, 99), 3) if all_gaps else None,
            "gaps_at_least_0_30": int(sum(gap >= 0.30 for gap in all_gaps)),
            "gaps_at_least_0_75": int(sum(gap >= 0.75 for gap in all_gaps)),
            "gaps_at_least_1_40": int(sum(gap >= 1.40 for gap in all_gaps)),
        },
        "transcription": {
            "word_logprob_mean": rounded(float(np.mean(all_logprobs)), 4) if all_logprobs else None,
            "word_logprob_median": rounded(float(np.median(all_logprobs)), 4) if all_logprobs else None,
            "words_below_minus_1_logprob": int(sum(value < -1.0 for value in all_logprobs)),
            "words_with_logprob": len(all_logprobs),
        },
        "audio": {
            "matching_flac_files": audio_found,
            "audio_files_scanned": audio_scanned,
            "total_gib": rounded(audio_bytes / 1024**3, 2) if audio_scanned else None,
            "sample_rates": dict(audio_sample_rates),
            "channels": dict(audio_channels),
            "subtypes": dict(audio_subtypes),
            "formats": dict(audio_formats),
            "mean_json_audio_duration_delta_seconds": rounded(float(np.mean(audio_duration_deltas)), 4) if audio_duration_deltas else None,
            "max_json_audio_duration_delta_seconds": rounded(max(audio_duration_deltas), 4) if audio_duration_deltas else None,
        },
        "tiers": tier_summary,
        "languages": language_rows,
        "top_recordings_by_hours": recording_rows[:15],
        "errors": errors[:100],
    }
    return frame, summary


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--output-dir", type=Path, default=Path("data"))
    parser.add_argument("--punctuation-summary", type=Path, default=DEFAULT_PUNCTUATION_SUMMARY)
    parser.add_argument("--skip-audio-scan", action="store_true")
    args = parser.parse_args()

    frame, summary = analyse(args.source, scan_audio=not args.skip_audio_scan)
    if args.punctuation_summary.is_file():
        summary["punctuation_normalization"] = json.loads(args.punctuation_summary.read_text(encoding="utf-8"))

    args.output_dir.mkdir(parents=True, exist_ok=True)
    csv_path = args.output_dir / "omar_wpm.csv"
    summary_path = args.output_dir / "omar_dataset_summary.json"
    frame.sort_values(["recording", "utterance"]).to_csv(csv_path, index=False)
    summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Wrote {len(frame):,} clip rows to {csv_path}")
    print(f"Wrote summary to {summary_path}")


if __name__ == "__main__":
    main()
