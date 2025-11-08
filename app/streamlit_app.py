# app/streamlit_app.py
import streamlit as st
import matplotlib.pyplot as plt
import networkx as nx
from ga_scheduler.utils import generate_random_workflow
from ga_scheduler.models import VM
from ga_scheduler.ga import ga_optimize
from ga_scheduler.simulator import simulate_schedule

# --- Page Config ---
st.set_page_config(page_title="Real-Time GA Scheduler", layout="wide")

st.title("🧬 Real-Time Genetic Algorithm Scheduler for Cloud Workflows")
st.markdown("This demo lets you generate a random workflow (DAG), visualize it, and schedule it across multiple VMs using GA.")

# Sidebar: Parameters
st.sidebar.header("⚙️ Configuration")
num_tasks = st.sidebar.slider("Number of Tasks", 4, 20, 8)
edge_prob = st.sidebar.slider("Edge Probability", 0.1, 0.9, 0.3)
pop_size = st.sidebar.slider("Population Size", 10, 100, 30)
generations = st.sidebar.slider("Generations", 5, 50, 20)
mut_prob = st.sidebar.slider("Mutation Probability", 0.0, 0.5, 0.15)
alpha = st.sidebar.number_input("Weight α (Makespan)", 0.0, 5.0, 1.0)
beta = st.sidebar.number_input("Weight β (Cost)", 0.0, 5.0, 0.3)
gamma = st.sidebar.number_input("Weight γ (Comm)", 0.0, 5.0, 0.2)

# VM Setup
st.sidebar.subheader("💻 VM Configuration")
vm_count = st.sidebar.slider("Number of VMs", 2, 5, 3)

if st.sidebar.button("🎲 Generate Workflow"):
    g, tasks = generate_random_workflow(num_tasks=num_tasks, edge_prob=edge_prob)
    st.session_state['workflow'] = (g, tasks)

# Display workflow
if 'workflow' in st.session_state:
    g, tasks = st.session_state['workflow']
    st.subheader("📊 Generated Workflow DAG")

    pos = nx.spring_layout(g, seed=42)
    plt.figure(figsize=(5, 4))
    nx.draw(g, pos, with_labels=True, node_color="skyblue", node_size=1500, arrowsize=20)
    st.pyplot(plt)

    st.markdown("### Task Details")
    for t in tasks:
        st.markdown(f"- **{t.id}** — comp={t.comp:.1f}, preds={t.preds}, type={t.ttype}")

    # Prepare VM dictionary
    vms = {}
    for i in range(vm_count):
        vid = f"VM{i+1}"
        vms[vid] = VM(
            id=vid,
            speeds=[500, 300, 200],
            cores=2,
            cost_rate=1.0 + 0.3*i,
            vtype="general",
            current_wait=0.2*i
        )

    if st.button("🚀 Run GA Scheduler"):
        with st.spinner("Running Genetic Algorithm..."):
            best_assign, score = ga_optimize(
                tasks, vms,
                pop_size=pop_size, generations=generations,
                mut_prob=mut_prob,
                alpha=alpha, beta=beta, gamma=gamma
            )

            makespan, cost, comm = simulate_schedule(tasks, vms, best_assign)
            st.success("Scheduling Complete ✅")

            # Results
            st.markdown("### 🧾 Results")
            st.markdown(f"**Best Fitness:** {score:.3f}")
            st.markdown(f"**Makespan:** {makespan:.3f} s")
            st.markdown(f"**Total Cost:** {cost:.3f}")
            st.markdown(f"**Total Communication Delay:** {comm:.3f} s")

            st.markdown("### Task → VM Assignment")
            for t in tasks:
                vm, core = best_assign[t.id]
                st.markdown(f"- {t.id} → **{vm} (core {core})**")

else:
    st.info("👈 Configure and click **'Generate Workflow'** in the sidebar to start.")
