import mysql.connector
import streamlit as st
import pandas as pd
import plotly.express as px
import geopandas as gpd
import matplotlib.pyplot as plt
import plotly.subplots as sp
import plotly.graph_objects as go
import json

# Establish connection to MySQL database
connection = mysql.connector.connect(
    host="127.0.0.1",
    user="root",
    password="rakshita",
    database="phonepe_pulse"
)

cursor = connection.cursor()

# Retrieve table data from MySQL
query_agg_trans = "SELECT * FROM agg_trans"
cursor.execute(query_agg_trans)
agg_trans = cursor.fetchall()

query_agg_user = "SELECT * FROM agg_user"
cursor.execute(query_agg_user)
agg_user = cursor.fetchall()

query_map_trans = "SELECT * FROM map_trans"
cursor.execute(query_map_trans)
map_trans = cursor.fetchall()

query_map_user = "SELECT * FROM map_user"
cursor.execute(query_map_user)
map_user = cursor.fetchall()

query_top_trans_dist = "SELECT * FROM top_trans_dist"
cursor.execute(query_top_trans_dist)
top_trans_dist = cursor.fetchall()

query_top_trans_pin = "SELECT * FROM top_trans_pin"
cursor.execute(query_top_trans_pin)
top_trans_pin = cursor.fetchall()

query_top_user_dist = "SELECT * FROM top_user_dist"
cursor.execute(query_top_user_dist)
top_user_dist = cursor.fetchall()

query_top_user_pin = "SELECT * FROM top_user_pin"
cursor.execute(query_top_user_pin)
top_user_pin = cursor.fetchall()

st.set_page_config(layout='wide')

# Title columns
t1, c1, c2, c3 = st.columns([8, 1, 1, 2])
with t1:
    title_html = '''
        <h1 style="text-align: center; color: green;">
            <a style="color: Purple;">
                PhonePe Pulse Analysis
            </a>
        </h1>
    '''

    st.markdown(title_html, unsafe_allow_html=True)

with c1:
    y = ['2018', '2019', '2020', '2021', '2022']
    default_y = y.index("2022")
    year = st.selectbox('', y, key='Year', index=default_y)
with c2:
    q = ['Q1', 'Q2', 'Q3', 'Q4']
    default_qua = q.index("Q1")
    qua = st.selectbox('', q, key='Quarter', index=default_qua)
    if qua == 'Q1':
        quarter = 1
    elif qua == 'Q2':
        quarter = 2
    elif qua == 'Q3':
        quarter = 3
    elif qua == 'Q4':
        quarter = 4
with c3:
    options = ["Transaction count", "Transaction amount","Registered Users", "App Opens"]
    default_index = options.index("Transaction count")
    u_t = st.selectbox("", options, key='u_t', index=default_index)

### users map data get processed from here
def formated(number):
    number_str = str(number)
    length = len(number_str)
    formatted_number = ""
    comma_counter = 0
    for i in range(length - 1, -1, -1):
        formatted_number = number_str[i] + formatted_number
        comma_counter += 1
        if comma_counter == 2 and i != 0:
            formatted_number = "," + formatted_number
            comma_counter = 0
        elif comma_counter == 3 and i != 0:
            formatted_number = "," + formatted_number
            comma_counter = 0
    return formatted_number


file_path = "C:\\Users\\User\\Downloads\\states_india(1).geojson"
with open(file_path, 'r') as file:
    india_states = json.load(file)

# processing the geojson file to refer in plotting(do not remove this section plot will not visible)
state_id_map = {}
for feature in india_states["features"]:
    feature["id"] = feature["properties"]["state_code"]
    state_id_map[feature["properties"]["st_nm"]] = feature["id"]

# preprocessed geojson file for referencing the plot section ('state' & 'id')
file_path = r"C:\Users\User\Downloads\tr_map.csv"
tr_map = pd.read_csv(file_path)

# tc data
ur_df1 = pd.DataFrame(agg_trans, columns=['State', 'Year', 'Quarter', 'Transaction_type', 'Transaction_count', 'Transaction_amount'])
tc1 = ur_df1.loc[(ur_df1['Quarter'] == int(quarter)) & (ur_df1['Year'] == int(year))].sort_values(by='State')
tc1['Transaction_count'] = tc1['Transaction_count'].astype(float)
tc2 = tc1.groupby('State').agg({'Transaction_count': 'sum'}).reset_index()
tc2[['id', 'StNames']] = tr_map[['id', 'state']]
tc2['State'] = tc2['State'].apply(lambda x: str(x)).apply(lambda x: x.capitalize())
tc2['Transaction count'] = tc2['Transaction_count'].apply(lambda x: formated(round(x)) if pd.notnull(x) else '')
tc2[f'Transaction count in Q{quarter}'] = tc2['Transaction_count'].apply(lambda x: formated(round(x)) if pd.notnull(x) else '')
snd1 = tc2.copy()

## users map
fig1 = px.choropleth_mapbox(
    snd1,
    locations="id",
    geojson=india_states,
    color="Transaction_count",
    hover_name="State",
    hover_data={'Transaction count': True, 'id': False, 'Transaction_count': False},
    title=f"PhonePe Total Transaction count in Q{quarter} - {year}",
    mapbox_style="carto-positron",
    center={"lat": 24, "lon": 79},
    color_continuous_scale=px.colors.diverging.PuOr,
    color_continuous_midpoint=0,
    zoom=3.6,
    width=800,
    height=800
)
fig1.update_layout(coloraxis_colorbar=dict(title=' ', showticklabels=True), title={
    'font': {'size': 24}
}, hoverlabel_font={'size': 18})

# ta data
ta1 = ur_df1.loc[(ur_df1['Quarter'] == int(quarter)) & (ur_df1['Year'] == int(year))].sort_values(by='State')
ta1['Transaction_amount'] = ta1['Transaction_amount'].astype(float)
ta2 = ta1.groupby('State').agg({'Transaction_amount': 'sum'}).reset_index()
ta2[['id', 'StNames']] = tr_map[['id', 'state']]
ta2['State'] = ta2['State'].apply(lambda x: str(x)).apply(lambda x: x.capitalize())
ta2['Transaction amount'] = ta2['Transaction_amount'].apply(lambda x: formated(round(x)) if pd.notnull(x) else '')
ta2[f'Transaction amount in Q{quarter}'] = ta2['Transaction_amount'].apply(lambda x: formated(round(x)) if pd.notnull(x) else '')
snd2 = ta2.copy()

## users map
fig2 = px.choropleth_mapbox(
    snd2,
    locations="id",
    geojson=india_states,
    color="Transaction_amount",
    hover_name="State",
    hover_data={'Transaction amount': True, 'id': False, 'Transaction_amount': False},
    title=f"PhonePe Total Transaction amount in Q{quarter} - {year}",
    mapbox_style="carto-positron",
    center={"lat": 24, "lon": 79},
    color_continuous_scale=px.colors.diverging.PuOr,
    color_continuous_midpoint=0,
    zoom=3.6,
    width=800,
    height=800
)
fig2.update_layout(coloraxis_colorbar=dict(title=' ', showticklabels=True), title={
    'font': {'size': 24}
}, hoverlabel_font={'size': 18})

#  data
ur_df3 = pd.DataFrame(map_user, columns=['State', 'Year', 'Quarter', 'District', 'Registered_users', 'App_opens'])
ru1 = ur_df3.loc[(ur_df3['Quarter'] == int(quarter)) & (ur_df3['Year'] == int(year))].sort_values(by='State')
ru1['Registered_users'] = ru1['Registered_users'].astype(float)
ru2 = ru1.groupby('State').agg({'Registered_users': 'sum'}).reset_index()
ru2[['id', 'StNames']] = tr_map[['id', 'state']]
ru2['State'] = ru2['State'].apply(lambda x: str(x)).apply(lambda x: x.capitalize())
ru2['Registered users'] = ru2['Registered_users'].apply(lambda x: formated(round(x)) if pd.notnull(x) else '')
ru2[f'Registered users in Q{quarter}'] = ru2['Registered_users'].apply(lambda x: formated(round(x)) if pd.notnull(x) else '')
snd3 = ru2.copy()

## users map
fig3 = px.choropleth_mapbox(
    snd3,
    locations="id",
    geojson=india_states,
    color="Registered_users",
    hover_name="State",
    hover_data={'Registered users': True, 'id': False, 'Registered_users': False},
    title=f"PhonePe Total Registered users in Q{quarter} - {year}",
    mapbox_style="carto-positron",
    center={"lat": 24, "lon": 79},
    color_continuous_scale=px.colors.diverging.PuOr,
    color_continuous_midpoint=0,
    zoom=3.6,
    width=800,
    height=800
)
fig3.update_layout(coloraxis_colorbar=dict(title=' ', showticklabels=True), title={
    'font': {'size': 24}
}, hoverlabel_font={'size': 18})

# ta data
ao1 = ur_df3.loc[(ur_df3['Quarter'] == int(quarter)) & (ur_df3['Year'] == int(year))].sort_values(by='State')
ao1['App_opens'] = ao1['App_opens'].astype(float)
ao2 = ao1.groupby('State').agg({'App_opens': 'sum'}).reset_index()
ao2[['id', 'StNames']] = tr_map[['id', 'state']]
ao2['State'] = ao2['State'].apply(lambda x: str(x)).apply(lambda x: x.capitalize())
ao2['Total no. of times App was opened'] = ao2['App_opens'].apply(lambda x: formated(round(x)) if pd.notnull(x) else '')
ao2[f'Total no. of times App was opened in Q{quarter}'] = ao2['App_opens'].apply(lambda x: formated(round(x)) if pd.notnull(x) else '')
snd4 = ao2.copy()

## users map
fig4 = px.choropleth_mapbox(
    snd4,
    locations="id",
    geojson=india_states,
    color="App_opens",
    hover_name="State",
    hover_data={'Total no. of times App was opened': True, 'id': False, 'App_opens': False},
    title=f"PhonePe Total no. of times App was opened in Q{quarter} - {year}",
    mapbox_style="carto-positron",
    center={"lat": 24, "lon": 79},
    color_continuous_scale=px.colors.diverging.PuOr,
    color_continuous_midpoint=0,
    zoom=3.6,
    width=800,
    height=800
)
fig4.update_layout(coloraxis_colorbar=dict(title=' ', showticklabels=True), title={'font': {'size': 24}}, hoverlabel_font={'size': 18})

ur = pd.DataFrame(map_user, columns=['State', 'Year', 'Quarter', 'District', 'Registered_users', 'App_opens'])
ur['App_opens'] = ur['App_opens'].astype(float)
filter_ur = ur.loc[(ur['Year'] == int(year)) & (ur['Quarter'] == int(quarter))]
gr_ur = filter_ur.groupby('Year').sum()
Registered_users = gr_ur['Registered_users'].to_list()[0]  # ****Registered users****
App_opens = int(gr_ur['App_opens'].to_list()[0])  # ****App opens****

### Transaction values
tr = pd.DataFrame(top_trans_dist, columns=['State', 'Year', 'Quarter', 'District', 'Transaction_count', 'Transaction_amount'])
filter_tr = tr.loc[(tr['Year'] == int(year)) & (tr['Quarter'] == int(quarter))]
gr_tr = filter_tr.groupby('Year').sum()
All_transactions = gr_tr['Transaction_count'].to_list()[0]
Total_payments = gr_tr['Transaction_amount']
Total_payments1 = gr_tr['Transaction_amount'].to_list()[0]
reversed_numbers = [segment[:] for segment in str(All_transactions).split(",")]
reversed_number = ",".join(reversed_numbers)

def format_number(number):
    return "{:,}".format(number)

atl = format_number(All_transactions)
# atl = "{:,}".format(All_transactions)
Avg_Transaction = round(Total_payments1 / All_transactions)  # *** Averege transaction value
av_form = '₹{:,}'.format(Avg_Transaction)
# Set the locale to Indian English
sf1 = Total_payments.apply(lambda x: "₹" + "{:,.0f}".format(x / 10000000) + "Cr")

trvalue1 = sf1.to_list()[0]  # ***Total payments

# payments method groupby
at = pd.DataFrame(agg_user, columns=['State', 'Year', 'Quarter', 'Brand', 'Transaction_count', 'Percentage'])
atr = at.loc[(at['Year'] == int(year)) & (at['Quarter'] == int(quarter))]
atr1 = atr.groupby(['Year', 'Brand']).sum()
df1a = atr1.reset_index().sort_values(by='Transaction_count', ascending=False).reset_index(drop=True).drop(
    ['Year', 'Quarter', 'Percentage'], axis=1)

df1a = df1a.drop(3).append(df1a.loc[3]).reset_index().drop('index', axis=1)
df1a['Transaction_count'] = df1a['Transaction_count'].apply(lambda x: format_number(x))  # this will be dataframe that inserted into
df1a = df1a.reset_index(drop=True)
df1a.index += 1

s1, s2 = st.columns([8, 4])

with s1:
    # Transaction count map
    if u_t == "Transaction count":
        st.plotly_chart(fig1, config=dict({'displayModeBar': False}, **{'displaylogo': False}),
                        use_container_width=False)

    # Transaction amount map
    elif u_t == "Transaction amount":
        st.plotly_chart(fig2, config=dict({'displayModeBar': False}, **{'displaylogo': False}),
                        use_container_width=False)

    elif u_t == "Registered Users":
        st.plotly_chart(fig3, config=dict({'displayModeBar': False}, **{'displaylogo': False}),
                        use_container_width=False)

    else:
        st.plotly_chart(fig4, config=dict({'displayModeBar': False}, **{'displaylogo': False}),
                        use_container_width=False)

with s2:
    st.subheader("DETAILS")
    st.markdown('<hr>', unsafe_allow_html=True)
    st.subheader('Categories')
    if u_t == "Registered Users" or u_t == "App Opens":
        fc1, fc2 = st.columns([1.3, 0.45])
        with fc1:
            mrch = df1a['Brand'][1]
            st.write(f'#### :green[{mrch}]')
            st.write('')
            peer = df1a['Brand'][2]
            st.write(f'#### :green[{peer}]')
            st.write('')
            rech = df1a['Brand'][3]
            st.write(f'#### :green[{rech}]')
            st.write('')
            fin = df1a['Brand'][4]
            st.write(f'#### :green[{fin}]')
            st.write('')
            oth = df1a['Brand'][5]
            st.write(f'#### :green[{oth}]')
        with fc2:
            val1 = df1a['Transaction_count'][1]
            st.write(f'#### {val1}')
            st.write('')
            val2 = df1a['Transaction_count'][2]
            st.write(f'#### {val2}')
            st.write('')
            val3 = df1a['Transaction_count'][3]
            st.write(f'#### {val3}')
            st.write('')

            val4 = df1a['Transaction_count'][4]
            st.write(f'#### {val4}')
            st.write('')

            val5 = df1a['Transaction_count'][5]
            st.write(f'#### {val5}')
    else:
        st.subheader(f":green[Registered Users Till {qua} {year}] ")
        st.write(f'#### {Registered_users}')  ## values
        st.write('')
        st.subheader(f':green[ App Opens in {qua} {year}]')
        st.write(f'#### {App_opens}')  ## values
        st.markdown('<hr>', unsafe_allow_html=True)
        st.write(f'## {u_t}')
        st.write('#### :green[All Transactions (UPI+Cards+Wallets)]')
        st.write(f'#### {atl}')  ## values
        st.write('')
        rc1, rc2 = st.columns([1, 1])
        with rc1:
            st.write('##### :green[Total payment value]')
            st.write(f'#### {trvalue1}')  ## values
        with rc2:
            st.write('##### :green[Avg.transaction value]')
            st.write(f'#### {av_form}')  ## values
        st.markdown('<hr>', unsafe_allow_html=True)

#--------------------------------------------------------------------------------------------------------------------------------------------------------------

bsb1, bsb2, bsb3, bsb4, bsb5, bsb6 = st.columns([2, 1, 1, 1, 2, 2])
with bsb1:
    stname = [
        'Arunachal-Pradesh', 'Assam', 'Chandigarh', 'Karnataka', 'Manipur', 'Meghalaya',
        'Mizoram', 'Nagaland', 'Punjab', 'Rajasthan', 'Sikkim', 'Tripura', 'Uttarakhand',
        'Telangana', 'Bihar', 'Kerala', 'Madhya-Pradesh', 'Andaman-&-Nicobar-Islands', 'Gujarat',
        'Lakshadweep', 'Odisha', 'Dadra-&-Nagar-Haveli-&-Daman-&-Diu', 'Ladakh',
        'Jammu-&-Kashmir', 'Chhattisgarh', 'Delhi', 'Goa', 'Haryana', 'Himachal-Pradesh',
        'Jharkhand', 'Tamil-Nadu', 'Uttar-Pradesh', 'West-Bengal', 'Andhra-Pradesh',
        'Puducherry', 'Maharashtra'
    ]
    defk = stname.index("Telangana")
    stnr = st.selectbox('', stname, key='stname', index=defk)
with bsb2:
    chgh = ['bar', 'line', 'area']
    chfk = chgh.index('line')
    fnch = st.selectbox('', chgh, key='ploti', index=chfk)
with bsb3:
    y1 = ['2018', '2019', '2020', '2021', '2022']
    default_y1 = y.index("2022")
    year1 = st.selectbox('',
                         y1, key='year1', index=default_y1)

with bsb4:
    q1 = ['Q1', 'Q2', 'Q3', 'Q4']
    default_qua1 = q.index("Q1")
    qua1 = st.selectbox('',
                        q1, key='quarter1', index=default_qua)
    if qua1 == 'Q1':
        quarter1 = 1
    elif qua1 == 'Q2':
        quarter1 = 2
    elif qua1 == 'Q3':
        quarter1 = 3
    elif qua1 == 'Q4':
        quarter1 = 4

with bsb5:
    ust1a = ["Users", "Transactions"]
    default_index1 = ust1a.index("Transactions")
    u_t1 = st.selectbox("", ust1a, key='u_t1', index=default_index1)

with bsb6:
    if u_t1 == "Transactions":
        usty1 = ["Transaction_amount", "Transaction_count"]
        default_index2 = usty1.index("Transaction_amount")
        u_t2 = st.selectbox("", usty1, key='u_t2', index=default_index2)
    else:
        usty1a = ["No of Users", "No of App Opens", ]
        default_index2a = usty1a.index("No of Users")
        u_t2a = st.selectbox("", usty1a, key='u_t2', index=default_index2a)

### shape of the invidual districts
file_path = r"C:\\Users\\User\\Downloads\\test.geojson"

india_dist1 = gpd.read_file(file_path)
jk = india_dist1.loc[india_dist1['ST_NM'] == str(stnr), 'geometry']
# Plot the selected area using Geopandas' plot function
stfig, ax = plt.subplots(figsize=(90 / 10, 70 / 10))
jk.plot(ax=ax, facecolor='green', edgecolor='blue')
ax.axis('off')  # Remove the axis ticks and labels
## data for line and other grahs

cha_df = pd.DataFrame(map_user, columns = ['State', 'Year', 'Quarter', 'District', 'Registered_users', 'App_opens'])
cha_df['State'] = cha_df['State'].apply(lambda x: x.title())
ch = cha_df.loc[
    (cha_df['Year'] == int(year1)) & (cha_df['Quarter'] == int(quarter1)) & (cha_df['State'] == str(stnr))]
ch['District'] = ch['District'].apply(lambda x: x.title())
lnk = ch[['District', 'Registered_users']]  ## userscounts
lnka = ch[['District', 'App_opens']]  ## Appopenings


### transaction chart data
transch_df = pd.DataFrame(top_trans_dist, columns = ['State', 'Year', 'Quarter', 'District', 'Transaction_count', 'Transaction_amount'])
transch_df['State'] = transch_df['State'].apply(lambda x: x.title())
ch1 = transch_df.loc[(transch_df['Year'] == int(year1)) & (transch_df['Quarter'] == int(quarter1)) & (
            transch_df['State'] == str(stnr))]
ch1['District'] = ch1['District'].apply(lambda x: x.title())
lnk1 = ch1[['District', 'Transaction_amount']]  ## total transaction amount
lnk2 = ch1[['District', 'Transaction_count']]  ## total transaction count

# if-else statement for choosing a type of graph
c1, c2 = st.columns([3, 6])
if u_t1 == "Users":
    with c1:
        # Display the plot in Streamlit
        st.write(f'### {str(stnr)}')
        st.pyplot(stfig)
    with c2:
        if u_t2a == "NoOfUsers":
            if fnch == 'line':
                st.write(str(stnr))
                figch = px.line(lnk, x='District', y='Registered_users', width=850, height=525)
                st.plotly_chart(figch, config=dict({'displayModeBar': False}, **{'displaylogo': False}),
                                use_container_width=False, layout=dict({'width': '100%'}, **{'height': '100%'}))
            elif fnch == 'bar':
                figch = px.bar(lnk, x='District', y='Registered_users', width=850, height=525)
                st.plotly_chart(figch, config=dict({'displayModeBar': False}, **{'displaylogo': False}),
                                use_container_width=False, layout=dict({'width': '100%'}, **{'height': '100%'}))
            elif fnch == 'area':
                figch = px.area(lnk, x='District', y='Registered_users', width=850, height=525)
                st.plotly_chart(figch, config=dict({'displayModeBar': False}, **{'displaylogo': False}),
                                use_container_width=False, layout=dict({'width': '100%'}, **{'height': '100%'}))
        else:
            if fnch == 'line':
                st.write(str(stnr))
                figch = px.line(lnka, x='District', y='App_opens', width=850, height=525)
                st.plotly_chart(figch, config=dict({'displayModeBar': False}, **{'displaylogo': False}),
                                use_container_width=False, layout=dict({'width': '100%'}, **{'height': '100%'}))
            elif fnch == 'bar':
                figch = px.bar(lnka, x='District', y='App_opens', width=850, height=525)
                st.plotly_chart(figch, config=dict({'displayModeBar': False}, **{'displaylogo': False}),
                                use_container_width=False, layout=dict({'width': '100%'}, **{'height': '100%'}))
            elif fnch == 'area':
                figch = px.area(lnka, x='District', y='App_opens', width=850, height=525)
                st.plotly_chart(figch, config=dict({'displayModeBar': False}, **{'displaylogo': False}),
                                use_container_width=False, layout=dict({'width': '100%'}, **{'height': '100%'}))


else:
    with c1:
        # Display the plot in Streamlit
        st.write(f'### {str(stnr)}')
        st.pyplot(stfig)
    with c2:
        if u_t2 == "TransactionAmount":
            if fnch == 'line':
                figch = px.line(lnk1, x='District', y='Transaction_amount', width=850, height=525)
                st.plotly_chart(figch, config=dict({'displayModeBar': False}, **{'displaylogo': False}),
                                use_container_width=False, layout=dict({'width': '100%'}, **{'height': '100%'}))
            elif fnch == 'bar':
                figch = px.bar(lnk1, x='District', y='Transaction_amount', width=850, height=525)
                st.plotly_chart(figch, config=dict({'displayModeBar': False}, **{'displaylogo': False}),
                                use_container_width=False, layout=dict({'width': '100%'}, **{'height': '100%'}))
            elif fnch == 'area':
                figch = px.area(lnk1, x='District', y='Transaction_amount', width=850, height=525)
                st.plotly_chart(figch, config=dict({'displayModeBar': False}, **{'displaylogo': False}),
                                use_container_width=False, layout=dict({'width': '100%'}, **{'height': '100%'}))
        else:
            if fnch == 'line':
                st.write(str(stnr))
                figch = px.line(lnk2, x='District', y='Transaction_count', width=850, height=525)
                st.plotly_chart(figch, config=dict({'displayModeBar': False}, **{'displaylogo': False}),
                                use_container_width=False, layout=dict({'width': '100%'}, **{'height': '100%'}))
            elif fnch == 'bar':
                figch = px.bar(lnk2, x='District', y='Transaction_count', width=850, height=525)
                st.plotly_chart(figch, config=dict({'displayModeBar': False}, **{'displaylogo': False}),
                                use_container_width=False, layout=dict({'width': '100%'}, **{'height': '100%'}))
            elif fnch == 'area':
                figch = px.area(lnk2, x='District', y='Transaction_count', width=850, height=525)
                st.plotly_chart(figch, config=dict({'displayModeBar': False}, **{'displaylogo': False}),
                                use_container_width=False, layout=dict({'width': '100%'}, **{'height': '100%'}))

## Top 10 values
a = pd.DataFrame(top_user_dist, columns=['State', 'Year', 'Quarter', 'District', 'Registered_users'])

def crores(number):
    return '{:.2f}Cr'.format(number / 10000000)

# Top 10 district
filter_ds = a.loc[(a['Year'] == int(year)) & (a['Quarter'] == int(quarter))]
pin_d = filter_ds.groupby(['Year', 'District']).sum().reset_index()
top_10_dist = pin_d.nlargest(10, 'Registered_users')[['District', 'Registered_users']]
df_d = top_10_dist.copy()
df_d['District'] = df_d['District'].apply(lambda x: x.title())
df_d['Registered_users'] = df_d['Registered_users'].apply(lambda x: crores(x))  # top 10 districts
df_d = df_d.reset_index(drop=True)
df_d.index += 1

# Top 10 states
filter_st = a.loc[(a['Year'] == int(year)) & (a['Quarter'] == int(quarter))]
pin_s = filter_st.groupby(['Year', 'State']).sum().reset_index()
top_10_sts = pin_s.nlargest(10, 'Registered_users')[['State', 'Registered_users']]
df_s = top_10_sts.copy()
df_s['State'] = df_s['State'].apply(lambda x: x.title())
df_s['Registered_users'] = df_s['Registered_users'].apply(lambda x: crores(x))  # top 10 states
df_s = df_s.reset_index(drop=True)
df_s.index += 1

# Top 10 Pincodes
pr = pd.DataFrame(top_user_pin, columns=['State', 'Year', 'Quarter', 'Pincode', 'Registered_users'])
filter_pr = pr.loc[(pr['Year'] == int(year)) & (pr['Quarter'] == int(quarter))]
pin = filter_pr.groupby(['Year', 'Pincode']).sum().reset_index()
top_10_pins = pin.nlargest(10, 'Registered_users')[['Pincode', 'Registered_users']]

def lakh(number):
    return '{:.2f}L'.format(number / 100000)


df_p = pd.DataFrame(top_user_pin, columns=['State', 'Year', 'Quarter', 'Pincode', 'Registered_users'])
df_p['Registered_users'] = df_p['Registered_users'].apply(lambda x: lakh(x))
df_p = df_p.reset_index(drop=True)
df_p.index += 1

# payments method groupby
at = pd.DataFrame(agg_user, columns=['State', 'Year', 'Quarter', 'Brand', 'Transaction_count', 'Percentage'])
atr = at.loc[(at['Year'] == int(year)) & (at['Quarter'] == int(quarter))]
atr1 = atr.groupby(['Year', 'Brand']).sum()
df1a = atr1.reset_index().sort_values(by='Transaction_count', ascending=False).reset_index(drop=True).drop(
    ['Year', 'Quarter', 'Percentage'], axis=1)

df1a = df1a.drop(3).append(df1a.loc[3]).reset_index().drop('index', axis=1)
df1a['Transaction_count'] = df1a['Transaction_count'].apply(lambda x: format_number(x))  # this will be dataframe that inserted into
df1a = df1a.reset_index(drop=True)
df1a.index += 1

#4th layer
thc1, thc2, thc3, thc4 = st.columns([0.1, 6, 6, 0.1])
with thc2:
    pth1a = ["Transaction_amount", "Transaction_count", "App_opens", "Registered_users"]
    pieind = pth1a.index("Transaction_amount")
    piea1 = st.selectbox("", pth1a, key='pit', index=pieind)
with thc3:
    pth1b = ["Transaction_amount", "Transaction_count", "App_opens", "Registered_users"]
    pieind1 = pth1b.index("Registered_users")
    piea2 = st.selectbox("", pth1b, key='pit1', index=pieind1)

### Pie chart for Uerscount and total transaction count

df = pd.DataFrame(map_user, columns = ['State', 'Year', 'Quarter', 'District', 'Registered_users', 'App_opens'])
df1 = pd.DataFrame(map_trans, columns=['State', 'Year', 'Quarter', 'District', 'Transaction_count', 'Transaction_amount'])
mer_df = df.merge(df1, on=['District', 'State', 'Year', 'Quarter'], how='left')
df_sorted = mer_df.sort_values('Year')

# Create subplots with 1 row and 2 columns
piefig = sp.make_subplots(rows=1, cols=2, subplot_titles=(piea1, piea2), specs=[[{'type': 'pie'}, {'type': 'pie'}]])

# Add the first pie chart for registered users
piefig.add_trace(go.Pie(labels=df_sorted['Year'], values=df_sorted[piea1], hole=0.5,
                        hovertemplate=f"Year: %{{label}}<br>{piea1}: %{{value:,.0f}}"),
                 row=1, col=1)

# Add the second pie chart for transactions
piefig.add_trace(go.Pie(labels=df_sorted['Year'], values=df_sorted[piea2], hole=0.5,
                        hovertemplate=f"Year: %{{label}}<br>{piea2}: %{{value:,.0f}}"),
                 row=1, col=2)

# Update the layout
piefig.update_layout(height=600, width=1250)

# Show the chart
st.plotly_chart(piefig, config=dict({'displayModeBar': False}, **{'displaylogo': False}), use_container_width=False,
                layout=dict({'width': '100%'}, **{'height': '100%'}))

tb10 = st.selectbox('', ('Top 10 States', 'Top 10 Districts', 'Top 10 Pincodes'), key='top10')
if tb10 == 'Top 10 Districts':
    st.dataframe(df_d, width=800)
elif tb10 == 'Top 10 States':
    st.dataframe(df_s, width=800)
else:
    st.dataframe(df_p, width=800)

# bsb1, bsb2, bsb3 = st.columns([1, 1, 2])
# with bsb1:
#     y1 = ['2018', '2019', '2020', '2021', '2022']
#     default_y1 = y.index("2022")
#     year1 = st.selectbox('',
#                          y1, key='year1', index=default_y1)
#
# with bsb2:
#     q1 = ['Q1', 'Q2', 'Q3', 'Q4']
#     default_qua1 = q.index("Q1")
#     qua1 = st.selectbox('',
#                         q1, key='quarter1', index=default_qua)
#     if qua1 == 'Q1':
#         quarter1 = 1
#     elif qua1 == 'Q2':
#         quarter1 = 2
#     elif qua1 == 'Q3':
#         quarter1 = 3
#     elif qua1 == 'Q4':
#         quarter1 = 4
#
# with bsb3:
#     ust1a = ["Transaction count", "Transaction amount","Registered Users", "App Opens"]
#     default_index1 = ust1a.index("Transaction count")
#     u_t1 = st.selectbox("", ust1a, key='u_t1', index=default_index1)
#
# file_path1 = "C:\\Users\\User\\Downloads\\dist_lat_long.geojson"
# with open(file_path1, 'r') as file1:
#     india_dst = json.load(file1)
#
# # processing the geojson file to refer in plotting(do not remove this section plot will not visible)
# dist_id_map = {}
# for featuree in india_dst["features"]:
#     featuree["District"] = featuree["properties"]["District"]
#     dist_id_map[featuree["properties"]["State"]] = featuree["District"]
#
# # Transaction_count data
# ur_df2 = pd.DataFrame(top_trans_dist, columns=['State', 'Year', 'Quarter', 'District', 'Transaction_count', 'Transaction_amount', 'Latitude', 'Longitude', 'Region'])
# dc2 = ur_df2.loc[(ur_df2['Quarter'] == int(quarter1)) & (ur_df2['Year'] == int(year1))].sort_values(by='State')
# dc2['Transaction_count'] = dc2['Transaction_count'].astype(float)
# dc3 = dc2.groupby('District').agg({'Transaction_count': 'sum'}).reset_index()
# dc3['DstNames'] = dc3['District'].map(india_dst)
# # state_mapping = {feature['properties']['District']: feature['properties']['State'] for feature in india_dst['features']}
# # ur_df2['State'] = ur_df2['State'].map(state_mapping)
# dc3['District'] = dc3['District'].apply(lambda x: str(x)).apply(lambda x: x.capitalize())
# dc3['Transaction count'] = dc3['Transaction_count'].apply(lambda x: formated(round(x)) if pd.notnull(x) else '')
# dc3[f'Transaction count in Q{quarter1}'] = dc3['Transaction_count'].apply(lambda x: formated(round(x)) if pd.notnull(x) else '')
# snd5 = dc3.copy()
#
# ## users map
# fig5 = px.choropleth_mapbox(
#     snd5,
#     locations="DstNames",
#     geojson=india_dst,
#     color="Transaction_count",
#     hover_name="District",
#     hover_data={'Transaction count': True, 'DstNames': False, 'Transaction_count': False},
#     title=f"PhonePe Total Transaction count in Q{quarter1} - {year1}",
#     mapbox_style="carto-positron",
#     center={"lat": 24, "lon": 79},
#     color_continuous_scale=px.colors.diverging.PuOr,
#     color_continuous_midpoint=0,
#     zoom=3.6,
#     width=800,
#     height=800
# )
# fig5.update_layout(coloraxis_colorbar=dict(title=' ', showticklabels=True), title={
#     'font': {'size': 24}
# }, hoverlabel_font={'size': 18})
#
# # ta data
# ur_df2 = pd.DataFrame(top_trans_dist, columns=['State', 'Year', 'Quarter', 'District', 'Transaction_count', 'Transaction_amount', 'Latitude', 'Longitude', 'Region'])
# da2 = ur_df2.loc[(ur_df2['Quarter'] == int(quarter1)) & (ur_df2['Year'] == int(year1))].sort_values(by='State')
# da2['Transaction_amount'] = da2['Transaction_amount'].astype(float)
# da3 = da2.groupby('District').agg({'Transaction_amount': 'sum'}).reset_index()
# da3['DstNames'] = da3['District'].map(india_dst)
# da3['District'] = da3['District'].apply(lambda x: str(x)).apply(lambda x: x.capitalize())
# da3['Transaction amount'] = da3['Transaction_amount'].apply(lambda x: formated(round(x)) if pd.notnull(x) else '')
# da3[f'Transaction amount in Q{quarter1}'] = da3['Transaction_amount'].apply(lambda x: formated(round(x)) if pd.notnull(x) else '')
# snd6 = da3.copy()
#
# ## users map
# fig6 = px.choropleth_mapbox(
#     snd6,
#     locations="DstNames",
#     geojson=india_dst,
#     color="Transaction_amount",
#     hover_name="District",
#     hover_data={'Transaction amount': True, 'DstNames': False, 'Transaction_amount': False},
#     title=f"PhonePe Total Transaction amount in Q{quarter1} - {year1}",
#     mapbox_style="carto-positron",
#     center={"lat": 24, "lon": 79},
#     color_continuous_scale=px.colors.diverging.PuOr,
#     color_continuous_midpoint=0,
#     zoom=3.6,
#     width=800,
#     height=800
# )
# fig6.update_layout(coloraxis_colorbar=dict(title=' ', showticklabels=True), title={
#     'font': {'size': 24}
# }, hoverlabel_font={'size': 18})
#
# # Registered data
# ur_df4 = pd.DataFrame(map_user, columns=['State', 'Year', 'Quarter', 'District', 'Registered_users', 'App_opens', 'Latitude', 'Longitude', 'Region'])
# du2 = ur_df4.loc[(ur_df4['Quarter'] == int(quarter1)) & (ur_df4['Year'] == int(year1))].sort_values(by='State')
# du2['Registered_users'] = du2['Registered_users'].astype(float)
# du3 = du2.groupby('District').agg({'Registered_users': 'sum'}).reset_index()
# du3['DstNames'] = du3['District'].map(india_dst)
# du3['District'] = du3['District'].apply(lambda x: str(x)).apply(lambda x: x.capitalize())
# du3['Registered users'] = du3['Registered_users'].apply(lambda x: formated(round(x)) if pd.notnull(x) else '')
# du3[f'Registered users in Q{quarter1}'] = du3['Registered_users'].apply(lambda x: formated(round(x)) if pd.notnull(x) else '')
# snd7 = du3.copy()
#
# ## users map
# fig7 = px.choropleth_mapbox(
#     snd7,
#     locations="DstNames",
#     geojson=india_dst,
#     color="Registered_users",
#     hover_name="District",
#     hover_data={'Registered users': True, 'DstNames': False, 'Registered_users': False},
#     title=f"PhonePe Total Registered users in Q{quarter1} - {year1}",
#     mapbox_style="carto-positron",
#     center={"lat": 24, "lon": 79},
#     color_continuous_scale=px.colors.diverging.PuOr,
#     color_continuous_midpoint=0,
#     zoom=3.6,
#     width=800,
#     height=800
# )
# fig7.update_layout(coloraxis_colorbar=dict(title=' ', showticklabels=True), title={
#     'font': {'size': 24}
# }, hoverlabel_font={'size': 18})
#
# # ta data
# ur_df4 = pd.DataFrame(map_user, columns=['State', 'Year', 'Quarter', 'District', 'Registered_users', 'App_opens', 'Latitude', 'Longitude', 'Region'])
# ao4 = ur_df4.loc[(ur_df4['Quarter'] == int(quarter1)) & (ur_df4['Year'] == int(year1))].sort_values(by='State')
# ao4['App_opens'] = ao4['App_opens'].astype(float)
# ao5 = ao4.groupby('District').agg({'App_opens': 'sum'}).reset_index()
# ao5['DstNames'] = ao5['District'].map(india_dst)
# ao5['District'] = ao5['District'].apply(lambda x: str(x)).apply(lambda x: x.capitalize())
# ao5['App Opens'] = ao5['App_opens'].apply(lambda x: formated(round(x)) if pd.notnull(x) else '')
# ao5[f'App Opens in Q{quarter1}'] = ao5['App_opens'].apply(lambda x: formated(round(x)) if pd.notnull(x) else '')
# snd8 = ao5.copy()
#
# ## users map
# fig8 = px.choropleth_mapbox(
#     snd8,
#     locations="DstNames",
#     geojson=india_dst,
#     color="App_opens",
#     hover_name="District",
#     hover_data={'App Opens': True, 'DstNames': False, 'App_opens': False},
#     title=f"PhonePe Total App Opens in Q{quarter1} - {year1}",
#     mapbox_style="carto-positron",
#     center={"lat": 24, "lon": 79},
#     color_continuous_scale=px.colors.diverging.PuOr,
#     color_continuous_midpoint=0,
#     zoom=3.6,
#     width=800,
#     height=800
# )
# fig8.update_layout(coloraxis_colorbar=dict(title=' ', showticklabels=True), title={
#     'font': {'size': 24}
# }, hoverlabel_font={'size': 18})
#
# s1, s2 = st.columns([8, 4])
#
# with s1:
#     # Transaction count map
#     if u_t1 == "Transaction count":
#         st.plotly_chart(fig5, config=dict({'displayModeBar': False}, **{'displaylogo': False}),
#                         use_container_width=False)
#
#     # Transaction amount map
#     elif u_t1 == "Transaction amount":
#         st.plotly_chart(fig6, config=dict({'displayModeBar': False}, **{'displaylogo': False}),
#                         use_container_width=False)
#
#     elif u_t1 == "Registered Users":
#         st.plotly_chart(fig7, config=dict({'displayModeBar': False}, **{'displaylogo': False}),
#                         use_container_width=False)
#
#     else:
#         st.plotly_chart(fig8, config=dict({'displayModeBar': False}, **{'displaylogo': False}),
#                         use_container_width=False)
#
# with s2:
#     st.subheader("DETAILS")
#     st.markdown('<hr>', unsafe_allow_html=True)
#     st.subheader('Categories')
#     if u_t1 == "Registered Users" or u_t1 == "App Opens":
#         fc1, fc2 = st.columns([1.3, 0.45])
#         with fc1:
#             mrch = df1a['Brand'][1]
#             st.write(f'#### :green[{mrch}]')
#             st.write('')
#             peer = df1a['Brand'][2]
#             st.write(f'#### :green[{peer}]')
#             st.write('')
#             rech = df1a['Brand'][3]
#             st.write(f'#### :green[{rech}]')
#             st.write('')
#             fin = df1a['Brand'][4]
#             st.write(f'#### :green[{fin}]')
#             st.write('')
#             oth = df1a['Brand'][5]
#             st.write(f'#### :green[{oth}]')
#         with fc2:
#             val1 = df1a['Transaction_count'][1]
#             st.write(f'#### {val1}')
#             st.write('')
#             val2 = df1a['Transaction_count'][2]
#             st.write(f'#### {val2}')
#             st.write('')
#             val3 = df1a['Transaction_count'][3]
#             st.write(f'#### {val3}')
#             st.write('')
#
#             val4 = df1a['Transaction_count'][4]
#             st.write(f'#### {val4}')
#             st.write('')
#
#             val5 = df1a['Transaction_count'][5]
#             st.write(f'#### {val5}')
#     else:
#         st.subheader(f":green[Registered Users Till {qua1} {year1}] ")
#         st.write(f'#### {Registered_users}')  ## values
#         st.write('')
#         st.subheader(f':green[ App Opens in {qua1} {year1}]')
#         st.write(f'#### {App_opens}')  ## values
#         st.markdown('<hr>', unsafe_allow_html=True)
#         st.write(f'## {u_t1}')
#         st.write('#### :green[All Transactions (UPI+Cards+Wallets)]')
#         st.write(f'#### {atl}')  ## values
#         st.write('')
#         rc1, rc2 = st.columns([1, 1])
#         with rc1:
#             st.write('##### :green[Total payment value]')
#             st.write(f'#### {trvalue1}')  ## values
#         with rc2:
#             st.write('##### :green[Avg.transaction value]')
#             st.write(f'#### {av_form}')  ## values
#         st.markdown('<hr>', unsafe_allow_html=True)