import streamlit as st
import pandas as pd
import sqlite3
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors

# Database Connection
conn = sqlite3.connect('csqs_advanced.db', check_same_thread=False)
c = conn.cursor()

# Create Tables
c.execute('''CREATE TABLE IF NOT EXISTS spectro 
              (heat_no TEXT, grade TEXT, carbon REAL, silicon REAL, manganese REAL, sulfur REAL, phosphorus REAL, chromium REAL, nickel REAL, molybdenum REAL, status TEXT)''')

c.execute('''CREATE TABLE IF NOT EXISTS sand_lab 
              (date TEXT, shift TEXT, moisture REAL, permeability REAL, compactability REAL, gcs REAL, advice TEXT)''')

c.execute('''CREATE TABLE IF NOT EXISTS metal_testing 
              (heat_no TEXT, hardness_bhn REAL, tensile_strength REAL, nodularity REAL, matrix TEXT)''')

c.execute('''CREATE TABLE IF NOT EXISTS raw_material 
              (date TEXT, material_name TEXT, supplier TEXT, status TEXT, remarks TEXT)''')

c.execute('''CREATE TABLE IF NOT EXISTS pouring_log 
              (heat_no TEXT, temp_c REAL, inoculant_added REAL, status TEXT)''')

conn.commit()

# Streamlit Page Setup
st.set_page_config(page_title="Chemical & Sand Quality System (CSQS)", layout="wide")
st.title("Chemical & Sand Quality System (CSQS)")

menu = [
    "1. Chemical Spectro Analysis", 
    "2. Sand Lab Testing & Correction Advice", 
    "3. Metal & Microstructure Testing", 
    "4. Raw Material Inspection", 
    "5. Pouring & Ladle Control", 
    "6. Test Certificate (TC) Generator",
    "7. Quality Analytics Dashboard"
]
choice = st.sidebar.selectbox("Navigation Menu", menu)

# Section 1
if choice == "1. Chemical Spectro Analysis":
    st.subheader("Spectrometer Chemical Analysis Log")
    col1, col2, col3 = st.columns(3)
    with col1:
        heat_no = st.text_input("Heat / Ladle Number", "H-2026-001")
        grade = st.selectbox("Select Material Grade", ["SG Iron 400/12", "Grey Iron FG260"])
        c_val = st.number_input("Carbon (C %)", value=3.60, step=0.01)
        si_val = st.number_input("Silicon (Si %)", value=2.40, step=0.01)
    
    with col2:
        mn_val = st.number_input("Manganese (Mn %)", value=0.35, step=0.01)
        s_val = st.number_input("Sulfur (S %)", value=0.012, step=0.001, format="%.3f")
        p_val = st.number_input("Phosphorus (P %)", value=0.025, step=0.001, format="%.3f")
        cr_val = st.number_input("Chromium (Cr %)", value=0.03, step=0.01)
        
    with col3:
        ni_val = st.number_input("Nickel (Ni %)", value=0.01, step=0.01)
        mo_val = st.number_input("Molybdenum (Mo %)", value=0.01, step=0.01)

    status = "PASS"
    if grade == "SG Iron 400/12":
        if c_val < 3.50 or c_val > 3.85 or si_val < 2.20 or si_val > 2.80 or s_val > 0.020:
            status = "OUT OF SPEC"

    st.info(f"Specification Validation Result: **{status}**")

    if st.button("Save Chemical Test Record"):
        c.execute("INSERT INTO spectro VALUES (?,?,?,?,?,?,?,?,?,?,?)", 
                  (heat_no, grade, c_val, si_val, mn_val, s_val, p_val, cr_val, ni_val, mo_val, status))
        conn.commit()
        st.success(f"Heat {heat_no} chemical properties successfully saved!")

# Section 2
elif choice == "2. Sand Lab Testing & Correction Advice":
    st.subheader("Sand Lab Testing & Smart Correction Advice")
    col1, col2 = st.columns(2)
    with col1:
        test_date = st.date_input("Date")
        shift = st.selectbox("Shift", ["Shift A", "Shift B", "Shift C"])
        moisture = st.number_input("Moisture (%)", value=3.6, step=0.1)
        compactability = st.number_input("Compactability (%)", value=42.0, step=0.5)
    
    with col2:
        permeability = st.number_input("Permeability Number", value=145, step=1)
        gcs = st.number_input("Green Compression Strength (GCS - gm/cm2)", value=1650, step=10)

    advice = "Sand Properties are in Normal Limits."
    if moisture > 4.0:
        advice = "High Moisture! Blowhole risks. Reduce water addition in intensive mixer."
    elif moisture < 3.0:
        advice = "Low Moisture! Sand dropping risk. Add required percentage of water."
    
    if gcs < 1400:
        advice += " | Low GCS Strength! Add 0.2% Bentonite."

    st.warning(f"**Correction Advisory:** {advice}")

    if st.button("Save Sand Testing Record"):
        c.execute("INSERT INTO sand_lab VALUES (?,?,?,?,?,?,?)", 
                  (str(test_date), shift, moisture, permeability, compactability, gcs, advice))
        conn.commit()
        st.success("Sand lab record saved successfully!")

# Section 3
elif choice == "3. Metal & Microstructure Testing":
    st.subheader("Hardness, Tensile & Microstructure Testing")
    col1, col2 = st.columns(2)
    with col1:
        heat_no = st.text_input("Heat Number", "H-2026-001")
        hardness = st.number_input("Hardness (BHN)", value=180, step=1)
        tensile = st.number_input("Tensile Strength (MPa)", value=420, step=5)
        
    with col2:
        nodularity = st.number_input("Nodularity (%)", value=85.0, step=1.0)
        matrix = st.selectbox("Matrix Structure", ["Ferritic-Pearlitic", "Fully Ferritic", "Pearlitic"])

    if st.button("Save Mechanical & Micro Record"):
        c.execute("INSERT INTO metal_testing VALUES (?,?,?,?,?)", 
                  (heat_no, hardness, tensile, nodularity, matrix))
        conn.commit()
        st.success("Mechanical test properties recorded!")

# Section 4
elif choice == "4. Raw Material Inspection":
    st.subheader("Raw Material Inward Quality Inspection")
    col1, col2 = st.columns(2)
    with col1:
        rm_date = st.date_input("Inspection Date")
        material = st.selectbox("Material Name", ["Pig Iron", "Steel Scrap", "FeSi (Ferro Silicon)", "FeMn (Ferro Manganese)", "Inoculant"])
        supplier = st.text_input("Supplier / Vendor Name", "Tata Steel / Local Dealer")
    
    with col2:
        rm_status = st.selectbox("Quality Status", ["ACCEPTED", "REJECTED", "ACCEPTED WITH DEVIATION"])
        remarks = st.text_area("Inspection Remarks / Chemical Certificate Match")

    if st.button("Save Raw Material Inspection"):
        c.execute("INSERT INTO raw_material VALUES (?,?,?,?,?)", 
                  (str(rm_date), material, supplier, rm_status, remarks))
        conn.commit()
        st.success("Raw material inspection saved!")

# Section 5
elif choice == "5. Pouring & Ladle Control":
    st.subheader("Pouring Temperature & Alloy Inoculation Control")
    col1, col2 = st.columns(2)
    with col1:
        heat_no = st.text_input("Heat Number", "H-2026-001")
        temp = st.number_input("Pouring Temp (C)", value=1420, step=5)
    
    with col2:
        inoculant = st.number_input("Inoculant Added (kg)", value=2.5, step=0.1)
        p_status = "READY FOR POURING" if temp >= 1380 and temp <= 1450 else "TEMP OUT OF RANGE"

    st.write(f"**Pouring Status:** {p_status}")

    if st.button("Save Pouring Log"):
        c.execute("INSERT INTO pouring_log VALUES (?,?,?,?)", (heat_no, temp, inoculant, p_status))
        conn.commit()
        st.success("Pouring log entry saved!")

# Section 6
elif choice == "6. Test Certificate (TC) Generator":
    st.subheader("Customer Test Certificate (PDF) Auto Generator")
    col1, col2 = st.columns(2)
    with col1:
        cust_name = st.text_input("Customer Name", "Kirloskar Oil Engines")
        part_name = st.text_input("Part Description", "Crankcase Casting")
    with col2:
        tc_heat = st.text_input("Enter Heat No for TC", "H-2026-001")
        tc_qty = st.number_input("Quantity (Pcs)", value=100)

    def generate_pdf():
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        styles = getSampleStyleSheet()
        elements = []

        elements.append(Paragraph("<b>QUALITY TEST CERTIFICATE</b>", styles['Title']))
        elements.append(Spacer(1, 15))
        elements.append(Paragraph(f"<b>Customer Name:</b> {cust_name} | <b>Part Name:</b> {part_name}", styles['Normal']))
        elements.append(Paragraph(f"<b>Heat Number:</b> {tc_heat} | <b>Quantity:</b> {tc_qty} Pcs", styles['Normal']))
        elements.append(Spacer(1, 15))

        data = [
            ["Element / Parameter", "Specified Standard", "Observed Test Result", "Status"],
            ["Carbon (C %)", "3.50 - 3.85", "3.62", "PASS"],
            ["Silicon (Si %)", "2.20 - 2.80", "2.41", "PASS"],
            ["Manganese (Mn %)", "0.20 - 0.50", "0.36", "PASS"],
            ["Hardness (BHN)", "160 - 210 BHN", "180 BHN", "PASS"],
            ["Nodularity (%)", "> 80%", "85%", "PASS"]
        ]

        t = Table(data)
        t.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.navy),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('GRID', (0,0), (-1,-1), 1, colors.grey),
            ('ALIGN', (0,0), (-1,-1), 'CENTER')
        ]))
        
        elements.append(t)
        elements.append(Spacer(1, 20))
        elements.append(Paragraph("<b>Authorized Quality Stamp & Signature: _______________________</b>", styles['Normal']))
        doc.build(elements)
        buffer.seek(0)
        return buffer

    if st.button("Generate Preview & Ready Certificate"):
        pdf_bytes = generate_pdf()
        st.download_button(
            label="Download Test Certificate PDF",
            data=pdf_bytes,
            file_name=f"TC_{tc_heat}.pdf",
            mime="application/pdf"
        )

# Section 7
elif choice == "7. Quality Analytics Dashboard":
    st.subheader("Quality Inspection Summary & Records")
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### Spectro Chemical Logs")
        df_spectro = pd.read_sql_query("SELECT * FROM spectro", conn)
        st.dataframe(df_spectro, use_container_width=True)

    with col2:
        st.markdown("### Sand Lab Logs")
        df_sand = pd.read_sql_query("SELECT * FROM sand_lab", conn)
        st.dataframe(df_sand, use_container_width=True)

    st.divider()

    col3, col4 = st.columns(2)
    with col3:
        st.markdown("### Metal & Microstructure Logs")
        df_metal = pd.read_sql_query("SELECT * FROM metal_testing", conn)
        st.dataframe(df_metal, use_container_width=True)

    with col4:
        st.markdown("### Pouring & Ladle Logs")
        df_pouring = pd.read_sql_query("SELECT * FROM pouring_log", conn)
        st.dataframe(df_pouring, use_container_width=True)

    st.markdown("### Raw Material Inspection Logs")
    df_rm = pd.read_sql_query("SELECT * FROM raw_material", conn)
    st.dataframe(df_rm, use_container_width=True)