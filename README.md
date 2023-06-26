# PhonePe_Pulse_Analysis
## Project Requirments:
- __[Python 3.11](https://www.google.com/search?q=docs.python.org)__ 
- __[Pandas](https://www.google.com/search?q=python+pandas)__
- __[Streamlit](https://www.google.com/search?q=python+streamlit)__
- __[Plotly](https://www.google.com/search?q=python+plotly)__
- __[Matplotlib](https://www.google.com/search?q=python+matplotlib)__
- __[Geopandas](https://www.google.com/search?q=python+geopandas)__

### PhonePe Pulse Dashboard contains Four sections:

1. __Overall Geo Visualization:__
   
   * PhonePe Pulse `Geo visulization` includes four options __Transaction count, Transaction amount, Registered Users and App Opens__  for all __Quaters__ from __2018 to 2022__.
     
   * Every State in INDIA is ploted in the map using Plotly `choropleth_mapbox`. Based upon scale of values, the ratio of colour scale differs.
   
   * Here we have three `Drop Down` button on top right corner to view different options to choose from __Year, Quarter, Information__.
   
   * Under the __Transaction count, Transaction amount__ `Drop Down` contains _Total Transaction Counts, Transaction Amounts, Averge of Transactions_, _Registered       Users_ and _No of App Opens_ in _Each Quarter_ of _Every Year_.
   
   * Under the __Registered Users and App Opens__ `Drop Down` contains __Mode of Transactions__.

2. __District wise Visualization:__

   * This Section Gives Detailed Analysis of __Users__ and their __Transaction__ in Each __Indian States__ and their __Districts__.
   
   * There are Six `Drop Down` Buttons with options __State Name, Type Of Graph, Year, Quarter, Users or Transaction, Users count/Appopens or TransactionAmount/TransactionCount__.
   
   * Each State in India is displayed in `left side` of this section using __Matplotlib Subplot__ and their Disticts Visualization in `right side` using __Plotly Express__.
   
3. __Year Wise Visualization:__ 

   * This Section Gives Detailed Analysis of __Users__ and __Transaction__ over the years from __2018 to 2022__ using `plotly.graph_objects` __Pie Chart__.
   
   * There are Two `Drop Down` Buttons with options __Users Count, AppOpens, Transaction Amount and Transaction Count__.

4. __Top 10 Districts, States and Pincode:__

   *  This section has a `Drop Down` to understand the **Top 10 Districts, States, Pincode wise Sorted values**.
