import networkx as nx

def build_graph(scenario: dict, accidents=None) -> nx.DiGraph:
    g = nx.DiGraph()
    nodes = [
      ("Facility","시설", "facility"), ("Equipment", scenario.get("equipment","설비"), "equipment"),
      ("Process", scenario.get("process","정비 작업"), "process"), ("Worker","작업자", "worker"),
      ("Hazard", scenario.get("hazard","끼임"), "hazard"), ("RiskFactor","LOTO 상태", "factor"),
      ("Accident","과거 사고사례", "accident"), ("Control","에너지 차단·출입통제", "control"),
      ("RiskScore","위험점수", "score"), ("Alert","안전 알림", "alert")
    ]
    for node_id, label, kind in nodes:
        g.add_node(node_id, label=label, kind=kind)
    edges = [
      ("Facility","Equipment","CONTAINS"), ("Process","Equipment","USES"),
      ("Process","Worker","EXPOSES_TO"), ("Equipment","Hazard","CAN_CAUSE"),
      ("Hazard","Accident","SIMILAR_TO"), ("Accident","Control","PREVENTED_BY"),
      ("RiskFactor","RiskScore","INCREASES"), ("Control","RiskScore","REDUCES"),
      ("RiskScore","Alert","TRIGGERS")
    ]
    for source, target, relation in edges:
        g.add_edge(source,target,relation=relation)
    return g

def graph_to_dot(g: nx.DiGraph) -> str:
    lines = ["digraph G {", 'rankdir="LR";', 'node [shape="box", style="rounded,filled", fillcolor="#EAF1F8"];']
    for node, data in g.nodes(data=True):
        label = str(data.get("label", node)).replace('"', "'")
        lines.append(f'"{node}" [label="{label}"];')
    for a,b,d in g.edges(data=True):
        lines.append(f'"{a}" -> "{b}" [label="{d.get("relation","RELATED")}"];')
    lines.append("}")
    return "\n".join(lines)
