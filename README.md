# achievement_reconstructor

A simple tool use to convert Steam's achievement schema to and from YAML to allow for editing achievement names, descriptions and icons locally.

### Configuration

As with most Python projects, the first step is to set up a virtual environment through `python -m venv` and activate it through one of the scripts in `<venv>/bin`.

Following that, one can safely install the dependencies through `pip install -r requirements.txt` as usual. This file will be kept up to date with the needed dependencies and any commits changing them will have a warning.

### Usage

```
usage: achievement_reconstructor.py [-h] (-d PATH | -r PATH) [-o PATH]

options:
  -h, --help            show this help message and exit
  -d, --deconstruct PATH
                        parse .bin file containing achievement schema and output into readable YAML format
  -r, --reconstruct PATH
                        parse YAML file containing achievement schema and output into encoded .bin format
  -o, --output PATH     destination folder (defaults to working directory)
```

**Warning:** The current tool expects both binary and YAML input files to be in the format `UserGameStatsSchema_<appId>.{bin,yaml}`, depending on whether you're *deconstructing* (`.bin` -> `.yaml`)  or *reconstructing* (`.yaml` -> `.bin`). These files can be found in:
- Windows: `C:\Program Files (x86)\Steam\appcache\stats\`
- Linux: `~/.local/share/Steam/appcache/stats/`
- Mac: `~/Library/Application Support/Steam/appcache/stats/`

Not to be confused with `UserGameStats_<userId>_<appId>.bin`, which contain the achievement progress for each local Steam user for each Steam game.

### Credits

- SamRewritten: https://github.com/PaulCombal/SamRewritten
Given work already had been put in to reverse-engineer Steam's achievement schema format, their implementation of the schema parser was used as reference for our own. The relevant file can be found [here](https://github.com/PaulCombal/SamRewritten/blob/master/src/backend/key_value.rs).