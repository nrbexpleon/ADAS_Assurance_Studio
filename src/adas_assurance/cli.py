from __future__ import annotations

import argparse
import json
from pathlib import Path

from .evidence import verify_evidence
from .io import load_campaign, save_campaign
from .studio import AssuranceStudio
from .synthetic import generate_campaign


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="ADAS Assurance Studio")
    parser.add_argument("--input", help="campaign JSON file")
    parser.add_argument("--frames", type=int, default=20)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--output", help="write the assurance report to this file")
    parser.add_argument("--write-example", help="write an example campaign and exit")
    parser.add_argument("--verify-evidence", help="verify an evidence JSON file and exit")
    return parser


def main(argv=None) -> int:
    args = _parser().parse_args(argv)
    if args.verify_evidence:
        evidence = json.loads(Path(args.verify_evidence).read_text(encoding="utf-8"))
        valid = verify_evidence(evidence)
        print("VALID" if valid else "INVALID")
        return 0 if valid else 1
    if args.write_example:
        save_campaign(args.write_example, generate_campaign(args.frames, args.seed))
        print(f"Wrote {args.write_example}")
        return 0

    if args.input:
        frames, truths, detections, observations, reviews = load_campaign(args.input)
    else:
        frames, truths, detections, observations = generate_campaign(args.frames, args.seed)
        reviews = []
    report = AssuranceStudio().run(frames, truths, detections, observations, reviews)
    text = json.dumps(report, indent=2)
    if args.output:
        Path(args.output).write_text(text + "\n", encoding="utf-8")
        print(f"Wrote {args.output}")
    else:
        print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
