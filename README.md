# About

Meissner Lop is a dictionary-based mutation-based exploit fuzzer for XSS.

![xss](https://raw.githubusercontent.com/Arinerron/meissner/master/tests/run.gif)

# Installation
### Automatic

```bash
pip3 install meissner
```

### Manual

```
git clone https://github.com/arinerron/meissner.git
cd meissner
sudo ./setup.py install
```

# Usage

```
usage: meissner [-h] [--no-ansi] [--log-level LOG_LEVEL] [--url URL] [--dictionary DICTIONARY] [--threads THREADS] [--filter FILTER] [--engine ENGINE] [cmd [cmd ...]]

Meissner Lop - XSS Filter Bypass Exploit Fuzzer

positional arguments:
  cmd                   the command to execute, where {xss} is the injection point

optional arguments:
  -h, --help            show this help message and exit
  --no-ansi, -c         disable ANSI coloring on all output
  --log-level LOG_LEVEL, -v LOG_LEVEL
                        set logging level
  --url URL, --uri URL, -u URL
                        use a URL harness, where {xss} is the injection point
  --dictionary DICTIONARY, --dict DICTIONARY, -d DICTIONARY
                        the Meissner mutation dictionary to use
  --threads THREADS, --threads-count THREADS, -t THREADS
                        the number of threads allocated to use for engines
  --filter FILTER, -f FILTER
                        pass the input through a filter before the program
  --engine ENGINE, --browser ENGINE, -e ENGINE
                        the browser rendering engine to use
```

## General

When entering a URL, simply put the string `{xss}` where you would like to insert XSS payloads. For example:

```bash
meissner --url 'https://example.com/vulnerable.php?query={xss}'
```

Additionally, if you have a script that outputs the generated HTML, Meissner Lop can work with you. For example, if a mutation XSS CTF challenge provides source and you setup a local instance at `https://localhost:8080/xss.php`, you may use that as the URL. It is more efficient to run instances locally as HTTP requests will not have to travel across the internet.

Meissner can also provide XSS payloads through `argv` if you have an executable that generates HTML output. This option is by far the most efficient as it removes need for HTTP servers/clients and networking.

For example, if your executable is called `./give-me-flag`, you may use the tool like:

```bash
meissner -- ./give-me-flag '{xss}'
```

If the `{xss}` argument is not found in the arguments, Meissner will assume that you would like payloads to be passed through stdin/stdout.

# Limitations

- The tool does not attempt to abide by any character or length restrictions. This does not mean that it will not work for your specific XSS vulnerability, however; just that it may take longer to find something as the tool is not specifically trying to abide by restrictions.
- Meissner does not attempt to parse HTML and bypass filters in that way; rather, it is a "dumb" fuzzer and prioritizes based on cases it considers interesting. However, it can brute-force XSS challenges MUCH faster than you can. I'd recommend running this tool in the background while you manually solve challenges.
- The fuzzer may take the fun of the challenge away from you. If you are playing a CTF for fun, then solve the challenge by hand! ... unless you get some sort of odd satisfaction from using tools to solve all your problems like I do--in which case, by all means, use this tool.

# TODO
- double URL encoding

- New features
    - more intelligent fuzzing
        - detect "interesting" cases and prioritize them
    - more mutations
        - randomly pick bytes to encode with HTML entities
    - make HTTP requests more flexible
        - random user agent generation
        - `POST`, `PUT`, etc requests
        - cookies
        - proxies
        - requests from a file
    - support custom filters through Python files (use stdin/stdout)
    - if `{xss}`not found in stdin/stdout, write through stdin
    - saving and restoring progress
- Fix bugs / race conditions (search for `XXX: ` in the code!)
    - expose some of the hardcoded timeouts to the CLI
- Write documentation
- Create more / better dictionaries
- Optimizations!
