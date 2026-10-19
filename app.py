
import io
import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(page_title='StatVista | UTS Statistika 1B', page_icon='🌈', layout='wide', initial_sidebar_state='collapsed')
st.markdown('''<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');
html,body,[class*="css"],.stApp{font-family:'Plus Jakarta Sans',sans-serif}
.stApp{background:linear-gradient(140deg,#f9f5ff 0%,#eff8ff 50%,#fff5fa 100%);color:#25304a}
.block-container{max-width:1200px;padding-top:1.4rem;padding-bottom:3rem}
h1,h2,h3{color:#273052!important;letter-spacing:-.035em}
h2,h3{margin-top:1.4rem!important}
[data-testid="stSidebar"]{background:linear-gradient(180deg,#f3edff,#eaf5ff)}
[data-testid="stMetric"]{background:#fff;border:1px solid #eee7fb;border-radius:20px;padding:18px;box-shadow:0 8px 28px #5d4a9512}
[data-testid="stMetricLabel"]{color:#706b87}
[data-testid="stMetricValue"]{color:#6246d9;font-weight:800}
[data-testid="stVerticalBlockBorderWrapper"]{border-radius:20px}
.stButton>button,.stDownloadButton>button{border-radius:13px!important;border:1px solid #c8baf9!important;background:white!important;color:#5233bc!important;font-weight:700!important}
.stButton>button:hover,.stDownloadButton>button:hover{background:#f0eaff!important}
[data-testid="stFileUploader"]{background:white;border-radius:16px;padding:8px}
.hero{background:linear-gradient(115deg,#6345dc,#9b5ce8 53%,#f47ca9);border-radius:26px;padding:30px 32px;color:white;box-shadow:0 15px 35px #7950c52a;margin-bottom:20px}
.hero h1{color:white!important;font-size:clamp(2rem,5vw,3.2rem);margin:0}
.hero p{color:#f9edff;margin:10px 0 0;font-size:1.03rem}
.pill{display:inline-block;background:#ffffff33;border:1px solid #ffffff55;border-radius:100px;padding:5px 12px;font-size:.8rem;margin-bottom:12px}
.section-note{color:#77748e;font-size:.92rem}
@media(max-width:640px){.block-container{padding:1rem .9rem}.hero{padding:24px 19px;border-radius:20px}}
</style>''',unsafe_allow_html=True)

st.markdown('''<div class="hero"><span class="pill">✨ UTS STATISTIKA • MATEMATIKA 1B</span><h1>🌈 StatVista</h1><p>Dashboard statistik deskriptif yang colorful, interaktif, dan mudah digunakan.</p></div>''',unsafe_allow_html=True)
st.write('Unggah data Excel/CSV, pilih variabel, eksplorasi grafik, lalu unduh hasil analisis.')

@st.cache_data
def load_data(file_bytes,name):
    b=io.BytesIO(file_bytes)
    if name.lower().endswith('.csv'):
        try:return pd.read_csv(b)
        except UnicodeDecodeError:
            b.seek(0)
            return pd.read_csv(b,encoding='latin1')
    return pd.read_excel(b)

with st.sidebar:
    st.header('⚙️ Pengaturan Analisis')
    upload=st.file_uploader('📁 Unggah dataset',type=['xlsx','xls','csv'])
    st.caption('Mendukung Excel dan CSV • Maksimum mengikuti pengaturan Streamlit')
    st.divider()
    st.subheader('💡 Cara menggunakan')
    st.write('1. Unggah Excel/CSV atau pakai data contoh.\n\n2. Pilih variabel dan ukuran statistik.\n\n3. Jelajahi visualisasi dan tabel frekuensi.\n\n4. Unduh laporan.')
    st.info('Varians dan standar deviasi dihitung sebagai statistik sampel (ddof=1). Kuartil menggunakan interpolasi linear.')

if upload is not None:
    try:df=load_data(upload.getvalue(),upload.name)
    except Exception as e:
        st.error(f'File gagal dibaca: {e}')
        st.stop()
    label=upload.name
else:
    df=pd.DataFrame({'Usia':[18,19,20,19,21,18,20,22,19,21,20,18], 'Tinggi Badan (cm)':[160,168,172,165,174,158,170,176,166,173,169,162], 'Berat Badan (kg)':[51,60,68,56,72,49,65,77,58,70,63,53], 'Nilai Ujian':[78,85,90,82,94,74,88,96,80,92,86,76], 'Kelas':['1B']*12})
    label='Data contoh (otomatis)'
    st.info('💡 Belum ada file diunggah. Kamu bisa mencoba semua fitur dengan data contoh otomatis. Untuk memakai dataset_contoh.xlsx, buka menu ☰ lalu unggah file tersebut.')

st.header('📁 Dataset Overview')
a,b,c=st.columns(3)
a.metric('🧾 Jumlah baris',f'{len(df):,}')
b.metric('📚 Jumlah kolom',len(df.columns))
c.metric('✨ Nilai kosong',int(df.isna().sum().sum()))
st.caption(f'📌 Sumber: {label}')
with st.expander('👀 Lihat tabel dataset',expanded=True):
    st.dataframe(df,use_container_width=True,hide_index=True)

numeric=df.select_dtypes(include='number').columns.tolist()
if not numeric:
    st.warning('Dataset tidak memiliki kolom numerik. Gunakan file yang berisi angka.')
    st.stop()

st.header('🎛️ Konfigurasi Analisis')
variables=st.multiselect('Pilih variabel numerik',numeric,default=numeric[:min(3,len(numeric))])
options=['N','Minimum','Maksimum','Mean','Median','Modus','Varians','Standar Deviasi','Q1','Q2','Q3']
metrics=st.multiselect('Pilih ukuran statistik',options,default=options)
if not variables or not metrics:
    st.warning('Pilih minimal satu variabel dan satu ukuran statistik.')
    st.stop()

def mode_str(s):
    m=s.mode(dropna=True)
    if m.empty:return '—'
    return ', '.join(f'{v:g}' if isinstance(v,(int,float,np.integer,np.floating)) else str(v) for v in m.iloc[:5])+(' …' if len(m)>5 else '')

rows=[]
for col in variables:
    s=pd.to_numeric(df[col],errors='coerce').dropna()
    rows.append({'Variabel':col,'N':len(s),'Minimum':s.min() if len(s) else np.nan,'Maksimum':s.max() if len(s) else np.nan,'Mean':s.mean() if len(s) else np.nan,'Median':s.median() if len(s) else np.nan,'Modus':mode_str(s),'Varians':s.var(ddof=1) if len(s)>1 else np.nan,'Standar Deviasi':s.std(ddof=1) if len(s)>1 else np.nan,'Q1':s.quantile(.25) if len(s) else np.nan,'Q2':s.quantile(.5) if len(s) else np.nan,'Q3':s.quantile(.75) if len(s) else np.nan})
result=pd.DataFrame(rows)[['Variabel']+metrics]
st.header('💎 Ringkasan Statistika Deskriptif')
st.dataframe(result.style.format({k:'{:,.2f}' for k in metrics if k not in ['N','Modus']},na_rep='—'),use_container_width=True,hide_index=True)
st.caption('N adalah jumlah data valid. Modus dapat lebih dari satu. Varians/standar deviasi memerlukan minimal 2 data.')

st.header('🎨 Visualisasi Interaktif')
col1,col2=st.columns(2)
with col1:chosen=st.selectbox('Variabel grafik',variables)
with col2:chart=st.selectbox('Jenis grafik',['Histogram','Boxplot','Diagram batang frekuensi','Diagram lingkaran frekuensi'])
palette=st.selectbox('🌈 Tema warna',['Ungu & Pink','Biru Laut','Tropical','Pelangi'])
colors={'Ungu & Pink':['#7856e8','#e77bb4','#a7a0f5'],'Biru Laut':['#3699ee','#73c8ef','#a2e7f1'],'Tropical':['#10bfa3','#ffb85c','#ff7193'],'Pelangi':['#7b61ff','#fa7db2','#46bce7','#ffbf69','#59cfa9']}[palette]
series=pd.to_numeric(df[chosen],errors='coerce').dropna()
if series.empty:
    st.warning('Tidak ada nilai valid untuk grafik.')
else:
    if chart=='Histogram':
        bins=st.slider('Jumlah kelompok (bins)',3,30,10)
        fig=px.histogram(x=series,nbins=bins,labels={'x':chosen,'y':'Frekuensi'},title=f'Distribusi {chosen}',color_discrete_sequence=colors)
        fig.update_layout(yaxis_title='Frekuensi')
    elif chart=='Boxplot':
        fig=px.box(y=series,labels={'y':chosen},title=f'Boxplot {chosen}',color_discrete_sequence=colors,points='outliers')
    else:
        freq=series.value_counts().sort_index().reset_index()
        freq.columns=['Nilai','Frekuensi']
        if len(freq)>30:
            st.info('Grafik menampilkan 30 nilai dengan frekuensi tertinggi.')
            freq=freq.nlargest(30,'Frekuensi')
        freq['Nilai']=freq['Nilai'].astype(str)
        if chart=='Diagram batang frekuensi':
            fig=px.bar(freq,x='Nilai',y='Frekuensi',color='Nilai',title=f'Frekuensi {chosen}',color_discrete_sequence=colors)
            fig.update_layout(showlegend=False)
        else:fig=px.pie(freq,names='Nilai',values='Frekuensi',title=f'Proporsi {chosen}',color_discrete_sequence=colors)
    fig.update_layout(template='plotly_white',paper_bgcolor='rgba(0,0,0,0)',plot_bgcolor='rgba(0,0,0,0)',margin=dict(l=10,r=10,t=55,b=10),font=dict(family='Arial',color='#34405e'),title_font=dict(size=20))
    st.plotly_chart(fig,use_container_width=True)

st.header('📊 Tabel Distribusi Frekuensi')
valid=series
frequency=pd.DataFrame()
if len(valid):
    grouping=st.radio('Pengelompokan',['Nilai unik','Interval kelas'],horizontal=True)
    if grouping=='Nilai unik':
        frequency=valid.value_counts().sort_index().rename_axis('Nilai').reset_index(name='Frekuensi')
    else:
        classes=st.slider('Jumlah kelas',2,20,6)
        if valid.nunique()==1:frequency=pd.DataFrame({'Interval':[str(valid.iloc[0])],'Frekuensi':[len(valid)]})
        else:
            counts,edges=np.histogram(valid,bins=classes)
            frequency=pd.DataFrame({'Interval':[f'{edges[i]:.2f} – {edges[i+1]:.2f}' for i in range(len(counts))],'Frekuensi':counts})
    frequency['Persentase (%)']=(frequency['Frekuensi']/len(valid)*100).round(2)
    frequency['Frekuensi Kumulatif']=frequency['Frekuensi'].cumsum()
    st.dataframe(frequency,use_container_width=True,hide_index=True)

st.header('💡 Interpretasi Otomatis')
for col in variables:
    s=pd.to_numeric(df[col],errors='coerce').dropna()
    if len(s):
        st.info(f'**{col}:** Dari **{len(s)}** data valid, nilai berkisar antara **{s.min():.2f}** dan **{s.max():.2f}**. Rata-rata **{s.mean():.2f}**, median **{s.median():.2f}**. Ada **{len(df)-len(s)}** data kosong/tidak numerik.')

st.header('📥 Unduh Hasil')
left,right=st.columns(2)
left.download_button('📄 Unduh ringkasan CSV',result.to_csv(index=False).encode('utf-8-sig'),file_name='ringkasan_statistika.csv',mime='text/csv',use_container_width=True)
buf=io.BytesIO()
with pd.ExcelWriter(buf,engine='openpyxl') as writer:
    result.to_excel(writer,index=False,sheet_name='Ringkasan')
    df.to_excel(writer,index=False,sheet_name='Dataset')
    if not frequency.empty:frequency.to_excel(writer,index=False,sheet_name='Frekuensi')
right.download_button('📗 Unduh laporan Excel',buf.getvalue(),file_name='laporan_statistika.xlsx',mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',use_container_width=True)
st.divider()
st.caption('🌈 StatVista • UTS Statistika 1B • Python · Streamlit · Pandas · NumPy · Plotly')
