from __future__ import annotations
import streamlit as st
import requests
import json
import time

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="UW MLOps · Boeing × WIC",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

  html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

  /* ── Page background ── */
  .stApp { background: #0f172a; }

  /* ── All text defaults ── */
  .stApp, .stApp p, .stApp li, .stApp span { color: #e2e8f0; }

  /* ── Sidebar ── */
  [data-testid="stSidebar"] {
    background: #1e293b !important;
    border-right: 1px solid #334155;
  }
  [data-testid="stSidebar"] * { color: #e2e8f0 !important; }
  [data-testid="stSidebar"] .stMarkdown p,
  [data-testid="stSidebar"] .stMarkdown strong { color: #f1f5f9 !important; }
  [data-testid="stSidebar"] .stCaption p { color: #94a3b8 !important; }

  /* ── Headings ── */
  h1, h2, h3, h4 { color: #f8fafc !important; }

  /* ── Input labels ── */
  label[data-testid="stWidgetLabel"] p {
    color: #cbd5e1 !important;
    font-size: 0.85rem !important;
    font-weight: 600 !important;
  }

  /* ── Text inputs & number inputs ── */
  input[type="number"], input[type="text"], input[type="password"] {
    background: #0f172a !important;
    border: 1.5px solid #475569 !important;
    color: #f1f5f9 !important;
    border-radius: 8px !important;
    font-size: 0.95rem !important;
  }
  input:focus {
    border-color: #38bdf8 !important;
    box-shadow: 0 0 0 2px rgba(56,189,248,0.2) !important;
  }

  /* ── Slider ── */
  [data-testid="stSlider"] [data-testid="stTickBarMin"],
  [data-testid="stSlider"] [data-testid="stTickBarMax"] { color: #94a3b8 !important; }

  /* ── Buttons ── */
  .stButton > button {
    background: #2563eb !important;
    color: #ffffff !important;
    border: none !important;
    border-radius: 8px !important;
    font-weight: 700 !important;
    font-size: 0.95rem !important;
    padding: 0.6rem 1.6rem !important;
    letter-spacing: 0.02em;
    transition: background 0.2s, transform 0.1s !important;
  }
  .stButton > button:hover {
    background: #1d4ed8 !important;
    transform: translateY(-1px);
  }

  /* ── Tabs ── */
  [data-testid="stTabs"] button {
    color: #94a3b8 !important;
    font-weight: 600 !important;
    font-size: 0.92rem !important;
  }
  [data-testid="stTabs"] button[aria-selected="true"] {
    color: #38bdf8 !important;
    border-bottom: 2px solid #38bdf8 !important;
  }

  /* ── DataFrames ── */
  [data-testid="stDataFrame"] { border-radius: 10px; overflow: hidden; }

  /* ── Divider ── */
  hr { border-color: #334155 !important; }

  /* ── Hero banner ── */
  .hero {
    background: linear-gradient(135deg, #1e3a5f 0%, #1e293b 50%, #1a1f3a 100%);
    border: 1px solid #334155;
    border-radius: 16px;
    padding: 2.8rem 3rem;
    margin-bottom: 2rem;
    text-align: center;
    box-shadow: 0 8px 32px rgba(0,0,0,0.4);
  }
  .hero h1 {
    font-size: 2.5rem;
    font-weight: 800;
    color: #f8fafc;
    margin: 0 0 0.5rem 0;
    letter-spacing: -0.02em;
  }
  .hero h1 span {
    background: linear-gradient(90deg, #38bdf8, #818cf8);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
  }
  .hero p {
    color: #94a3b8 !important;
    font-size: 1rem;
    margin: 0;
  }
  .badge-row {
    display: flex;
    justify-content: center;
    gap: 0.6rem;
    margin-top: 1.4rem;
    flex-wrap: wrap;
  }
  .badge {
    background: #1e40af;
    color: #bfdbfe;
    border-radius: 999px;
    padding: 0.3rem 1rem;
    font-size: 0.78rem;
    font-weight: 600;
    letter-spacing: 0.06em;
    text-transform: uppercase;
  }

  /* ── Model card ── */
  .model-card {
    background: #1e293b;
    border: 1px solid #334155;
    border-radius: 14px;
    padding: 1.6rem 2rem;
    margin-bottom: 1.5rem;
  }
  .card-title {
    font-size: 1.2rem;
    font-weight: 700;
    color: #f1f5f9;
    margin-bottom: 0.2rem;
  }
  .card-subtitle {
    font-size: 0.83rem;
    color: #94a3b8;
  }

  /* ── Result box ── */
  .result-box {
    background: #1e293b;
    border: 1px solid #334155;
    border-left: 4px solid #38bdf8;
    border-radius: 10px;
    padding: 1.4rem 1.8rem;
    margin-top: 1rem;
  }
  .result-label {
    font-size: 0.72rem;
    font-weight: 700;
    color: #38bdf8;
    text-transform: uppercase;
    letter-spacing: 0.12em;
    margin-bottom: 0.4rem;
  }
  .result-value {
    font-size: 2.6rem;
    font-weight: 800;
    color: #f8fafc;
    line-height: 1.1;
  }
  .result-sub {
    font-size: 0.82rem;
    color: #94a3b8;
    margin-top: 0.4rem;
  }

  /* ── Cluster colors ── */
  .cluster-0 { color: #34d399; }
  .cluster-1 { color: #fbbf24; }
  .cluster-2 { color: #f87171; }
  .cluster-3 { color: #a78bfa; }
  .cluster-4 { color: #22d3ee; }

  /* ── Metric items ── */
  .metric-strip { display: flex; flex-direction: column; gap: 0.6rem; margin-top: 0.5rem; }
  .metric-item {
    background: #0f172a;
    border: 1px solid #334155;
    border-radius: 10px;
    padding: 0.9rem 1rem;
    text-align: center;
  }
  .metric-item .m-val { font-size: 1.8rem; font-weight: 700; color: #38bdf8; }
  .metric-item .m-lab { font-size: 0.72rem; color: #94a3b8; text-transform: uppercase; letter-spacing: 0.08em; margin-top: 0.2rem; }

  /* ── Error box ── */
  .err-box {
    background: rgba(239,68,68,0.15);
    border: 1px solid #ef4444;
    border-radius: 10px;
    padding: 1rem 1.4rem;
    color: #fca5a5;
    font-size: 0.9rem;
    font-weight: 500;
    margin-top: 1rem;
  }

  /* ── Empty state ── */
  .empty-state {
    margin-top: 2.5rem;
    text-align: center;
    padding: 2rem;
    border: 1px dashed #334155;
    border-radius: 12px;
  }
  .empty-state .icon { font-size: 2.8rem; }
  .empty-state p { color: #94a3b8 !important; font-size: 0.9rem; margin-top: 0.5rem; }

  /* ── Sidebar footer ── */
  .sidebar-footer { color: #64748b !important; font-size: 0.72rem; text-align: center; padding-top: 0.5rem; }
</style>
""", unsafe_allow_html=True)

# ── Session state ─────────────────────────────────────────────────────────────
if "lr_history" not in st.session_state:
    st.session_state.lr_history = []
if "km_history" not in st.session_state:
    st.session_state.km_history = []

# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## ⚙️ Configuration")
    st.markdown("---")

    st.markdown("**🔑 API Authentication**")
    api_key = st.text_input(
        "Bearer Token / API Key",
        type="password",
        placeholder="Paste your Azure ML key here",
        help="Your Azure ML endpoint key. Sent as Authorization: Bearer <key>",
    )
    st.caption("Your key is never stored and only used for this session.")

    st.markdown("---")
    st.markdown("**🔗 Endpoints**")
    lr_url = st.text_input(
        "Linear Regression URL",
        value="https://taxi-mlops-endpoint.westus2.inference.ml.azure.com/score",
    )
    km_url = st.text_input(
        "K-Means URL",
        value="https://taxi-cluster-endpoint.westus2.inference.ml.azure.com/score",
    )

    st.markdown("---")
    st.markdown("**📊 Session Stats**")
    st.markdown(f"""
    <div class="metric-strip" style="flex-direction:column; gap:0.5rem;">
      <div class="metric-item">
        <div class="m-val">{len(st.session_state.lr_history)}</div>
        <div class="m-lab">Fare Predictions</div>
      </div>
      <div class="metric-item">
        <div class="m-val">{len(st.session_state.km_history)}</div>
        <div class="m-lab">Cluster Lookups</div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")
    st.markdown(
        "<div class='sidebar-footer'>UW MLOps · Boeing × WIC · 2025</div>",
        unsafe_allow_html=True,
    )

# ── Hero banner ───────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
  <h1>✈️ Taxi Fare <span>MLOps Platform</span></h1>
  <p>Real-time inference powered by Azure ML · University of Washington</p>
  <div class="badge-row">
    <span class="badge">🎓 UW MLOps</span>
    <span class="badge">✈️ Boeing</span>
    <span class="badge">💡 WIC</span>
    <span class="badge">☁️ Azure ML</span>
    <span class="badge">🤖 Live Endpoints</span>
  </div>
</div>
""", unsafe_allow_html=True)

# ── Helper ────────────────────────────────────────────────────────────────────
def call_endpoint(url: str, payload: dict, api_key: str) -> tuple[dict | None, str | None, float]:
    headers = {"Content-Type": "application/json"}
    if api_key.strip():
        headers["Authorization"] = f"Bearer {api_key.strip()}"
    t0 = time.time()
    try:
        r = requests.post(url, headers=headers, json=payload, timeout=30)
        elapsed = (time.time() - t0) * 1000
        r.raise_for_status()
        # The endpoint returns a JSON-encoded string, so double-parse if needed
        raw = r.json()
        if isinstance(raw, str):
            raw = json.loads(raw)
        return raw, None, elapsed
    except requests.exceptions.HTTPError as e:
        return None, f"HTTP {r.status_code}: {r.text}", (time.time() - t0) * 1000
    except Exception as e:
        return None, str(e), (time.time() - t0) * 1000

# ── Tabs ──────────────────────────────────────────────────────────────────────
tab1, tab2 = st.tabs(["💵  Fare Prediction  (Linear Regression)", "🗺️  Trip Clustering  (K-Means)"])

# ─────────────────────────────────────────────────────────────────────────────
# TAB 1 · LINEAR REGRESSION
# ─────────────────────────────────────────────────────────────────────────────
with tab1:
    st.markdown("""
    <div class="model-card">
      <div class="card-title">💵 Predicted Fare Amount</div>
      <div class="card-subtitle">Linear regression model · Azure ML real-time endpoint</div>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns([1, 1], gap="large")

    with col1:
        st.markdown("#### 🧮 Input Parameters")
        trip_distance = st.number_input(
            "Trip Distance (miles)", min_value=0.1, max_value=100.0,
            value=3.5, step=0.1, format="%.1f", key="lr_dist"
        )
        trip_duration = st.number_input(
            "Trip Duration (minutes)", min_value=1.0, max_value=300.0,
            value=15.0, step=0.5, format="%.1f", key="lr_dur"
        )
        pickup_hour = st.slider(
            "Pickup Hour (0–23)", min_value=0, max_value=23, value=14, key="lr_hour"
        )
        passenger_count = st.number_input(
            "Passenger Count", min_value=1, max_value=8, value=2, step=1, key="lr_pax"
        )

        st.markdown("")
        run_lr = st.button("🚀  Predict Fare", use_container_width=True, key="btn_lr")

    with col2:
        st.markdown("#### 📤 Prediction Result")

        if run_lr:
            if not api_key.strip():
                st.markdown('<div class="err-box">⚠️ Please enter your API key in the sidebar first.</div>', unsafe_allow_html=True)
            else:
                payload = {
                    "model": "linear_regression",
                    "trip_distance": trip_distance,
                    "trip_duration_min": trip_duration,
                    "pickup_hour": pickup_hour,
                    "passenger_count": int(passenger_count),
                }
                with st.spinner("Calling Azure ML endpoint…"):
                    result, error, latency = call_endpoint(lr_url, payload, api_key)

                if error:
                    st.markdown(f'<div class="err-box">❌ {error}</div>', unsafe_allow_html=True)
                else:
                    fare = result.get("predicted_fare_amount", "—")
                    st.markdown(f"""
                    <div class="result-box">
                      <div class="result-label">Predicted Fare Amount</div>
                      <div class="result-value">${fare:,.2f}</div>
                      <div class="result-sub">Model: {result.get('model','—')} · Latency: {latency:.0f} ms</div>
                    </div>
                    """, unsafe_allow_html=True)

                    st.session_state.lr_history.append({
                        "dist": trip_distance,
                        "dur": trip_duration,
                        "hour": pickup_hour,
                        "pax": passenger_count,
                        "fare": fare,
                        "ms": round(latency),
                    })

        elif st.session_state.lr_history:
            last = st.session_state.lr_history[-1]
            st.markdown(f"""
            <div class="result-box" style="border-left-color:#475569;">
              <div class="result-label" style="color:#475569;">Last Prediction</div>
              <div class="result-value" style="color:#94a3b8;">${last['fare']:,.2f}</div>
              <div class="result-sub">dist {last['dist']} mi · {last['dur']} min · {last['ms']} ms</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="empty-state">
              <div class="icon">💵</div>
              <p>Fill in the parameters and click <strong>Predict Fare</strong></p>
            </div>
            """, unsafe_allow_html=True)

        # history table
        if st.session_state.lr_history:
            st.markdown("---")
            st.markdown("**📋 Session History**")
            import pandas as pd
            df = pd.DataFrame(st.session_state.lr_history)
            df.columns = ["Distance (mi)", "Duration (min)", "Hour", "Passengers", "Fare ($)", "Latency (ms)"]
            st.dataframe(df.style.format({"Fare ($)": "${:.2f}", "Distance (mi)": "{:.1f}", "Duration (min)": "{:.1f}"}),
                         use_container_width=True, hide_index=True)

# ─────────────────────────────────────────────────────────────────────────────
# TAB 2 · K-MEANS CLUSTERING
# ─────────────────────────────────────────────────────────────────────────────
CLUSTER_LABELS = {
    0: ("🟢", "Budget Short-Haul", "cluster-0"),
    1: ("🟡", "Standard Mid-Range", "cluster-1"),
    2: ("🔴", "Premium Long-Haul", "cluster-2"),
    3: ("🟣", "Off-Peak Economy", "cluster-3"),
    4: ("🔵", "High-Demand Express", "cluster-4"),
}

with tab2:
    st.markdown("""
    <div class="model-card">
      <div class="card-title">🗺️ Trip Cluster Classification</div>
      <div class="card-subtitle">K-Means clustering model · Azure ML real-time endpoint</div>
    </div>
    """, unsafe_allow_html=True)

    col3, col4 = st.columns([1, 1], gap="large")

    with col3:
        st.markdown("#### 🧮 Input Parameters")
        do_location = st.number_input(
            "Drop-off Location ID (DOLocationID)", min_value=1, max_value=265,
            value=161, step=1, key="km_doloc"
        )
        fare_amount = st.number_input(
            "Fare Amount ($)", min_value=0.01, max_value=500.0,
            value=12.50, step=0.50, format="%.2f", key="km_fare"
        )
        km_distance = st.number_input(
            "Trip Distance (miles)", min_value=0.1, max_value=100.0,
            value=2.1, step=0.1, format="%.1f", key="km_dist"
        )
        km_passengers = st.number_input(
            "Passenger Count", min_value=1, max_value=8, value=1, step=1, key="km_pax"
        )
        km_hour = st.slider(
            "Pickup Hour (0–23)", min_value=0, max_value=23, value=9, key="km_hour"
        )

        st.markdown("")
        run_km = st.button("🚀  Classify Trip", use_container_width=True, key="btn_km")

    with col4:
        st.markdown("#### 📤 Cluster Result")

        if run_km:
            if not api_key.strip():
                st.markdown('<div class="err-box">⚠️ Please enter your API key in the sidebar first.</div>', unsafe_allow_html=True)
            else:
                payload = {
                    "DOLocationID": int(do_location),
                    "fare_amount": fare_amount,
                    "trip_distance": km_distance,
                    "passenger_count": int(km_passengers),
                    "pickup_hour": km_hour,
                }
                with st.spinner("Calling Azure ML endpoint…"):
                    result, error, latency = call_endpoint(km_url, payload, api_key)

                if error:
                    st.markdown(f'<div class="err-box">❌ {error}</div>', unsafe_allow_html=True)
                else:
                    cluster_id = result.get("predicted_cluster", 0)
                    emoji, label, css_class = CLUSTER_LABELS.get(cluster_id, ("⚪", f"Cluster {cluster_id}", "cluster-0"))
                    st.markdown(f"""
                    <div class="result-box">
                      <div class="result-label">Predicted Cluster</div>
                      <div class="result-value {css_class}">{emoji} Cluster {cluster_id}</div>
                      <div class="result-sub" style="font-size:0.95rem;color:#94a3b8;margin-top:0.4rem;">{label}</div>
                      <div class="result-sub">Drop-off: {result.get('DOLocationID','—')} · Model: {result.get('model','—')} · {latency:.0f} ms</div>
                    </div>
                    """, unsafe_allow_html=True)

                    st.session_state.km_history.append({
                        "do_loc": int(do_location),
                        "fare": fare_amount,
                        "dist": km_distance,
                        "pax": km_passengers,
                        "hour": km_hour,
                        "cluster": cluster_id,
                        "label": label,
                        "ms": round(latency),
                    })

        elif st.session_state.km_history:
            last = st.session_state.km_history[-1]
            c_id = last["cluster"]
            emoji, label, css_class = CLUSTER_LABELS.get(c_id, ("⚪", f"Cluster {c_id}", "cluster-0"))
            st.markdown(f"""
            <div class="result-box" style="border-left-color:#475569;">
              <div class="result-label" style="color:#475569;">Last Result</div>
              <div class="result-value {css_class}" style="font-size:1.8rem;">{emoji} Cluster {c_id}</div>
              <div class="result-sub">{label} · {last['ms']} ms</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="empty-state">
              <div class="icon">🗺️</div>
              <p>Fill in the parameters and click <strong>Classify Trip</strong></p>
            </div>
            """, unsafe_allow_html=True)

        # history table
        if st.session_state.km_history:
            st.markdown("---")
            st.markdown("**📋 Session History**")
            import pandas as pd
            df2 = pd.DataFrame(st.session_state.km_history)
            df2.columns = ["DOLocationID", "Fare ($)", "Distance (mi)", "Passengers", "Hour", "Cluster", "Label", "Latency (ms)"]
            st.dataframe(df2.style.format({"Fare ($)": "${:.2f}", "Distance (mi)": "{:.1f}"}),
                         use_container_width=True, hide_index=True)

# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown("""
<div style="text-align:center;color:#475569;font-size:0.78rem;padding:0.5rem 0 1.5rem 0;">
  Built with ❤️ · UW MLOps Program · Boeing × WIC · Azure Machine Learning
</div>
""", unsafe_allow_html=True)
