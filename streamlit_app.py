import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import math

# --- 1. CORE CALCULATION LOGIC ---
def calculate_capacities(inputs):
    # Effective Depth Calculation
    # d = h - cover - bar_diameter / 2 [cite: 27-28, 77]
    d = inputs['h'] - inputs['cover'] - (inputs['bar_diam'] / 2)
    
    # Steel Area Calculation: As = bar_area / spacing * 12 [cite: 29-30, 78]
    As = (inputs['bar_area'] / inputs['spacing_x']) * 12
    
    # Plastic Moment Capacity [cite: 31-35, 79-81]
    a = (As * inputs['fy']) / (0.85 * inputs['fc'] * 12)
    m = As * inputs['fy'] * (d - a/2)
    m_design = 0.9 * m
    
    # Yield-Line Collapse Method [cite: 36-43, 82-87]
    multipliers = {"interior": 8, "edge": 4, "corner": 2}
    P_flex = multipliers[inputs['location']] * m_design
    
    # Reduction for Existing Uniform Load [cite: 44-48, 88]
    wu = (1.2 * inputs['dead_load'] + 1.6 * inputs['live_load']) / 144 # lb/in2
    area_in2 = (inputs['Lx_ft'] * 12) * (inputs['Ly_ft'] * 12)
    P_flex -= (wu * area_in2 * 0.25)

    # Punching Shear Check [cite: 49-55, 89-90]
    bo = 4 * (inputs['plate_dim'] + d)
    Vpunch = 0.75 * 4 * math.sqrt(inputs['fc']) * bo * d

    # One-Way Shear Check [cite: 56-62, 91-92]
    width_eff = inputs['plate_dim'] + 2*d
    Vshear = 0.75 * 2 * math.sqrt(inputs['fc']) * width_eff * d

    # Governing Capacity [cite: 68-74, 93]
    p_max = max(0, min(P_flex, Vpunch, Vshear))
    
    return {
        "P_max": p_max,
        "P_flex": P_flex,
        "Vpunch": Vpunch,
        "Vshear": Vshear,
        "d": d
    }

# --- 2. STREAMLIT UI ---
st.set_page_config(page_title="Slab Point Load Tool", layout="wide")
st.title("One-Way Slab Point Load Analysis")

with st.sidebar:
    st.header("Slab Parameters")
    lx = st.number_input("Short Span (Lx) [ft]", value=10.0)
    ly = st.number_input("Long Span (Ly) [ft]", value=20.0)
    h = st.number_input("Slab Thickness (h) [in]", value=6.0)
    bar_sz = st.selectbox("Bar Size (#)", [3, 4, 5, 6, 7, 8], index=1)
    spacing = st.number_input("Spacing [in]", value=12.0)
    fc = st.selectbox("Concrete f'c [psi]", [3000, 4000, 5000], index=1)
    loc = st.radio("Location", ["interior", "edge", "corner"])

# Assembly for Engine
params = {
    'Lx_ft': lx, 'Ly_ft': ly, 'h': h, 'cover': 0.75,
    'bar_area': (bar_sz/8)**2 * 0.785, 'bar_diam': bar_sz/8,
    'spacing_x': spacing, 'fc': fc, 'fy': 60000,
    'dead_load': 20, 'live_load': 50, 'location': loc, 'plate_dim': 12.0
}

# Run Analysis
res = calculate_capacities(params)

# Display Results
st.subheader("Governing Capacity Results")
c1, c2, c3 = st.columns(3)
c1.metric("Max Point Load (Pmax)", f"{res['P_max']:.0f} lbs")
c2.metric("Governing Mode", "Punching" if res['P_max'] == res['Vpunch'] else "Flexure")
c3.metric("Effective Depth (d)", f"{res['d']:.2f} in")
