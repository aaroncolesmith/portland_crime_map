import streamlit as st
import pandas as pd
import plotly_express as px
import plotly.graph_objects as go
import plotly.io as pio
pio.templates.default = "simple_white"


st.set_page_config(
    page_title='aaroncolesmith.com',
    page_icon='dog'
    )

def density_map_agg(d):

    fig = px.density_mapbox(d, 
                        lat='LATITUDE', 
                        lon='LONGITUDE', 
                        z='COUNT',
                        radius=25,
                        center=dict(lat=pd.to_numeric(d['LATITUDE'],errors='coerce').mean(), lon=pd.to_numeric(d['LONGITUDE'],errors='coerce').mean()), 
                        zoom=10,
                        opacity=.90, 
                        height=600,
                        hover_data=['ADDRESS','CRIME','LAST_DATE'],
                        mapbox_style="stamen-terrain")
    fig.update_traces(hovertemplate='<b>%{hovertext}</b><br><br>Crime Count: %{z}<br>Coordinates: (%{lat},%{lon})<br>Address: %{customdata[0]}<br>Last date: %{customdata[2]|%-m/%-d %-I:%M%p}')
    st.plotly_chart(fig)

def density_map_day(d):

    fig = px.density_mapbox(d, 
                            lat='LATITUDE', 
                            lon='LONGITUDE', 
                            hover_name='CRIME',
                            hover_data=['ADDRESS','COUNT','LAST_DATE'],
                            animation_frame=d['DAY'].astype('str'),
                            zoom=10,
                            radius=25,
                            opacity=.90, 
                            center=dict(lat=pd.to_numeric(d['LATITUDE'],errors='coerce').mean(), lon=pd.to_numeric(d['LONGITUDE'],errors='coerce').mean()),
                            height=600)
    fig.update_layout(mapbox_style="stamen-terrain")
    custom_template = '<b>%{hovertext}</b><br><br>Crime Count: %{customdata[1]}<br>Coordinates: (%{lat},%{lon})<br>Address: %{customdata[0]}<br>Last date: %{customdata[2]|%-m/%-d %-I:%M%p}'
    fig.update_traces(hovertemplate=custom_template)
    for frame in fig.frames:
        frame.data[0].hovertemplate = custom_template
    fig['layout']['sliders'][0]['currentvalue']['prefix'] = 'Date: '
    st.plotly_chart(fig)

def scatter_map_agg(d):

    #setting the size max based on the input data -- 
    if d.COUNT.max() < 10:
        size_max=20
    else:
        size_max=50

    fig = px.scatter_mapbox(d, 
                            lat='LATITUDE', 
                            lon='LONGITUDE', 
                            hover_name='CRIME',
                            hover_data=['ADDRESS','COUNT','LAST_DATE'],
                            size='COUNT_SCALED',
                            color_discrete_sequence=["fuchsia"],
                            opacity=.6,
                            size_max=size_max, 
                            center=dict(lat=pd.to_numeric(d['LATITUDE'],errors='coerce').mean(), lon=pd.to_numeric(d['LONGITUDE'],errors='coerce').mean()),
                            zoom=10, 
                            height=600)
    fig.update_layout(mapbox_style="open-street-map")
    fig.update_traces(hovertemplate='<b>%{hovertext}</b><br><br>Crime Count: %{customdata[1]}<br>Coordinates: (%{lat},%{lon})<br>Address: %{customdata[0]}<br>Last date: %{customdata[2]|%-m/%-d %-I:%M%p}')
    st.plotly_chart(fig)

def scatter_map_day(d):

    fig = px.scatter_mapbox(d, 
                            lat='LATITUDE', 
                            lon='LONGITUDE', 
                            hover_name='CRIME',
                            hover_data=['ADDRESS','COUNT','LAST_DATE'],
                            size='COUNT_SCALED',
                            animation_group='LAT_LON',
                            animation_frame=d['DAY'].astype('str'),
                            color_discrete_sequence=["fuchsia"],
                            opacity=.6,
                            center=dict(lat=pd.to_numeric(d['LATITUDE'],errors='coerce').mean(), lon=pd.to_numeric(d['LONGITUDE'],errors='coerce').mean()),
                            size_max=100, 
                            zoom=10, 
                            height=600)
    fig.update_layout(mapbox_style="stamen-terrain")
    custom_template = '<b>%{hovertext}</b><br><br>Crime Count: %{customdata[1]}<br>Coordinates: (%{lat},%{lon})<br>Address: %{customdata[0]}<br>Last date: %{customdata[2]|%-m/%-d %-I:%M%p}'
    fig.update_traces(hovertemplate=custom_template)
    for frame in fig.frames:
        frame.data[0].hovertemplate = custom_template
    fig['layout']['sliders'][0]['currentvalue']['prefix'] = 'Date: '
    st.plotly_chart(fig)

def group_data_agg(df):
    d=df.groupby(['LATITUDE','LONGITUDE','ADDRESS']).agg({'DATE_CRIME': lambda x: '<br>'.join(x),
                                            'CRIME_ID': 'size',
                                            'DATE':'max'}).reset_index()

    d.columns = ['LATITUDE','LONGITUDE','ADDRESS','CRIME','COUNT','LAST_DATE']
    d['LATITUDE'] = pd.to_numeric(d['LATITUDE'])
    d['LONGITUDE'] = pd.to_numeric(d['LONGITUDE'])
    d['COUNT_SCALED'] = d['COUNT']*1

    d['LAT_LON'] = d['LATITUDE'].astype('str') + ', ' +  d['LONGITUDE'].astype('str')

    # if the crime desciption is greater than 500 characters, cut it off at 500 characters
    d['CRIME'] = d['CRIME'].apply(lambda x: x[:1500] + '...' if len(x) > 1500 else x)

    return d

def group_data_day(df):
    d=df.groupby(['LATITUDE','LONGITUDE','ADDRESS','DAY']).agg({'DATE_CRIME': lambda x: '<br>'.join(x),
                                            'CRIME_ID': 'size',
                                            'DATE':'max'}).reset_index()
    d.columns = ['LATITUDE','LONGITUDE','ADDRESS','DAY','CRIME','COUNT','LAST_DATE']
    d['LATITUDE'] = pd.to_numeric(d['LATITUDE'])
    d['LONGITUDE'] = pd.to_numeric(d['LONGITUDE'])
    d['LAT_LON'] = d['LATITUDE'].astype('str') + ', ' +  d['LONGITUDE'].astype('str')

    # if the crime desciption is greater than 500 characters, cut it off at 500 characters
    d['CRIME'] = d['CRIME'].apply(lambda x: x[:1500] + '...' if len(x) > 1500 else x)
    d['DAY']=d['DAY'].dt.tz_localize(None).dt.to_pydatetime()
    d['COUNT_SCALED'] = d['COUNT']*1

    d=d.sort_values('DAY',ascending=True).reset_index(drop=True)

    return d

def crime_cnt_rolling_avg(df):
    df2=df.groupby('HOUR').size().to_frame('CRIME_CNT').reset_index()
    df2['ROLLING_24'] = df2['CRIME_CNT'].rolling(window=24).mean()

    fig=go.Figure()
    fig.add_trace(
        go.Scatter(x=df2.HOUR,
                y=df2.ROLLING_24,
                name='Rolling Avg',
                mode='lines',
                line_shape='spline',
                marker_color='#626EF6',
                marker=dict(
                    size=4,
                    line=dict(
                        width=1,
                        color='#1320B2'
                        )
                    )
                )
        )

    fig.add_trace(
        go.Scatter(x=df2.HOUR,
                y=df2.CRIME_CNT,
                name='Crime Count',
                mode='markers',
                marker_color='#626EF6',
                opacity=.5,
                marker=dict(
                    size=8,
                    line=dict(
                        width=1,
                        color='#1320B2'
                        )
                    )
                )
        )
    st.plotly_chart(fig)


# def twitter_data():
#     df = pd.read_csv('https://raw.githubusercontent.com/aaroncolesmith/portland_crime_map/main/data.csv')
#     df['DATE'] = pd.to_datetime(df['DATE'],utc=True)
#     # Convert date from UTC to PST
#     df['DATE'] = df['DATE'].dt.tz_convert('US/Pacific')
#     df['HOUR'] = df['DATE'].dt.floor('h')
#     df['DAY'] = df['DATE'].dt.floor('d')
#     df['DATE_CRIME'] = df['DATE'].dt.strftime('%-m/%-d %-I:%M%p').astype('str') + ' - ' + df['CRIME']

#     return df

@st.cache_data(ttl=1800)
def pdx911_data(days):
    d=pd.read_parquet('https://raw.githubusercontent.com/aaroncolesmith/portland_crime_data/main/portland_crime_data.parquet', engine='pyarrow')
    d=d.loc[d.DATE.dt.date >= pd.to_datetime('today') - pd.Timedelta(days=days)]

    url='https://www.portlandonline.com/scripts/911incidents.cfm'
    dtmp=pd.read_xml(url)
    dtmp=dtmp.loc[(dtmp.id.notnull())&(dtmp.title.notnull())].reset_index(drop=True)

    dtmp=dtmp[['summary','updated','point']]
    dtmp.columns=['TEXT','DATE','COORDS']

    dtmp[['CRIME','ADDRESS']] = dtmp['TEXT'].str.split('at',n=1, expand=True)
    dtmp[['ADDRESS','CRIME_ID']]=dtmp['ADDRESS'].str.split(' \[',n=1,expand=True)
    dtmp['ADDRESS']=dtmp['ADDRESS'].str.replace(', PORT',', PORTLAND').str.replace(', GRSM',', GRESHAM')

    dtmp['DATE'] = pd.to_datetime(dtmp['DATE'])
    dtmp['HOUR'] = dtmp['DATE'].dt.floor('h')
    dtmp['DAY'] = dtmp['DATE'].dt.floor('d')
    dtmp['DATE_CRIME'] = dtmp['DATE'].dt.strftime('%-m/%-d %-I:%M%p').astype('str') + ' - ' + dtmp['CRIME']

    dtmp[['LATITUDE','LONGITUDE']] = dtmp['COORDS'].str.split(' ',n=1, expand=True)

    d = pd.concat([d,dtmp])

    d=d.groupby(['DATE','TEXT','COORDS']).size().to_frame('cnt').reset_index().sort_values('DATE',ascending=True).reset_index(drop=True)
    del d['cnt']

    d[['CRIME','ADDRESS']] = d['TEXT'].str.split('at',n=1, expand=True)
    d[['ADDRESS','CRIME_ID']]=d['ADDRESS'].str.split(' \[',n=1,expand=True)
    d['ADDRESS']=d['ADDRESS'].str.replace(', PORT',', PORTLAND').str.replace(', GRSM',', GRESHAM')
    d['DATE']=d['DATE'].apply(lambda x: pd.to_datetime(x).tz_convert('US/Pacific'))
    d['DATE_CRIME'] = pd.to_datetime(d['DATE'], utc=False).dt.strftime('%-m/%-d %-I:%M%p').astype('str') + ' - ' + d['CRIME']   
    d[['LATITUDE','LONGITUDE']] = d['COORDS'].str.split(' ',n=1, expand=True)
    d['DATE'] = pd.to_datetime(d['DATE'])
    d['HOUR'] = d['DATE'].dt.floor('h',ambiguous=True)
    d['DAY'] = d['DATE'].dt.floor('d')
    d['DATE_CRIME'] = d['DATE'].dt.strftime('%-m/%-d %-I:%M%p').astype('str') + ' - ' + d['CRIME']

    upd_coords=pd.merge(d.groupby(['ADDRESS','COORDS']).size().to_frame('CNT').reset_index().groupby(['ADDRESS'])['CNT'].max(),
            d.groupby(['ADDRESS','COORDS']).size().to_frame('CNT').reset_index(),
            how='inner',
            left_on=['ADDRESS','CNT'],
            right_on=['ADDRESS','CNT']
    )
    upd_coords.columns = ['ADDRESS','CNT','UPDATED_COORDS']

    d=pd.merge(d,
            upd_coords.groupby('ADDRESS').first().reset_index().sort_values('CNT',ascending=False)[['ADDRESS','UPDATED_COORDS']],
            how='inner',
            left_on='ADDRESS',
            right_on='ADDRESS')

    del d['COORDS']
    d['COORDS'] = d['UPDATED_COORDS']
    del d['UPDATED_COORDS']

    del d['LATITUDE']
    del d['LONGITUDE']

    d[['LATITUDE','LONGITUDE']] = d['COORDS'].str.split(' ',n=1, expand=True)

    return d



def app():
    url='https://www.portlandonline.com/scripts/911incidents.cfm'
    dtmp=pd.read_xml(url)
    st.title('Portland Crime Dashboard')
    st.markdown('Updated as of: ' + str(pd.to_datetime(dtmp['updated']).max().strftime('%-m/%-d %-I:%M%p')))

    days = st.sidebar.slider('How many days of data to load', min_value=1, max_value=365, value=7, step=1)


    df = pdx911_data(days)

    st.markdown('This app is a Streamlit dashboard that shows the number of crimes in Portland, Oregon.')

    # st.title('Portland Crime Map')
    
    # Add a multiselect widget with all the different CRIME options
    crime_options = df['CRIME'].unique()
    selected_crime = st.sidebar.multiselect('Select Crime(s)', crime_options, crime_options)
    df = df[df['CRIME'].isin(selected_crime)]

    st.subheader('Crime Map')

    c1, c2 = st.columns(2)

    # Selector to view aggregate data or by day
    view_type = c1.selectbox('View by', ['Last N Hours','Day', 'All-Time'])

    # Selector to view density_map or scatter_map
    map_type = c2.selectbox('Map Type', ['Scatter Map', 'Density Map'])

    if view_type == 'All-Time':
        d=group_data_agg(df)
        if map_type == 'Density Map':
            density_map_agg(d)
        elif map_type == 'Scatter Map':
            scatter_map_agg(d)

    if view_type == 'Day':
        d=group_data_day(df)
        if map_type == 'Density Map':
            density_map_day(d)
        elif map_type == 'Scatter Map':
            scatter_map_day(d)

    if view_type == 'Last N Hours':
        with st.form(key='my_form'):
            num = st.slider('How far back?', min_value=2, max_value=336, value=12, step=1)
            submit_button = st.form_submit_button(label='Submit')


        # num = st.slider('How far back?', min_value=2, max_value=336, value=12, step=1)
        d=group_data_agg(df[df['DATE'] > df['DATE'].max() - pd.Timedelta(hours=num)])
        if map_type == 'Density Map':
            density_map_agg(d)
        elif map_type == 'Scatter Map':
            scatter_map_agg(d)


    # Scatter plot of crime counts by hour
    # df['HOUR']=df['DATE'].dt.floor('h')
    # fig = px.scatter(df.groupby('HOUR').size().to_frame('COUNT').reset_index(), x='HOUR', y='COUNT')
    # st.plotly_chart(fig)


    crime_cnt_rolling_avg(df)


    # Stacked bar chart over by by crime type
    fig = px.bar(df.groupby(['HOUR','CRIME']).size().to_frame('COUNT').reset_index(), x='HOUR', y='COUNT', color='CRIME')
    st.plotly_chart(fig)  


if __name__ == "__main__":
    #execute
    app()
