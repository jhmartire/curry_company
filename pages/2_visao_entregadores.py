
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

st.set_page_config( page_title='Visao Entregadores', page_icon='🚚', layout='wide' )

#---------------------------------------
# FUNCOES
#---------------------------------------

def top_delivers( df1, top_asc ):
    df2 = (df1.loc[:,['Delivery_person_ID', 'City', 'Time_taken(min)']]
              .groupby(['City', 'Delivery_person_ID'] )
              .mean()
              .sort_values(['City', 'Time_taken(min)'], ascending=top_asc ).reset_index())
    df_aux01 = df2.loc[df2['City'] == 'Metropolitian',:].head(10)
    df_aux02 = df2.loc[df2['City'] == 'Urban',:].head(10)
    df_aux03 = df2.loc[df2['City'] == 'Semi-Urban',:].head(10)
                    
    df3 = pd.concat([df_aux01, df_aux02, df_aux03]).reset_index( drop=True)
                    
    return df3

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


# IMPORT DATASET
df = pd.read_csv( 'train.csv' )

#CLEANING DATASET
df1 = clean_code( df )



#=====================================
#           SIDE BAR
#=====================================

st.header('Marketplace - Visao Entregadores')

#image_path = 'logo.png'
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

tab1, tab2, tab3 = st.tabs( ['Visao Gerencial', '_', '_' ]  )

with tab1:
    with st.container():
        st.title( 'Overall Metrics')
        
        col1, col2, col3, col4 = st.columns( 4, gap='large' )
        with col1:
             # A Maior idade dos entregadores
            maior_idade = df1.loc[:,'Delivery_person_Age'].max()
            col1.metric( 'Maior de idade', maior_idade )

        with col2:
             # A Menor idade dos entregadores
            menor_idade = df1.loc[:,'Delivery_person_Age'].min()
            col2.metric( 'Menor de idade', menor_idade )
            
        with col3:
            # A Melhor condicao de Veiculo
            melhor_condicao = df1.loc[:,'Vehicle_condition'].max()
            col3.metric( 'Melhor condicao de Veiculo', melhor_condicao )

            
        with col4:
            # A pior condicao de Veiculo
            pior_condicao = df1.loc[:,'Vehicle_condition'].min()
            col4.metric( 'Pior condicao de veiculos', pior_condicao)
            
            
    with st.container():
        st.markdown( """___""" )
        st.title( 'Avaliacoes' )
        
        col1, col2 = st.columns( 2 )
        with col1:
            st.markdown( '##### Avaliacao medidas por Entregadores' )
            df_avg_ratings_per_deliver = df1.loc[:,['Delivery_person_ID', 'Delivery_person_Ratings']].groupby('Delivery_person_ID').mean().reset_index()
            st.dataframe( df_avg_ratings_per_deliver )
            
        with col2:
            st.markdown( '##### Avaliacao media por Transito' )
            df_avg_std_rating_by_traffic = (df1.loc[:,['Delivery_person_Ratings', 'Road_traffic_density']]
                                               .groupby('Road_traffic_density')
                                               .agg({'Delivery_person_Ratings':['mean','std']}) )  
            # MUDANCA DE NOME DAS COLUNAS
            df_avg_std_rating_by_traffic.columns = ['delivery_mean', 'delivery_std'] 
            #RESET DO INDEX
            df_avg_std_rating_by_traffic = df_avg_std_rating_by_traffic.reset_index()
            st.dataframe( df_avg_std_rating_by_traffic )
            
            st.markdown( '##### Avaliacao media por Clima' )
            df_avg_std_rating_by_weather = (df1.loc[:,['Delivery_person_Ratings', 'Weatherconditions']]
                                               .groupby('Weatherconditions')
                                               .agg({'Delivery_person_Ratings':['mean','std']}) ) 
            # MUDANCA DE NOME DAS COLUNAS
            df_avg_std_rating_by_weather.columns = ['delivery_mean', 'delivery_std'] 
            #RESET DO INDEX
            df_avg_std_rating_by_weather = df_avg_std_rating_by_weather.reset_index()
            st.dataframe( df_avg_std_rating_by_weather )

            
        with st.container():
            st.markdown( """___""" )
            st.title( 'Velocidade de Entrega' )
            
            col1, col2 = st.columns ( 2 )
            
            with col1:
                st.markdown( '##### Top Entregadores mais Rapidos' )
                df3 = top_delivers( df1, top_asc=True )
                st.dataframe( df3 )

            with col2:
                st.markdown( '##### Top Entregadores mais Lentos' )
                df3 = top_delivers( df1, top_asc=False )
                st.dataframe( df3 )
                
                

                    
                    
                    
                    
                
                
                
                
                
                
                
                
                
                
                
                

                
        
        
            

