import networkx as nx

def build_graph(scenario: dict, accidents=None) -> nx.DiGraph:
    g = nx.DiGraph()
    nodes = [
      ("Facility","시설", "facility"), ("Equipment", scenario.get("equipment","설비"), "equipment"),
      ("Process", scenario.get("process","정비 작업"), "process"), ("Worker","작업자", "worker"),
      ("Hazard", scenario.get("hazard","끼임"), "hazard"), ("RiskFactor","LOTO 상태", "factor"),
      ("Control","에너지 차단·출입통제", "control"), ("RiskScore","위험점수", "score"),
      ("Alert","안전 알림", "alert")
    ]
    for node_id, label, kind in nodes:
        g.add_node(node_id, label=label, kind=kind)
    edges = [
      ("Facility","Equipment","CONTAINS"), ("Process","Equipment","USES"),
      ("Process","Worker","EXPOSES_TO"), ("Equipment","Hazard","CAN_CAUSE"),
      ("RiskFactor","RiskScore","INCREASES"), ("Control","RiskScore","REDUCES"),
      ("RiskScore","Alert","TRIGGERS")
    ]
    for source, target, relation in edges:
        g.add_edge(source,target,relation=relation)
    if accidents is not None:
        for idx, row in accidents.head(30).iterrows():
            case_id = f"Accident_{idx}"
            title = str(row.get("title") or f"사고사례 {idx}")[:100]
            g.add_node(case_id, label=title, kind="accident")
            g.add_edge("Hazard", case_id, relation="CASE_MATCH_CANDIDATE")
            control_id = f"Control_{idx}"
            prevention = str(row.get("prevention") or "예방대책 확인 필요")[:100]
            g.add_node(control_id, label=prevention, kind="control")
            g.add_edge(case_id, control_id, relation="HAS_PREVENTION")
    return g

def graph_to_dot(g: nx.DiGraph) -> str:
    lines = ["digraph G {", 'rankdir="LR";', 'node [shape="box", style="rounded,filled", fillcolor="#EAF1F8"];']
    for node, data in g.nodes(data=True):
        label = str(data.get("label", node)).replace('"', "'").replace("\\n", " ")
        lines.append(f'"{node}" [label="{label}"];')
    for a,b,d in g.edges(data=True):
        lines.append(f'"{a}" -> "{b}" [label="{d.get("relation","RELATED")}"];')
    lines.append("}")
    return "\n".join(lines)
