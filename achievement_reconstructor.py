from pathlib import Path
import argparse, sys, re

from typing import Any

from ruamel.yaml import YAML

from lib.parser import Parser

def main() -> None:
    argparser = argparse.ArgumentParser(prog = sys.argv[0])
    group = argparser.add_mutually_exclusive_group(required = True)

    group.add_argument(
        "-d", "--deconstruct",
        action = "store",
        metavar= "PATH",
        type = Path,
        help = "parse .bin file containing achievement schema and output into readable YAML format"
    )

    argparser.add_argument(
        "-o", "--output",
        action = "store",
        required = False,
        metavar = "PATH",
        default = ".",
        type = Path,
        help = "destination folder (defaults to working directory)"
    )

    args = argparser.parse_args(sys.argv[1:])
    in_file : Path

    if (in_file := args.deconstruct):
        if not in_file.exists():
            print("[ERROR]\tPath to schema does not exist.");
            sys.exit(1)
        
        if not re.match(r"UserGameStatsSchema_\d+.bin", in_file.name):
            print("[ERROR]\tFile name does not conform to schema name.")
            sys.exit(1)
        
        parser = Parser(in_file)
        data : dict[str, Any]

        try:
            data = parser.parse()
        except EOFError:
            print("[ERROR]\tUnexpected end of file.")
            sys.exit(1)
        except ValueError as e:
            print(f"[ERROR]\tUnexpected value found while parsing file: { e }")
            sys.exit(1)
        except NotImplementedError:
            print(f"[ERROR]\tWide strings are not supported.")
            sys.exit(1)
        
        out_file : Path
        filename : str = in_file.name.rstrip(".bin") + ".yaml"
        
        if args.output.is_dir():
            out_file = args.output / filename
        else:
            print("[WARN]\tFile path specified; Ignoring supplied filename.")
            out_file = args.output.with_name(filename)

        yaml = YAML()
        yaml.preserve_quotes = True
        yaml.dump(data, out_file) # type: ignore

        print(f"[INFO]\tSuccessfully extracted game achievement schema to { out_file.relative_to(Path("."), walk_up = True) }.")

if __name__ == "__main__":
    main()