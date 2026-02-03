from pathlib import Path
import argparse, sys, re

from typing import Any

from ruamel.yaml import YAML

from lib.dumpers import BinaryDumper, YamlDumper

yaml = YAML()
yaml.encoding = "utf-8"
yaml.preserve_quotes = True

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

    group.add_argument(
        "-r", "--reconstruct",
        action = "store",
        metavar = "PATH",
        type = Path,
        help = "parse YAML file containing achievement schema and output into encoded .bin format"
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
        
        dumper = BinaryDumper(in_file)
        data : dict[str, Any]

        try:
            data = dumper.dump()
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

        with open(out_file, "w", encoding = "utf-8") as fl:
            yaml.dump(data, fl) # type: ignore

        print(f"[INFO]\tSuccessfully extracted game achievement schema to { out_file.relative_to(Path("."), walk_up = True) }.")
   
    elif (in_file := args.reconstruct):
        if not in_file.exists():
            print("[ERROR]\tPath to schema does not exist.");
            sys.exit(1)
        
        if not re.match(r"UserGameStatsSchema_\d+.yaml", in_file.name):
            print("[ERROR]\tFile name does not conform to schema name.")
            sys.exit(1)
        
        data : dict[str, Any]

        try:
            with open(in_file, "r", encoding = "utf-8") as fl:
                data = yaml.load(fl)
        except:
            raise
        
        out_file : Path
        filename : str = in_file.name.rstrip(".yaml") + ".bin"
        
        if args.output.is_dir():
            out_file = args.output / filename
        else:
            print("[WARN]\tFile path specified; Ignoring supplied filename.")
            out_file = args.output.with_name(filename)

        dumper = YamlDumper(out_file)
        dumper.dump(data)

        print(f"[INFO]\tSuccessfully encoded game achievement schema to { out_file.relative_to(Path("."), walk_up = True) }.")

if __name__ == "__main__":
    main()