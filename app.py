import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import io
import math
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

# --- STRUCTURAL ENGINE ---
def calculate_capacities(inputs):
    # 1. Effective Depth [cite: 27-28, 77]
    d = inputs['h'] - inputs['cover'] - (inputs['bar_diam'] / 2)
    
    # 2. Flexural Strength [cite: 29-35, 78-81]
    As = (inputs['bar_area'] / inputs['spacing_x']) * 12 
    a = (As * inputs['fy']) / (0.85 * inputs['fc'] * 12)
    m_design = 0.9 * (As * inputs['fy'] * (d - a / 2))
    
    # 3. Yield-Line Capacity [cite: 36-43, 82-87]
    if inputs['location'] == "interior":
        P_flex = 8 * m_design
    elif inputs['location'] == "edge":
        P_flex = 4 * m_design
    else:
        P_flex = 2 * m_design

    # 4. Uniform Load Reduction [cite: 44-48, 88]
    # Factored uniform load: 1.2D + 1.6L
    wu = (1.2 * inputs['dead_load'] + 1.6 * inputs['live_load']) / 144 # lb/in2
    # Area in sq inches
    area_sqin = (inputs['Lx_ft'] * 12) * (inputs['Ly_ft'] * 12)
    P_flex -= (wu * area_sqin * 0.25)

    # 5. Punching Shear [cite: 50-55, 90]
    bo = 4 * (inputs['plate_dim'] + d)
    Vpunch = 0.75 * 4 * math.sqrt(inputs['fc']) * bo * d

    # 6. One-Way Shear [cite: 56-62, 91-92]
    width_eff = inputs['plate_dim'] + (2 * d)
    Vshear = 0.75 * 2 * math.sqrt(inputs['fc']) * width_eff * d

    p_max = max(0, min(P_flex, Vpunch, Vshear))
    return {"P_flex": P_flex, "Vpunch": Vpunch, "Vshear": Vshear, "P_max": p_max, "d": d}

# --- UI SETUP ---
st.set_page_config(page_title="Slab Analysis Tool", layout="wide")
st.title("One-Way Slab Point Load Analysis")
st.sidebar.header("Input Parameters")

# Inputs [cite: 5-23]
lx_ft = st.sidebar.number_input("Short Span (Lx) [ft]", value=10.0)
ly_ft = st.sidebar.number_input("Long Span (Ly) [ft]", value=20.0)
h_in = st.sidebar.number_input("Slab Thickness (h) [in]", value=6.0)
cov_in = st.sidebar.number_input("Cover [in]", value=0.75)
bar_sz = st.sidebar.selectbox("Bar Size (#)", [3, 4, 5, 6, 7, 8], index=1)
spacing = st.sidebar.number_input("Bar Spacing [in]", value=12.0)
fc_psi = st.sidebar.selectbox("Concrete f'c [psi]", [3000, 4000, 5000], index=1)
fy_psi = st.sidebar.number_input("Steel fy [psi]", value=60000)
dl_psf = st.sidebar.number_input("Dead Load [psf]", value=25.0)
ll_psf = st.sidebar.number_input("Live Load [psf]", value=50.0)
loc = st.sidebar.radio("Location", ["interior", "edge", "corner"])

# Data Assembly
params = {
    'Lx_ft': lx_ft, 'Ly_ft': ly_ft, 'h': h_in, 'cover': cov_in,
    'bar_area': (bar_sz/8)**2 * 0.785, 'bar_diam': bar_sz/8,
    'spacing_x': spacing, 'fc': fc_psi, 'fy': fy_psi,
    'dead_load': dl_psf, 'live_load': ll_psf, 'location': loc, 'plate_dim': 12.0
}

res = calculate_capacities(params)

# Results Display [cite: 68-74, 93]
st.subheader("Governing Capacity Results")
c1, c2, c3 = st.columns(3)
c1.metric("Max Point Load (Pmax)", f"{res['P_max']:.0f} lbs")
c2.metric("Governing Mode", "Punching" if res['P_max'] == res['Vpunch'] else "Flexure")
c3.metric("Effective Depth (d)", f"{res['d']:.2f} in")

# Visualization [cite: 97-99]
st.subheader("Punching Shear Critical Perimeter")

fig, ax = plt.subplots(figsize=(4, 4))
ax.add_patch(plt.Rectangle((0.3, 0.3), 0.4, 0.4, color='gray', alpha=0.3, label="Load Plate (12x12)"))
ax.add_patch(plt.Rectangle((0.2, 0.2), 0.6, 0.6, fill=False, edgecolor='red', linestyle='--', label="d/2 Perimeter"))
ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.axis('off'); ax.legend()
st.pyplot(fig)
