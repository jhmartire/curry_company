
# Libraries
from haversine import haversine
import plotly.express       as px 
import plotly.graph_objects as go 


# Bibliotecas Necessarias
import pandas               as pd
import numpy                as np
import streamlit            as st
from PIL import             Image
import folium 
from streamlit_folium import folium_static
from pandas.core.frame import ColspaceArgType

st.set_page_config( page_title='Visao Restaurantes', page_icon='🍛', layout='wide' )

#---------------------------------------
# FUNCOES
#---------------------------------------

def avg_std_time_on_traffic( df1 ):
    df_aux = (df1.loc[:, ['City', 'Time_taken(min)','Road_traffic_density']]
                 .groupby(['City','Road_traffic_density' ])
                 .agg({ 'Time_taken(min)': ['mean', 'std']} ) )
    df_aux.columns = ['avg_time', 'std_time']
    df_aux = df_aux.reset_index()
    fig = px.sunburst(df_aux, path=['City', 'Road_traffic_density'], values='avg_time',
                                  color='std_time', color_continuous_scale='RdBu',
                                  color_continuous_midpoint=np.average(df_aux['std_time'] ) )
    return fig 

def avg_std_time_graph( df1 ):
    st.markdown( "###### Tempo medio de entrega por Cidade" )     
    df_aux = df1.loc[:, ['City', 'Time_taken(min)']].groupby('City').agg({ 'Time_taken(min)': ['mean', 'std']} )
    df_aux.columns = ['avg_time', 'std_time']
    df_aux = df_aux.reset_index()

    fig = go.Figure()
    fig.add_trace(go.Bar(name='Control',x=df_aux['City'],y=df_aux['avg_time'],error_y=dict( type='data', array=df_aux['std_time'] ) ) )    
    fig.update_layout(barmode='group')
                
    return fig 

def avg_std_time_delivery(df1, festival, op):
    """
    ESTA FUNCAO CALCULA O TEMPO MEDIO E O DESVIO PADRAO DO TEMPO DE ENTREGA.
    PARAMETROS:
        INPUT:
            - df: DATAFRAME COM OS DADOS NECESSARIOS PARA OS CALCULO
            - op: TIPO DE OPERACAO QUE PRECISA SER CALCULADO
                'avg_time': CALCULA O TEMPO MEDIO
                'std_time': CALCULA O DESVEIO PADRAO DO TEMPO.
        OUTPUT:
            - df: DATAFRAME COM 2 COLUNAS E 1 LINHA.
    """
    df_aux = (df1.loc[:, ['Time_taken(min)','Festival']]
              .groupby('Festival')
              .agg({'Time_taken(min)': ['mean', 'std']}))

    df_aux.columns = ['avg_time', 'std_time']
    df_aux = df_aux.reset_index()
    df_aux = np.round(df_aux.loc[df_aux['Festival'] == festival, op], 2 )

    return df_aux


def distance( df1, fig ):
    if fig == False:
        cols = ['Delivery_location_latitude','Delivery_location_longitude','Restaurant_longitude','Restaurant_latitude']
        df1['distance'] = df1.loc[:, cols].apply(lambda x:
                              haversine((x['Restaurant_latitude'], x['Restaurant_longitude']),
                              (x['Delivery_location_latitude'], x['Delivery_location_longitude'])), axis=1 )
        avg_distance = np.round( df1['distance'].mean(), 2 )
        return avg_distance
    
    else:
        cols = ['Delivery_location_latitude','Delivery_location_longitude','Restaurant_longitude','Restaurant_latitude']
        df1['distance'] = df1.loc[:, cols].apply(lambda x:
                              haversine((x['Restaurant_latitude'], x['Restaurant_longitude']),
                              (x['Delivery_location_latitude'], x['Delivery_location_longitude'])), axis=1 )
        avg_distance = df1.loc[:,['City', 'distance']].groupby( 'City' ).mean().reset_index()
        fig = go.Figure( data=[go.Pie(labels=avg_distance['City'], values=avg_distance['distance'],pull=[0, 0.1, 0])])
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

#------------------------------
# IMPORT DATAFRAME
#------------------------------

# df = pd.read_csv('../train.csv')
#df = pd.read_csv('ftc/train.csv')
df = pd.read_csv('/Users/jhmartire/repos/ftc/train.csv')


#CLEANING DATAFRAME
df1 = clean_code( df )

#=====================================
#           SIDE BAR
#=====================================

st.header('Marketplace - Visao Restaurante')

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

weather_conditions = st.sidebar.multiselect(
    'Quais as condicoes Climaticas',
    ['conditions Sunny', 'conditions Stormy', 'conditions Sandstorms',
       'conditions Cloudy', 'conditions Fog', 'conditions Windy'],
    default=['conditions Sunny', 'conditions Stormy', 'conditions Sandstorms',
       'conditions Cloudy', 'conditions Fog', 'conditions Windy'] )

st.sidebar.markdown( """___""" )
st.sidebar.markdown( '### Powerd by Comunidade DS')

# FILTROS DE DATA


linhas_selecionadas = df1['Order_Date'] < date_slider
df1 = df1.loc[linhas_selecionadas, : ]


# FILTRO DE TRANSITO
linhas_selecionadas = df1['Road_traffic_density'].isin( traffic_options )
df1 = df1.loc[ linhas_selecionadas, : ]

# FILTRO DE CLIMA
linhas_selecionadas = df1['Weatherconditions'].isin( weather_conditions )
df1 = df1.loc[ linhas_selecionadas, : ]


#=====================================
#     LAYOUT NO STREAMLIT
#=====================================
tab1, tab2, tab3 = st.tabs( ['Visao Gerencial', '_', '_'] )

with tab1:
    with st.container():
        st.title( "Overal Metrics" )
        
        col1, col2, col3, col4, col5, col6 = st.columns( 6 )
        with col1:
            delivery_unique = len( df1.loc[:,'Delivery_person_ID'].unique() )
            col1.metric( 'Entregadores', delivery_unique )
            
        with col2:
                avg_distance = distance( df1, fig=False )
                col2.metric( 'A distancia media', avg_distance )
     

        with col3:
            df_aux = avg_std_time_delivery( df1,'Yes', 'avg_time' )
            col3.metric('Tempo Medio', df_aux )

            
        with col4:
            df_aux = avg_std_time_delivery( df1,'Yes', 'std_time' )
            col4.metric('STD Entrega', df_aux )

            
        with col5:
            df_aux = avg_std_time_delivery( df1,'No', 'avg_time' )  
            col5.metric('Tempo Medio', df_aux )
  

        with col6:
            df_aux = avg_std_time_delivery( df1,'No', 'std_time' )          
            col6.metric('STD Entrega', df_aux )
            
        
    with st.container():
        st.markdown( """___""" )
        col1, col2= st.columns( 2 )
        
        with col1:
            fig = avg_std_time_graph( df1 )
            st.plotly_chart( fig )
        with col2:
            st.markdown( "###### Distribuicao da Distancia" )

            df_aux = ( df1.loc[:, ['City', 'Time_taken(min)','Type_of_order']]
                          .groupby(['City','Type_of_order' ])
                          .agg({ 'Time_taken(min)': ['mean', 'std']} ) )
            df_aux.columns = ['avg_time', 'std_time']
            df_aux = df_aux.reset_index()

            st.dataframe( df_aux )


    with st.container():
        st.markdown( """___""" )
        st.title( "Distribuicao do Tempo" )
        
        col1, col2 = st.columns( 2 )
        with col1:
            fig = distance( df1, fig=True )
            st.plotly_chart( fig )


        with col2:
            fig = avg_std_time_on_traffic( df1 )    
            st.plotly_chart( fig )

        
        
        
        
