import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import math

# Structural Analysis Logic [cite: 75-81, 93-94]
def calculate_capacities(inputs):
    d = inputs['h'] - inputs['cover'] - (inputs['bar_diam'] / 2) [cite: 27-28, 77]
    As = (inputs['bar_area'] / inputs['spacing_x']) * 12 [cite: 30, 78]
    a = (As * inputs['fy']) / (0.85 * inputs['fc'] * 12) [cite: 32, 79]
    m_design = 0.9 * (As * inputs['fy'] * (d - a / 2)) [cite: 33-35, 80-81]
    
    # Location multipliers [cite: 36-43, 82-87]
    multipliers = {"interior": 8, "edge": 4, "corner": 2}
    P_flex = multipliers[inputs['location']] * m_design
    
    # Punching & One-Way Shear [cite: 50-62, 89-92]
    bo = 4 * (inputs['plate_dim'] + d)
    Vpunch = 0.75 * 4 * math.sqrt(inputs['fc']) * bo * d
    Vshear = 0.75 * 2 * math.sqrt(inputs['fc']) * (inputs['plate_dim'] + 2*d) * d
    
    return {"P_max": max(0, min(P_flex, Vpunch, Vshear)), "d": d}

st.set_page_config(page_title="Slab Analysis", layout="wide")
st.title("One-Way Slab Point Load Analysis")

# Sidebar Inputs [cite: 5-23]
lx_ft = st.sidebar.number_input("Short Span (Lx) [ft]", value=10.0)
ly_ft = st.sidebar.number_input("Long Span (Ly) [ft]", value=20.0)
h_in = st.sidebar.number_input("Slab Thickness (h) [in]", value=6.0)
bar_sz = st.sidebar.selectbox("Bar Size (#)", [3, 4, 5, 6, 7, 8], index=1)
spacing = st.sidebar.number_input("Spacing [in]", value=12.0)
fc_psi = st.sidebar.selectbox("Concrete f'c [psi]", [3000, 4000, 5000], index=1)
loc = st.sidebar.radio("Location", ["interior", "edge", "corner"])

params = {
    'Lx_ft': lx_ft, 'Ly_ft': ly_ft, 'h': h_in, 'cover': 0.75,
    'bar_area': (bar_sz/8)**2 * 0.785, 'bar_diam': bar_sz/8,
    'spacing_x': spacing, 'fc': fc_psi, 'fy': 60000,
    'dead_load': 25, 'live_load': 50, 'location': loc, 'plate_dim': 12.0
}

res = calculate_capacities(params)
st.metric("Allowable Point Load (Pmax)", f"{res['P_max']:.0f} lbs") [cite: 68-74]
