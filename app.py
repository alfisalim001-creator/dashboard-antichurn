import streamlit as st
import pandas as pd
import plotly.express as px

# Konfigurasi halaman
st.set_page_config(
    page_title="Executive Dashboard Anti-Churn",
    page_icon="⚡",
    layout="wide"
)

# --- CUSTOM CSS UNTUK ANIMASI HALUS & KARTU MODERN ---
st.markdown("""
    <style>
    /* Styling latar belakang utama */
    .main {
        background-color: #f8fafc;
    }
    
    /* Efek Card / Metric Box dengan Animasi Hover Smooth */
    div.stMetric {
        background: linear-gradient(135deg, #ffffff 0%, #f1f5f9 100%);
        padding: 20px;
        border-radius: 14px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -1px rgba(0, 0, 0, 0.03);
        border: 1px solid #e2e8f0;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }
    div.stMetric:hover {
        transform: translateY(-6px);
        box-shadow: 0 12px 20px -3px rgba(37, 99, 235, 0.15), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
        border-color: #3b82f6;
    }
    
    /* Perbaikan font & header */
    h1, h2, h3 {
        font-family: 'Inter', sans-serif;
        color: #1e293b;
        font-weight: 700;
    }
    </style>
""", unsafe_allow_html=True)

# Judul Utama Korporat
st.title("⚡ Executive Dashboard Anti-Churn & Retention")
st.markdown("Monitoring performa *follow-up* harian agen secara *real-time* dengan analitik modern.")
st.divider()

# --- BAGIAN 1: MEMUAT DATA DARI GOOGLE SHEETS ---
@st.cache_data(ttl=600)
def load_data():
    # Ganti dengan link CSV Google Sheets 'tren_followup' Anda
    sheet_url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSGw6E8X8kn7zRv7u6mRY-uY_zmc7NSbl2BCJzhJBODjPpIY-O_cuoWPTET_0gqrqXmR5DdO48rMH20/pub?gid=1792408447&single=true&output=csv"
    df = pd.read_csv(sheet_url)
    return df

try:
    df = load_data()
    df.columns = df.columns.str.strip().str.lower()

    # --- BAGIAN 2: SIDEBAR FILTER ---
    st.sidebar.header("🔍 Filter Korporat")
    
    if 'sbu' in df.columns:
        sbu_list = ['Semua SBU'] + list(df['sbu'].dropna().unique())
        pilih_sbu = st.sidebar.selectbox("Pilih SBU", sbu_list)
        if pilih_sbu != 'Semua SBU':
            df = df[df['sbu'] == pilih_sbu]

    # --- BAGIAN 3: KPI CARDS (RINGKASAN UTAMA) ---
    col1, col2, col3, col4 = st.columns(4)
    
    total_fu = df['total_harian'].sum() if 'total_harian' in df.columns else len(df)
    total_tele = df['telecollection'].sum() if 'telecollection' in df.columns else 0
    total_ret = df['retention'].sum() if 'retention' in df.columns else 0
    total_win = df['winback'].sum() if 'winback' in df.columns else 0
    
    col1.metric("Total Follow-up", f"{total_fu:,}")
    col2.metric("Telecollection", f"{total_tele:,}")
    col3.metric("Retention", f"{total_ret:,}")
    col4.metric("Winback", f"{total_win:,}")

    st.markdown("<br>", unsafe_allow_html=True)

    # --- BAGIAN 4: GRAFIK ANALISIS (PLOTLY BERGAYA MODERN) ---
    col_left, col_right = st.columns(2)
    
    with col_left:
        st.subheader("📈 Tren Total Follow-up Harian")
        if 'tanggalbuat' in df.columns and 'total_harian' in df.columns:
            tren_tgl = df.groupby('tanggalbuat')['total_harian'].sum().reset_index()
            fig_line = px.line(
                tren_tgl, x='tanggalbuat', y='total_harian', 
                markers=True, template='plotly_white',
                color_discrete_sequence=['#2563eb']
            )
            # Styling grafik agar bersih dan transparan
            fig_line.update_traces(line=dict(width=3), marker=dict(size=8))
            fig_line.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                margin=dict(l=20, r=20, t=30, b=20)
            )
            st.plotly_chart(fig_line, use_container_width=True)
        else:
            st.info("Kolom tanggal atau total tidak ditemukan.")

    with col_right:
        st.subheader("🏆 Top 10 Agen Berdasarkan Follow-up")
        if 'agen' in df.columns and 'total_harian' in df.columns:
            top_agen = df.groupby('agen')['total_harian'].sum().reset_index().sort_values(by='total_harian', ascending=False).head(10)
            fig_bar = px.bar(
                top_agen, x='total_harian', y='agen', orientation='h', 
                template='plotly_white',
                color='total_harian',
                color_continuous_scale='Blues'
            )
            fig_bar.update_layout(
                yaxis={'categoryorder':'total ascending'},
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                margin=dict(l=20, r=20, t=30, b=20),
                coloraxis_showscale=False
            )
            st.plotly_chart(fig_bar, use_container_width=True)
        else:
            st.info("Kolom agen tidak ditemukan.")

except Exception as e:
    st.warning("⚠️ Belum dapat memuat data. Pastikan link Google Sheets CSV sudah dipasang dengan benar.")
    st.text(f"Detail Error: {e}")
