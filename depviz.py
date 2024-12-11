import sys
from os import getcwd, mkdir, path
from posixpath import join as pathjoin
from argparse import ArgumentParser
from subprocess import Popen, DEVNULL
from configparser import ConfigParser

from parser import get_repo, build_deps
from puml import genuml

RETRACT_LINE = "\x1b[2K\r"

def _quoted_path(path: str):
    quotes = '"' if ' ' in path else ''
    return f"{quotes}{path}{quotes}"

def main():
    parser = ArgumentParser()
    parser.add_argument('--repo', help='target npm repository name')
    parser.add_argument('--config', help='path to config file')
    parser.add_argument('--visualizer', help='path to PlantUML .jar executable')
    parser.add_argument('--registry', help='NPM registry url (default is public npm registry)', default="https://registry.npmjs.org/")
    parser.add_argument('--out', help='output directory', default="out")

    args = parser.parse_args()

    if args.config:
        ini_config = ConfigParser()
        ini_config.read(args.config)
        repo_name = ini_config.get("config", "repo")
        registry_url = ini_config.get("config", "registry")
        visualizer = ini_config.get("config", "visualizer", fallback=None)
    elif args.repo:
        repo_name = args.repo.lower()
        registry_url = args.registry
        visualizer = args.visualizer
    else:
        parser.error("you must specify config path or repository name.")
        return

    proc = Popen("java -version", stdout=DEVNULL, stderr=DEVNULL, shell=True)
    if proc.wait():
        print("Java may not be installed or not in path.")
        sys.exit(8) # software

    
    repo, status = get_repo(repo_name, registry_url)
    if repo is None:
        print(f"Repo {repo_name} not found. ({status})")
        sys.exit(17) # not found

    deps = {}
    for repo in build_deps(repo_name, registry_url, lambda d: deps.update(d)):
        print(f"{RETRACT_LINE}Fetching {repo}...", end="")
    print(f"{RETRACT_LINE}Finished.")
    
    output_dir = args.out
    cwd_path = pathjoin(*(getcwd().split("\\")))
    graph_filename = f"{repo_name}_dependencies.png"
    puml_filename = f"{repo_name}_dependencies.puml"
    puml_path = pathjoin(cwd_path, output_dir, puml_filename)
    graph_path = pathjoin(cwd_path, output_dir, graph_filename)

    print(f"Saving puml...", end="")

    if not path.exists(output_dir):
        mkdir(output_dir)

    with open(puml_path, "w") as file:
        file.write(genuml(deps))
    
    quoted_puml_path = _quoted_path(puml_path)
    quoted_graph_path = _quoted_path(graph_path)

    print(f"{RETRACT_LINE}Puml source saved at {quoted_puml_path}.")

    if visualizer:
        quoted_work_path = _quoted_path(pathjoin(output_dir, puml_filename))
        quoted_executamle_path = _quoted_path(visualizer)
        print(f"{RETRACT_LINE}Generating graph image...", end="")
        proc = Popen(f"java -jar {quoted_executamle_path} {quoted_work_path}", stdout=DEVNULL)
        if not proc.wait():
            print(f"{RETRACT_LINE}Dependency graph image saved at {quoted_graph_path}.")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        pass
