import streamlit as st
import pandas as pd
import plotly.express as px

# Konfigurasi halaman agar responsif di Google Sites
st.set_page_config(
    page_title="Executive Dashboard Anti-Churn",
    page_icon="📊",
    layout="wide"
)

# Judul Utama Korporat
st.title("📊 Executive Dashboard Anti-Churn & Retention")
st.markdown("Monitoring performa *follow-up* harian agen secara *real-time*.")
st.divider()

# --- BAGIAN 1: MEMUAT DATA DARI GOOGLE SHEETS ---
@st.cache_data(ttl=600) # Cache data selama 10 menit
def load_data():
    # GANTI LINK DI BAWAH INI dengan link CSV Google Sheets 'tren_followup' Anda
    sheet_url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSGw6E8X8kn7zRv7u6mRY-uY_zmc7NSbl2BCJzhJBODjPpIY-O_cuoWPTET_0gqrqXmR5DdO48rMH20/pub?gid=1792408447&single=true&output=csv"
    df = pd.read_csv(sheet_url)
    return df

try:
    df = load_data()
    
    # Standarisasi nama kolom ke huruf kecil
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

    st.divider()

    # --- BAGIAN 4: GRAFIK ANALISIS (PLOTLY) ---
    col_left, col_right = st.columns(2)
    
    with col_left:
        st.subheader("📈 Tren Total Follow-up Harian")
        if 'tanggalbuat' in df.columns and 'total_harian' in df.columns:
            tren_tgl = df.groupby('tanggalbuat')['total_harian'].sum().reset_index()
            fig_line = px.line(tren_tgl, x='tanggalbuat', y='total_harian', markers=True, template='plotly_white')
            st.plotly_chart(fig_line, use_container_width=True)
        else:
            st.info("Kolom tanggal atau total tidak ditemukan.")

    with col_right:
        st.subheader("🏆 Top 10 Agen Berdasarkan Follow-up")
        if 'agen' in df.columns and 'total_harian' in df.columns:
            top_agen = df.groupby('agen')['total_harian'].sum().reset_index().sort_values(by='total_harian', ascending=False).head(10)
            fig_bar = px.bar(top_agen, x='total_harian', y='agen', orientation='h', template='plotly_white')
            fig_bar.update_layout(yaxis={'categoryorder':'total ascending'})
            st.plotly_chart(fig_bar, use_container_width=True)
        else:
            st.info("Kolom agen tidak ditemukan.")

except Exception as e:
    st.warning("⚠️ Belum dapat memuat data. Pastikan link Google Sheets CSV sudah dipasang dengan benar di dalam kode.")
    st.text(f"Detail Error: {e}")
