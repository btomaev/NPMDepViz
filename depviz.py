from os import getcwd
from os.path import join as join_path
from argparse import ArgumentParser
from parser import get_repo, build_deps
from puml import genuml
from subprocess import Popen, DEVNULL

RETRACT_LINE = "\x1b[2K\r"

def _quoted_path(path: str):
    quotes = '"' if ' ' in path else ''
    return f"{quotes}{path}{quotes}"

def main():
    parser = ArgumentParser()
    parser.add_argument('repo', help='target npm repository name')
    parser.add_argument('--visualizer', help='path to PlantUML .jar executable')
    parser.add_argument('--registry', help='NPM registry url (default is public npm registry)', default="https://registry.npmjs.org/")

    args = parser.parse_args()

    proc = Popen("java -version", stdout=DEVNULL, stderr=DEVNULL, shell=True)
    if proc.wait():
        print("Java may not be installed or not in path.")
        exit(1)

    repo_name = args.repo.lower()
    repo, status = get_repo(repo_name, args.registry)
    if repo is None:
        print(f"Repo {repo_name} not found. ({status})")
        exit(1)

    deps = {}
    for repo in build_deps(repo_name, args.registry, lambda d: deps.update(d)):
        print(f"{RETRACT_LINE}Fetching {repo}...", end="")
    print(f"{RETRACT_LINE}Finished.")
    
    graph_filename = f"{repo_name}_dependencies.png"
    puml_filename = f"{repo_name}_dependencies.puml"
    puml_path = join_path(getcwd(), puml_filename)
    graph_path = join_path(getcwd(), graph_filename)

    print(f"Saving puml...", end="")

    with open(puml_path, "w") as file:
        file.write(genuml(deps))
    
    quoted_puml_path = _quoted_path(puml_path)
    quoted_graph_path = _quoted_path(graph_path)
    quoted_executamle_path = _quoted_path(args.visualizer)

    print(f"{RETRACT_LINE}Puml source saved at {quoted_puml_path}.")


    if args.visualizer:
        print(f"{RETRACT_LINE}Generating graph image...", end="")
        proc = Popen(f"java -jar {quoted_executamle_path} {puml_filename}", stdout=DEVNULL)
        proc.wait()
        print(f"{RETRACT_LINE}Dependency graph image saved at {quoted_graph_path}.")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        pass