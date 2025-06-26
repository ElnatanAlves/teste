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
        
        # CORREÇÃO 1: Criar campo para evolução DIÁRIA em vez de mensal
        df['DIA'] = df['DATA_ABORDAGEM'].dt.date
        df['MES_ANO'] = df['DATA_ABORDAGEM'].dt.to_period('M')
        
        # CORREÇÃO 2: Lógica corrigida para classificação de respostas
        # Definir corretamente quais são as respostas positivas/efetivas
        respostas_positivas = ['RESPONDEU E MARCOU CALL', 'POSITIVO', 'INTERESSADO']
        respostas_efetivas = ['RESPONDEU E MARCOU CALL', 'NEGATIVO', 'POSITIVO', 'INTERESSADO']
        sem_resposta = ['NÃO RESPONDEU', 'VISUALIZOU E NÃO RESPONDEU']
        
        # Criar flags corretas
        df['TEVE_RETORNO'] = ~df['RESULTADO'].isin(sem_resposta)
        df['RESPOSTA_POSITIVA'] = df['RESULTADO'].isin(respostas_positivas)
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
    
    # CORREÇÃO: EVOLUÇÃO DIÁRIA em vez de mensal
    if not df.empty:
        leads_por_dia = df.groupby('DIA').size().reset_index(name='leads')
        leads_por_dia['dia_formatado'] = pd.to_datetime(leads_por_dia['DIA']).dt.strftime('%d/%m')
        # Ordenar por data para garantir sequência correta
        leads_por_dia = leads_por_dia.sort_values('DIA')
        kpis['leads_por_dia'] = leads_por_dia
    else:
        kpis['leads_por_dia'] = pd.DataFrame()
    
    # CORREÇÃO DEFINITIVA: Análise de canais simplificada e robusta
    if len(df) > 0 and 'CANAL' in df.columns and 'RESULTADO' in df.columns:
        # Método mais direto - contar por canal
        canal_counts = df.groupby('CANAL').size().reset_index(name='total_leads')
        
        # Para cada canal, calcular estatísticas
        canal_stats_list = []
        
        for canal in canal_counts['CANAL'].unique():
            canal_df = df[df['CANAL'] == canal]
            
            total = len(canal_df)
            
            # Contar tipos de resposta diretamente
            sem_resposta = len(canal_df[canal_df['RESULTADO'].isin(['NÃO RESPONDEU', 'VISUALIZOU E NÃO RESPONDEU'])])
            com_retorno = total - sem_resposta
            
            # Respostas específicas
            negativo = len(canal_df[canal_df['RESULTADO'] == 'NEGATIVO'])
            positivo = len(canal_df[canal_df['RESULTADO'].isin(['POSITIVO', 'INTERESSADO', 'RESPONDEU E MARCOU CALL'])])
            
            # Calcular taxas
            taxa_retorno = (com_retorno / total * 100) if total > 0 else 0
            taxa_positiva = (positivo / total * 100) if total > 0 else 0
            
            canal_stats_list.append({
                'CANAL': canal,
                'total_leads': total,
                'com_retorno': com_retorno,
                'sem_resposta': sem_resposta,
                'respostas_negativas': negativo,
                'respostas_positivas': positivo,
                'taxa_retorno': round(taxa_retorno, 1),
                'taxa_positiva': round(taxa_positiva, 1)
            })
        
        kpis['canal_performance'] = pd.DataFrame(canal_stats_list)
    else:
        kpis['canal_performance'] = pd.DataFrame()
    
    # ANÁLISE DE SEGMENTOS SEM RESPOSTA
    if 'SEGMENTO' in df.columns and 'RESULTADO' in df.columns:
        sem_resposta_lista = ['NÃO RESPONDEU', 'VISUALIZOU E NÃO RESPONDEU']
        sem_resposta = df[df['RESULTADO'].isin(sem_resposta_lista)]
        if not sem_resposta.empty:
            kpis['sem_resposta_por_segmento'] = sem_resposta.groupby('SEGMENTO').size().reset_index(name='quantidade')
        else:
            kpis['sem_resposta_por_segmento'] = pd.DataFrame()
    else:
        kpis['sem_resposta_por_segmento'] = pd.DataFrame()
    
    # ESTATÍSTICAS GERAIS
    total_leads = len(df)
    if 'RESULTADO' in df.columns:
        sem_resposta_lista = ['NÃO RESPONDEU', 'VISUALIZOU E NÃO RESPONDEU']
        leads_sem_resposta = len(df[df['RESULTADO'].isin(sem_resposta_lista)])
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
        '#e74c3c',  # Vermelho para contraste
        '#3498db',  # Azul para contraste
        '#2ecc71'   # Verde para contraste
    ]
    kpis['cores_modernas'] = cores_modernas
    
    return kpis

# FUNÇÃO PARA CRIAR GRÁFICOS
def create_charts(kpis):
    """
    Cria todos os gráficos do dashboard
    """
    charts = {}
    
    # GRÁFICO 1: Evolução DIÁRIA de leads (CORRIGIDO)
    if not kpis['leads_por_dia'].empty:
        fig_daily = px.line(
            kpis['leads_por_dia'], 
            x='dia_formatado', 
            y='leads',
            title='📈 Evolução Diária de Leads',
            markers=True
        )
        
        fig_daily.update_layout(
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)',
            font_family="Inter, -apple-system, BlinkMacSystemFont, sans-serif",
            title_font_size=20,
            title_font_color='#1f2937',
            title_x=0.02,
            xaxis_title="Dia",
            yaxis_title="Quantidade de Leads",
            showlegend=False,
            margin=dict(l=40, r=40, t=60, b=40),
            xaxis=dict(
                showgrid=False,
                showline=False,
                zeroline=False,
                tickfont=dict(color='#6b7280', size=12),
                tickangle=45
            ),
            yaxis=dict(
                showgrid=True,
                gridcolor='rgba(0,0,0,0.05)',
                showline=False,
                zeroline=False,
                tickfont=dict(color='#6b7280', size=12)
            )
        )
        
        fig_daily.update_traces(
            line=dict(color='#72559a', width=3),
            marker=dict(color='#72559a', size=8, line=dict(color='white', width=2)),
            hovertemplate='<b>Dia %{x}</b><br>Leads: %{y}<extra></extra>'
        )
        charts['daily_evolution'] = fig_daily
    
    # GRÁFICO 2: Lead's que me responderam (NOME ALTERADO)
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
            hovertemplate='<b>%{label}</b><br>Taxa de Retorno: %{value}%<br>Total: %{customdata} leads<extra></extra>',
            customdata=kpis['canal_performance']['total_leads']
        )])
        
        fig_channel.update_layout(
            title='📊 Lead\'s que me responderam',
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
    
    # GRÁFICO 3: Lead que não responderam (NOME ALTERADO)
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
            title='🎯 Lead's que não responderam',
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
    st.markdown('<h1 class="main-title">📊 Dashboard Comercial Rankrup</h1>', unsafe_allow_html=True)
    
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
            if 'daily_evolution' in charts:
                st.plotly_chart(charts['daily_evolution'], use_container_width=True)
        
        with col_right:
            if 'channel_performance' in charts:
                st.plotly_chart(charts['channel_performance'], use_container_width=True)
        
        # Gráfico de segmentos (largura total)
        if 'segments_no_response' in charts:
            st.plotly_chart(charts['segments_no_response'], use_container_width=True)
        
        # SEÇÃO 3: INSIGHTS AUTOMÁTICOS
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
        else:
            st.warning("⚠️ Não foi possível gerar insights. Verifique os dados de canal.")
        
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
        st.write("Erro detalhado:", str(e))

if __name__ == "__main__":
    main()
