# Dashboard de Análise de Leads
# Criado com Streamlit e Plotly para análise avançada de performance de leads

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, date
import numpy as np

# CONFIGURAÇÃO DA PÁGINA
st.set_page_config(
    page_title="Dashboard de Leads",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# CSS CUSTOMIZADO - VERSÃO LIMPA SEM SIDEBAR
st.markdown("""
<style>
    /* CONFIGURAÇÕES GERAIS */
    .main {
        padding-top: 2rem;
    }
    
    /* TÍTULO PRINCIPAL */
    .main-title {
        font-size: 2.5rem !important;
        font-weight: 700 !important;
        color: #1e3d59 !important;
        text-align: center;
        margin-bottom: 2rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
    }
    
    /* SUBTÍTULOS */
    .section-title {
        font-size: 1.5rem !important;
        font-weight: 600 !important;
        color: #2c5f2d !important;
        margin-bottom: 1rem;
        border-bottom: 2px solid #97bc62;
        padding-bottom: 0.5rem;
    }
    
    /* CARTÕES DE KPI - Nova paleta roxa */
    .metric-card {
        background: linear-gradient(135deg, #72559a 0%, #9177d1 100%);
        padding: 1.5rem;
        border-radius: 15px;
        color: white !important;
        text-align: center;
        box-shadow: 0 8px 32px rgba(114,85,154,0.3);
        margin-bottom: 1rem;
        border: 1px solid rgba(255,255,255,0.2);
    }
    
    /* NÚMEROS DOS KPIs */
    .metric-number {
        font-size: 2.5rem !important;
        font-weight: 700 !important;
        color: #ffffff !important;
    }
    
    /* RÓTULOS DOS KPIs */
    .metric-label {
        font-size: 1rem !important;
        color: #f0f0f0 !important;
        margin-top: 0.5rem;
    }
    
    /* CARTÕES DE ALERTA */
    .alert-card {
        background: linear-gradient(135deg, #ff6b6b 0%, #ee5a52 100%);
        padding: 1.5rem;
        border-radius: 15px;
        color: white !important;
        text-align: center;
        box-shadow: 0 8px 32px rgba(255,0,0,0.1);
        margin-bottom: 1rem;
    }
    
    /* CARTÕES DE SUCESSO */
    .success-card {
        background: linear-gradient(135deg, #56ab2f 0%, #a8e6cf 100%);
        padding: 1.5rem;
        border-radius: 15px;
        color: white !important;
        text-align: center;
        box-shadow: 0 8px 32px rgba(0,255,0,0.1);
        margin-bottom: 1rem;
    }
    
    /* ESCONDER SIDEBAR COMPLETAMENTE */
    section[data-testid="stSidebar"] {
        display: none !important;
    }
    
    /* AJUSTAR CONTEÚDO PRINCIPAL SEM SIDEBAR */
    .main .block-container {
        padding-left: 1rem !important;
        padding-right: 1rem !important;
        max-width: 100% !important;
    }
    
    /* GRÁFICOS - Container dos gráficos */
    .plot-container {
        background: white;
        border-radius: 10px;
        padding: 1rem;
        box-shadow: 0 4px 16px rgba(0,0,0,0.1);
        margin-bottom: 2rem;
    }
    
    /* BOTÃO DE ATUALIZAR NO RODAPÉ - Nova paleta roxa */
    .refresh-button {
        position: fixed;
        bottom: 20px;
        right: 20px;
        background: linear-gradient(135deg, #72559a 0%, #9177d1 100%);
        color: white;
        border: none;
        border-radius: 50px;
        padding: 15px 20px;
        box-shadow: 0 4px 20px rgba(114,85,154, 0.4);
        cursor: pointer;
        font-size: 16px;
        font-weight: 600;
        transition: all 0.3s ease;
        z-index: 1000;
    }
    
    .refresh-button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 25px rgba(114,85,154, 0.6);
    }
    
    /* ESCONDER ELEMENTOS PADRÃO DO STREAMLIT */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* REMOVER DIVS VAZIAS */
    div:empty {
        display: none !important;
    }
    
    /* ESTILO PARA TABELA */
    .dataframe {
        font-size: 14px;
    }
    
    /* TABELA PERSONALIZADA */
    .custom-table {
        background: white;
        border-radius: 10px;
        padding: 1rem;
        box-shadow: 0 4px 16px rgba(0,0,0,0.1);
        margin-bottom: 2rem;
    }
</style>
""", unsafe_allow_html=True)

# FUNÇÃO PARA CARREGAR E PROCESSAR DADOS
@st.cache_data
def load_data(file_path=None):
    """
    Carrega e processa os dados do Excel
    """
    try:
        if file_path is None:
            file_path = r"dashboard_rank.xlsx"
        
        df = pd.read_excel(file_path)
        
        # LIMPEZA E FORMATAÇÃO DOS DADOS
        df['DATA_ABORDAGEM'] = pd.to_datetime(df['DATA_ABORDAGEM'], errors='coerce')
        df = df.dropna(subset=['DATA_ABORDAGEM'])
        
        text_columns = ['SEGMENTO', 'CANAL', 'RESULTADO']
        for col in text_columns:
            if col in df.columns:
                df[col] = df[col].astype(str).str.strip().str.upper()
        
        df['MES_ANO'] = df['DATA_ABORDAGEM'].dt.to_period('M')
        df['DIA'] = df['DATA_ABORDAGEM'].dt.date
        
        # CLASSIFICAÇÃO DE RESPOSTAS
        retornos_positivos = ['NEGATIVO', 'RESPONDEU E MARCOU CALL']
        df['TEVE_RETORNO'] = df['RESULTADO'].isin(retornos_positivos)
        
        respostas_efetivas = ['NEGATIVO', 'RESPONDEU E MARCOU CALL']
        df['RESPOSTA_EFETIVA'] = df['RESULTADO'].isin(respostas_efetivas)
        
        return df
    except Exception as e:
        st.error(f"Erro ao carregar o arquivo: {str(e)}")
        return None

# FUNÇÃO PARA CALCULAR KPIS
def calculate_kpis(df):
    """
    Calcula todos os KPIs necessários
    """
    kpis = {}
    
    # LEADS DO DIA MAIS RECENTE
    if not df.empty:
        kpis['leads_dia'] = len(df[df['DIA'] == df['DIA'].max()])
    else:
        kpis['leads_dia'] = 0
    
    # LEADS POR MÊS
    if not df.empty:
        kpis['leads_por_mes'] = df.groupby('MES_ANO').size().reset_index(name='leads')
        kpis['leads_por_mes']['mes_str'] = kpis['leads_por_mes']['MES_ANO'].astype(str)
    else:
        kpis['leads_por_mes'] = pd.DataFrame()
    
    # ANÁLISE DE CANAIS
    if len(df) > 0 and 'CANAL' in df.columns:
        canal_stats = df.groupby('CANAL').agg({
            'TEVE_RETORNO': ['count', 'sum'],
            'RESPOSTA_EFETIVA': 'sum'
        }).round(2)
        
        canal_stats.columns = ['total_leads', 'retornos', 'respostas_efetivas']
        canal_stats['taxa_retorno'] = (canal_stats['retornos'] / canal_stats['total_leads'] * 100).round(1)
        canal_stats['taxa_resposta_efetiva'] = (canal_stats['respostas_efetivas'] / canal_stats['total_leads'] * 100).round(1)
        canal_stats = canal_stats.reset_index()
        kpis['canal_performance'] = canal_stats
    else:
        kpis['canal_performance'] = pd.DataFrame()
    
    # ANÁLISE DE SEGMENTOS SEM RESPOSTA
    if 'SEGMENTO' in df.columns and 'RESULTADO' in df.columns:
        sem_resposta = df[df['RESULTADO'].isin(['NÃO RESPONDEU', 'VISUALIZOU E NÃO RESPONDEU'])]
        kpis['sem_resposta_por_segmento'] = sem_resposta.groupby('SEGMENTO').size().reset_index(name='quantidade')
    else:
        kpis['sem_resposta_por_segmento'] = pd.DataFrame()
    
    # ESTATÍSTICAS GERAIS
    total_leads = len(df)
    if 'RESULTADO' in df.columns:
        sem_resposta = df[df['RESULTADO'].isin(['NÃO RESPONDEU', 'VISUALIZOU E NÃO RESPONDEU'])]
        leads_sem_resposta = len(sem_resposta)
        kpis['total_sem_resposta'] = leads_sem_resposta
        kpis['percentual_sem_resposta'] = round(leads_sem_resposta / total_leads * 100, 1) if total_leads > 0 else 0
    else:
        kpis['total_sem_resposta'] = 0
        kpis['percentual_sem_resposta'] = 0
    
    # CORES MODERNAS - Nova paleta roxa
    cores_modernas = [
        '#72559a',  # Roxo escuro
        '#9177d1',  # Roxo médio
        '#c5a2f2',  # Roxo claro
        '#d5c5e3',  # Roxo muito claro
        '#f6f2fa',  # Quase branco
        '#72559a'   # Repetir primeira cor se necessário
    ]
    kpis['cores_modernas'] = cores_modernas
    
    return kpis

# FUNÇÃO PARA CRIAR GRÁFICOS
def create_charts(kpis):
    """
    Cria todos os gráficos do dashboard
    """
    charts = {}
    
    # GRÁFICO 1: Evolução mensal de leads
    if not kpis['leads_por_mes'].empty:
        try:
            kpis['leads_por_mes']['periodo_formatado'] = kpis['leads_por_mes']['MES_ANO'].dt.strftime('%b/%Y')
        except:
            kpis['leads_por_mes']['periodo_formatado'] = kpis['leads_por_mes']['MES_ANO'].astype(str)
        
        fig_monthly = px.line(
            kpis['leads_por_mes'], 
            x='periodo_formatado', 
            y='leads',
            title='📈 Evolução Mensal de Leads',
            markers=True
        )
        
        fig_monthly.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font_family="Inter, -apple-system, BlinkMacSystemFont, sans-serif",
            title_font_size=20,
            title_font_color='#1f2937',
            title_x=0.02,
            xaxis_title="",
            yaxis_title="Leads",
            showlegend=False,
            margin=dict(l=40, r=40, t=60, b=40),
            xaxis=dict(
                showgrid=False,
                showline=False,
                zeroline=False,
                tickfont=dict(color='#6b7280', size=12)
            ),
            yaxis=dict(
                showgrid=True,
                gridcolor='rgba(0,0,0,0.05)',
                showline=False,
                zeroline=False,
                tickfont=dict(color='#6b7280', size=12)
            )
        )
        
        fig_monthly.update_traces(
            line=dict(color='#72559a', width=3),
            marker=dict(color='#72559a', size=8, line=dict(color='white', width=2)),
            hovertemplate='<b>%{x}</b><br>Leads: %{y}<extra></extra>'
        )
        charts['monthly_evolution'] = fig_monthly
    
    # GRÁFICO 2: Performance por canal
    if not kpis['canal_performance'].empty:
        fig_channel = go.Figure(data=[go.Pie(
            labels=kpis['canal_performance']['CANAL'],
            values=kpis['canal_performance']['taxa_retorno'],
            hole=0.8,
            marker=dict(
                colors=kpis['cores_modernas'][:len(kpis['canal_performance'])],
                line=dict(color='white', width=3)
            ),
            textinfo='label+percent',
            textfont=dict(size=14, color='#72559a'),
            hovertemplate='<b>%{label}</b><br>Taxa: %{value}%<extra></extra>'
        )])
        
        fig_channel.update_layout(
            title='📊 Taxa de Retorno por Canal',
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font_family="Inter, -apple-system, BlinkMacSystemFont, sans-serif",
            title_font_size=20,
            title_font_color='#1f2937',
            title_x=0.02,
            showlegend=True,
            legend=dict(
                orientation="v",
                yanchor="middle",
                y=0.5,
                xanchor="left",
                x=1.05,
                font=dict(size=12)
            ),
            margin=dict(l=40, r=120, t=60, b=40),
            annotations=[dict(
                text=f"Taxa Média<br><b>{kpis['canal_performance']['taxa_retorno'].mean():.1f}%</b>",
                x=0.5, y=0.5,
                font_size=16,
                font_color='#72559a',
                showarrow=False
            )]
        )
        charts['channel_performance'] = fig_channel
    
    # GRÁFICO 3: Segmentos sem resposta
    if not kpis['sem_resposta_por_segmento'].empty:
        fig_segments = go.Figure(data=[go.Pie(
            labels=kpis['sem_resposta_por_segmento']['SEGMENTO'],
            values=kpis['sem_resposta_por_segmento']['quantidade'],
            hole=0.8,
            marker=dict(
                colors=kpis['cores_modernas'][:len(kpis['sem_resposta_por_segmento'])],
                line=dict(color='white', width=3)
            ),
            textinfo='label+percent',
            textfont=dict(size=14, color='#72559a'),
            hovertemplate='<b>%{label}</b><br>Sem resposta: %{value}<extra></extra>'
        )])
        
        fig_segments.update_layout(
            title='🎯 Distribuição de Não Respostas por Segmento',
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font_family="Inter, -apple-system, BlinkMacSystemFont, sans-serif",
            title_font_size=20,
            title_font_color='#1f2937',
            title_x=0.02,
            showlegend=True,
            legend=dict(
                orientation="h",
                yanchor="top",
                y=-0.05,
                xanchor="center",
                x=0.5,
                font=dict(size=12)
            ),
            margin=dict(l=40, r=40, t=60, b=80),
            annotations=[dict(
                text=f"Total<br><b>{kpis['sem_resposta_por_segmento']['quantidade'].sum()}</b>",
                x=0.5, y=0.5,
                font_size=16,
                font_color='#72559a',
                showarrow=False
            )]
        )
        charts['segments_no_response'] = fig_segments
    
    return charts

# INTERFACE PRINCIPAL
def main():
    # TÍTULO PRINCIPAL
    st.markdown('<h1 class="main-title">📊 Dashboard de Análise de Leads</h1>', unsafe_allow_html=True)
    
    try:
        # Carrega os dados automaticamente
        df = load_data()
        
        if df is None:
            return
        
        # Calcula KPIs
        kpis = calculate_kpis(df)
        
        # SEÇÃO 1: KPIs PRINCIPAIS
        st.markdown('<h2 class="section-title">📈 KPIs Principais</h2>', unsafe_allow_html=True)
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-number">{kpis['leads_dia']}</div>
                <div class="metric-label">Leads Abordados Hoje</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="alert-card">
                <div class="metric-number">{kpis['total_sem_resposta']}</div>
                <div class="metric-label">Leads Sem Resposta</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
            <div class="alert-card">
                <div class="metric-number">{kpis['percentual_sem_resposta']}%</div>
                <div class="metric-label">% Sem Resposta</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            total_leads = len(df)
            st.markdown(f"""
            <div class="success-card">
                <div class="metric-number">{total_leads}</div>
                <div class="metric-label">Total de Leads</div>
            </div>
            """, unsafe_allow_html=True)
        
        # SEÇÃO 2: GRÁFICOS ANALÍTICOS
        st.markdown('<h2 class="section-title">📊 Análises Detalhadas</h2>', unsafe_allow_html=True)
        
        charts = create_charts(kpis)
        
        # Layout dos gráficos
        col_left, col_right = st.columns([2, 1])
        
        with col_left:
            if 'monthly_evolution' in charts:
                st.plotly_chart(charts['monthly_evolution'], use_container_width=True)
        
        with col_right:
            if 'channel_performance' in charts:
                st.plotly_chart(charts['channel_performance'], use_container_width=True)
        
        # Gráfico de segmentos (largura total)
        if 'segments_no_response' in charts:
            st.plotly_chart(charts['segments_no_response'], use_container_width=True)
        
        # SEÇÃO 3: TABELA DETALHADA
        st.markdown('<h2 class="section-title">📋 Detalhamento por Canal</h2>', unsafe_allow_html=True)
        
        if not kpis['canal_performance'].empty:
            # Criar tabela formatada
            canal_df = kpis['canal_performance'].copy()
            canal_df.columns = ['Canal', 'Total Leads', 'Retornos', 'Respostas Efetivas', 'Taxa Retorno (%)', 'Taxa Resposta (%)']
            
            # Formatação de valores
            canal_df['Taxa Retorno (%)'] = canal_df['Taxa Retorno (%)'].apply(lambda x: f"{x:.1f}%")
            canal_df['Taxa Resposta (%)'] = canal_df['Taxa Resposta (%)'].apply(lambda x: f"{x:.1f}%")
            
            st.dataframe(
                canal_df, 
                use_container_width=True, 
                hide_index=True,
                column_config={
                    "Canal": st.column_config.TextColumn("Canal", width="medium"),
                    "Total Leads": st.column_config.NumberColumn("Total Leads", format="%d"),
                    "Retornos": st.column_config.NumberColumn("Retornos", format="%d"),
                    "Respostas Efetivas": st.column_config.NumberColumn("Respostas Efetivas", format="%d"),
                    "Taxa Retorno (%)": st.column_config.TextColumn("Taxa Retorno"),
                    "Taxa Resposta (%)": st.column_config.TextColumn("Taxa Resposta")
                }
            )
        else:
            st.warning("⚠️ Nenhum dado disponível para exibir o detalhamento por canal.")
        
        # SEÇÃO 4: INSIGHTS AUTOMÁTICOS
        st.markdown('<h2 class="section-title">💡 Insights Automáticos</h2>', unsafe_allow_html=True)
        
        if not kpis['canal_performance'].empty:
            best_channel = kpis['canal_performance'].loc[kpis['canal_performance']['taxa_retorno'].idxmax(), 'CANAL']
            best_rate = kpis['canal_performance']['taxa_retorno'].max()
            
            if not kpis['sem_resposta_por_segmento'].empty:
                worst_segment = kpis['sem_resposta_por_segmento'].loc[kpis['sem_resposta_por_segmento']['quantidade'].idxmax(), 'SEGMENTO']
                worst_count = kpis['sem_resposta_por_segmento']['quantidade'].max()
                
                st.info(f"""
                **🏆 Canal Mais Eficiente:** {best_channel} com {best_rate:.1f}% de taxa de retorno
                
                **⚠️ Segmento com Mais Não Respostas:** {worst_segment} ({worst_count} leads sem resposta)
                
                **📊 Recomendação:** Foque seus esforços no canal {best_channel} e revise a estratégia para o segmento {worst_segment}
                """)
            else:
                st.info(f"""
                **🏆 Canal Mais Eficiente:** {best_channel} com {best_rate:.1f}% de taxa de retorno
                
                **📊 Recomendação:** Continue focando no canal {best_channel} para maximizar resultados.
                """)
        
        # BOTÃO DE ATUALIZAR FIXO NO CANTO INFERIOR DIREITO
        st.markdown("""
        <div style="position: fixed; bottom: 20px; right: 20px; z-index: 1000;">
            <form>
                <button type="submit" class="refresh-button" onclick="window.location.reload()">
                    🔄 Atualizar
                </button>
            </form>
        </div>
        """, unsafe_allow_html=True)
        
        # JavaScript para funcionalidade do botão
        st.markdown("""
        <script>
        document.querySelector('.refresh-button').addEventListener('click', function(e) {
            e.preventDefault();
            window.location.reload();
        });
        </script>
        """, unsafe_allow_html=True)
        
    except FileNotFoundError:
        st.error("❌ **Arquivo não encontrado!**")
        st.markdown("""
        **Verifique se:**
        - O arquivo `dashboard_rank.xlsx` existe na pasta especificada
        - O caminho está correto
        - Você tem permissão para acessar o arquivo
        """)
        
    except Exception as e:
        st.error(f"❌ **Erro ao carregar o arquivo:** {str(e)}")
        st.markdown("**Detalhes do erro podem ajudar na identificação do problema.**")

if __name__ == "__main__":
    main()
