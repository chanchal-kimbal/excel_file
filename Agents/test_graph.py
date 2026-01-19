
from langgraph.graph import StateGraph, START, END
from understanding_agent import understanding_agent
from data_fetching_Agents import data_fetching_agents
from planning_agent import planning_agent
from execution_agent import execution_Agents
from report_agent import report_agents
from state import GraphState


def build_graph():
    g = StateGraph(GraphState)

    g.add_node("Understand", understanding_agent)
    g.add_node("data_fetching_agents", data_fetching_agents)
    g.add_node("planning_agent", planning_agent)
    g.add_node("execution_Agents", execution_Agents)
    g.add_node("report_agents", report_agents)

    g.add_edge(START, "Understand")
    g.add_edge("Understand", "data_fetching_agents")
    g.add_edge("data_fetching_agents", "planning_agent")
    g.add_edge("planning_agent", "execution_Agents")
    g.add_edge("execution_Agents", "report_agents")
    g.add_edge("report_agents", END)

    return g.compile()














