from requests import get
from urllib.parse import urljoin

def get_repo(name: str, registry_url: str):
    req = get(urljoin(registry_url, name), verify=False)

    if not req:
        return None, req.status_code
    
    resp: dict = req.json()

    return resp, req.status_code

def parse_deps(repo: dict):
    latest = repo["dist-tags"]["latest"]
    return repo["versions"][latest].get("dependencies")

def build_deps(repo_name: str, registry_url: str, cb):
    deps = {}
    new_deps = [repo_name]

    while new_deps:
        transitive_deps = []
        for repo in new_deps:
            if repo not in deps:
                yield repo
                dep_repo, _ = get_repo(repo, registry_url)
                new_transitive_deps = list(parse_deps(dep_repo) or []) 
                deps.update({repo: new_transitive_deps})
                transitive_deps.extend(new_transitive_deps)
        new_deps = transitive_deps
    cb(deps)
