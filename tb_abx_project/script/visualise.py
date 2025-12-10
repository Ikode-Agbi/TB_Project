import pandas as pd
import matplotlib.pyplot as plt
import os


def read_cvs(file_path):
    
   df = pd.read_csv(file_path)
   return df
   

def continent_graph(df):
   # continents tb average
   yearly_avg = df.groupby(['year', 'continent'])['tb_incidence'].mean().reset_index()
   
   yearly_avg['tb_incidence'] = yearly_avg['tb_incidence'].astype(int)

   fig, ax = plt.subplots()
   continents = yearly_avg['continent'].unique()

   for continent in continents:
      continent_data = yearly_avg[yearly_avg['continent']== continent]

      ax.plot(continent_data['year'], continent_data['tb_incidence'], label = continent)

   ax.set_xlabel('Year')
   ax.set_ylabel('TB Incidence')
   ax.legend()
   return fig


def top_highest(df):
# countries and their tb values 
   countries = df.groupby(['Country'])['tb_incidence'].mean().reset_index()


   # top 10 high tb incidence countries
   top_10_highest = countries.sort_values(by='tb_incidence', ascending=False).head(10)

   # plotting top 10 highest bar chart
   
   fig, ax = plt.subplots()

   ax.bar(top_10_highest['Country'], top_10_highest['tb_incidence'])
   ax.set_xlabel('Country')
   ax.set_ylabel('Average TB Incidence')
   plt.xticks(rotation=90)
   return fig

def top_lowest(df):
   
   countries = df.groupby(['Country'])['tb_incidence'].mean().reset_index()
# top 10 lowest tb incidence countries
   top_10_lowest = countries.sort_values(by='tb_incidence', ascending=True).head(10)

   # plotting top 10 lowest bar chart

   fig, ax = plt.subplots()
   ax.bar(top_10_lowest['Country'], top_10_lowest['tb_incidence'])
   ax.set_xlabel('Country')
   ax.set_ylabel('Average TB incidence')
   plt.xticks(rotation=90)
   return fig


file_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'tb_data_clean_updated.csv')

read_file = read_cvs(file_path)
plot_continent = continent_graph(read_file)
plot_top_highest = top_highest(read_file)
plot_top_lowest = top_lowest(read_file)

plt.show()

