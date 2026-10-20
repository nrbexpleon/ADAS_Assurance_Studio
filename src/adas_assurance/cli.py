import argparse,json
from pathlib import Path
from .studio import AssuranceStudio
from .synthetic import generate_campaign

def main(argv=None):
    parser=argparse.ArgumentParser(description="ADAS Assurance Studio");parser.add_argument("--frames",type=int,default=20);parser.add_argument("--seed",type=int,default=42);parser.add_argument("--output");args=parser.parse_args(argv)
    report=AssuranceStudio().run(*generate_campaign(args.frames,args.seed));text=json.dumps(report,indent=2)
    if args.output:Path(args.output).write_text(text+"\n",encoding="utf-8");print(f"Wrote {args.output}")
    else:print(text)
    return 0
if __name__=="__main__":raise SystemExit(main())
