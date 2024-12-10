def genuml(nodes: dict):
    uml = ["@startuml"]
    uml.extend([f"node \"{node}\"" for node in nodes])
    for node, deps in nodes.items():
        uml.extend([f"\"{node}\" --> \"{dep}\"" for dep in deps])
    uml.append("@enduml")
    return "\n".join(uml)