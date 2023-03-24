
# Libraries
from haversine import haversine
import plotly.express       as px 
import plotly.graph_objects as go 


# Bibliotecas Necessarias
import pandas               as pd
import streamlit            as st
from PIL import             Image
import folium 
from streamlit_folium import folium_static

st.set_page_config( page_title='Visao Empresa', page_icon='📈', layout='wide' )

#---------------------------------------
# FUNCOES
#---------------------------------------

def country_maps( df1 ):
    df_aux = ( df1.loc[:, ['City','Road_traffic_density','Delivery_location_latitude','Delivery_location_longitude']]
                  .groupby(['City','Road_traffic_density'])
                  .median()
                  .reset_index() )

    map = folium.Map()
    for index, location_info in df_aux.iterrows():
      folium.Marker([location_info['Delivery_location_latitude'],
                     location_info['Delivery_location_longitude']],
                    popup=location_info[['City', 'Road_traffic_density']] ).add_to( map)
    folium_static( map,width=1024, height=600 )
        

def order_share_by_week( df1 ):
    df_aux01 = df1.loc[:,['ID', 'week_of_year']].groupby('week_of_year').count().reset_index()
    df_aux02 = ( df1.loc[:,['Delivery_person_ID', 'week_of_year']]
                    .groupby('week_of_year')
                    .nunique()
                    .reset_index() )
    df_aux = pd.merge(df_aux01, df_aux02, how='inner', on='week_of_year')
    df_aux['order_by_deliver'] = df_aux['ID'] / df_aux['Delivery_person_ID']

    fig = px.line(df_aux, x='week_of_year', y='order_by_deliver')
            
    return fig 

def order_by_week( df1 ):            
    #CRIAR A COLUNA DA SEMANA.              
    df1['week_of_year'] = df1['Order_Date'].dt.strftime('%U') 
    df_aux = df1.loc[:,['ID', 'week_of_year']].groupby('week_of_year').count().reset_index()
    fig = px.line(df_aux, x='week_of_year', y='ID')
            
    return fig

def traffic_order_city( df1 ):                 
    df_aux = ( df1.loc[:,['ID','City','Road_traffic_density']]
                  .groupby(['City', 'Road_traffic_density'])
                  .count()
                  .reset_index() )
    fig = px.scatter(df_aux,x='City',y='Road_traffic_density', size='ID',color='City')
                
    return fig
                

def traffic_order_share( df1 ):              
    df_aux= ( df1.loc[:,['ID','Road_traffic_density']]
                 .groupby('Road_traffic_density')
                 .count()
                 .reset_index() )
    
    df_aux = df_aux.loc[df_aux['Road_traffic_density'] != "NaN",:]
    df_aux['entregas_perc'] = df_aux['ID'] / df_aux['ID'].sum()
    fig = px.pie( df_aux, values='entregas_perc', names='Road_traffic_density' )
    return fig

def order_metric( df1 ):
    cols = ['ID', 'Order_Date']
    #SELECAO DE LINHAS
    df_aux =  df1.loc[:,cols].groupby( 'Order_Date' ).count().reset_index()
    # DESENHAR O GRAFICO DE LINHAS
    fig = px.bar(df_aux,x='Order_Date',y='ID')
            
    return fig

def clean_code( df1 ):
    """ Esta funcao tem a responsabilidade de limpar o dataframe
    
    Tipos de Limpezas:
    1. Remocao dos dados NaN
    2. Mudanca do tipo da coluna de dados
    3. Remocao dos espaco das variaveis de texto
    4. Formatacao da coluna de datas
    5. Limpeza da coluna de tempo ( remocao do texto da variavel numerica )
    
    Input:  Dataframe
    Output: Dataframe
    
    """
    
    # 1. CONVERTENDO A COLUNA AGE DE TEXTO PARA NUMERO
    linhas_selecionadas = (df1['Delivery_person_Age'] != 'NaN ')
    df1 = df1.loc[linhas_selecionadas, :].copy()

    linhas_selecionadas = (df1['Road_traffic_density'] != 'NaN ')
    df1 = df1.loc[linhas_selecionadas, :].copy()
    
    linhas_selecionadas = (df1['City'] != 'NaN ')
    df1 = df1.loc[linhas_selecionadas, :].copy()

    linhas_selecionadas = (df1['Festival'] != 'NaN ')
    df1 = df1.loc[linhas_selecionadas, :].copy()

    df1['Delivery_person_Age'] = df1['Delivery_person_Age'].astype(int)


    # 2. CONVERTENDO A COLUNA RATINS DE TEXTO PARA NUMERO DECIMAL ( FLOAT)
    df1['Delivery_person_Ratings'] = df1['Delivery_person_Ratings'].astype(float)



    # 3. CONVERTENDO A COLUNA ORDER_DATE DE TEXTO PARA DATA
    df1['Order_Date'] = pd.to_datetime(df1['Order_Date'], format='%d-%m-%Y')

    # 4. CONVERETENDO MULTIPLE_DELIVERIES DE TEXTO PARA NUMERO INTEIRO ( INT )
    linhas_selecionadas = (df1['multiple_deliveries'] != 'NaN ')
    df1 = df1.loc[linhas_selecionadas, :].copy()
    df1['multiple_deliveries'] = df1['multiple_deliveries'].astype(int)

    # 5. REMOVENDO OS ESPACOS DENTRO DE STRINGS/TEXTO/OBJETOS  ESSA OPCAO E COM LUP FOR E UM POUCO DEMORADA
    # df1 = df1.reset_index(drop=True)
    # for i in range(len( df1 ) ):
      # df1.loc[i,'ID'] = df1.loc[i, 'ID'].strip()

    # 6. REMOVENDO OS ESPACOS DENTRO DE STRINGS/TEXTO/OBJETOS <- ESSA OPCAO E SEM O LUP FOR E MAIS RAPIDA 
    df1.loc[:, 'ID'] = df1.loc[:, 'ID'].str.strip()
    df1.loc[:, 'Road_traffic_density'] = df1.loc[:, 'Road_traffic_density'].str.strip()
    df1.loc[:, 'Type_of_order'] = df1.loc[:, 'Type_of_order'].str.strip()
    df1.loc[:, 'Type_of_vehicle'] = df1.loc[:, 'Type_of_vehicle'].str.strip()
    df1.loc[:, 'City'] = df1.loc[:, 'City'].str.strip()
    df1.loc[:, 'Festival'] = df1.loc[:, 'Festival'].str.strip()


    # 7. LIMPANDO  A COLUNA TIME TAKEN

    df1['Time_taken(min)'] = df1['Time_taken(min)'].apply(lambda x: x.split('(min)')[1] )
    df1['Time_taken(min'] = df1['Time_taken(min)'].astype(int)

    df1['Time_taken(min)'] = df1 ['Time_taken(min)'].astype(float)
    
    return df1




#---------------------------------- INICIO DA ESTRUTURA LOGICA DO CODIGO-----------------------------------
#----------------------------------
# Import dataset
#----------------------------------

# df = pd.read_csv('../train.csv')
#df = pd.read_csv('ftc/train.csv')
df = pd.read_csv('/Users/jhmartire/repos/ftc/train.csv')


#----------------------------------
# LIMPANDO OS DADOS
#----------------------------------

df1 = clean_code( df )


#=====================================
#           SIDE BAR
#=====================================

st.header('Marketplace - Visao Cliente')


image_path = 'logo.png'
image = Image.open( 'logo.png' )
st.sidebar.image( image, width=120 )



st.sidebar.markdown('# Cury Company')
st.sidebar.markdown('## Faster Delivery in Town')
st.sidebar.markdown( """___""" )

st.sidebar.markdown('##Selecione uma data limite')
date_slider = st.sidebar.slider(
    'Ate qual valor?',
    value=pd.datetime(2022,4,13),
    min_value=pd.datetime(2022, 2, 11),
    max_value=pd.datetime(2022, 4, 6 ),
    format='DD-MM-YYYY')


st.sidebar.markdown( """___""" )

traffic_options = st.sidebar.multiselect(
    'Quais as condicoes de transito',
    ['Low', 'Medium', 'High', 'Jam'],
    default=['Low', 'Medium', 'High', 'Jam'] )

st.sidebar.markdown( """___""" )
st.sidebar.markdown( '### Powerd by Comunidade DS')

# FILTROS DE DATA


linhas_selecionadas = df1['Order_Date'] < date_slider
df1 = df1.loc[linhas_selecionadas, : ]


# FILTRO DE TRANSITO
linhas_selecionadas = df1['Road_traffic_density'].isin( traffic_options )
df1 = df1.loc[ linhas_selecionadas, : ]



#=====================================
#     LAYOUT NO STREAMLIT
#=====================================

tab1, tab2, tab3 = st.tabs( ['Visao Gerencial', 'Visao Tatica', 'Visao Geografica'] )

with tab1:
    with st.container():
        # ORDER METRIC
        fig = order_metric( df1 )
        st.markdown( '# Orders by Day' )
        st.plotly_chart( fig, use_container_width=True )
            
    
    with st.container():
        col1, col2 = st.columns( 2 )
        
        with col1:
            fig = traffic_order_share( df1 )
            st.header( "Traffic Order Share" )
            st.plotly_chart( fig, use_container_width=True )
            

        with col2:
            st.header( " Traffic Order City" )
            fig = traffic_order_city( df1 )
            st.plotly_chart( fig, use_container_width=True )
            

with tab2:
    with st.container():
        st.markdown( "# Order by Week" )
        fig = order_by_week( df1 )
        st.plotly_chart( fig, use_container_width=True )

        
    with st.container():
        st.markdown("# Order Share by Week")
        fig = order_share_by_week( df1 )
        st.plotly_chart( fig, use_container_width=True )
        
    
with tab3:
    st.markdown( "# Country Maps" )
    country_maps( df1 )
    
