import streamlit as st
from PIL import Image

st.set_page_config(
    page_title="Home",
    page_icon="🎲"
)


#image_path= '/Users/jhmartire/repos/ftc/dataset/'
image = Image.open( 'logo.png' )
st.sidebar.image( image, width=120 )

st.sidebar.markdown('# Cury Company')
st.sidebar.markdown('## Faster Delivery in Town')
st.sidebar.markdown( """___""" )

st.write("# Curry Company Growth Dashboard" )

st.markdown(
    """
    Growth Dashboard foi contruido para acompanhar as metricas de crescimento dos Entregadores e Restaurantes.
    ### Como Utilizar esse Growth Dashboard?
    - Visao Empresa:
        - Visao Gerencial: Metricas gerais de comportamento.
        - Visao Tatica: Indicadores semanais de crescimento.
        - Visao Geografica: Insights de geolocalizacao.
    - Visao Entregador:
        - Acompanhamento dos indicadores semanais de crescimento
    - Visao Restaurante:
        - Indicadores semanais de crescimento dos restaurantes
    ### Ask for Help
    - Time de Data Science no Discord
        - @jhmartire """)
