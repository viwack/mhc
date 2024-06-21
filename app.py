from shiny import *
from shiny import reactive
from shinywidgets import output_widget, render_widget
#from shiny.express import render
#from ipywidgets import Label
import ipyleaflet as L
from ipywidgets import Layout
from ipyleaflet import GeoJSON, LayersControl, WidgetControl, CircleMarker, LayerGroup
import pathlib
from pathlib import Path
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib.ticker import FuncFormatter
import matplotlib.colors as mcolors
import json
import pandas as pd
import geopandas as gpd
#from geopy.geocoders import Nominatim
import numpy as np
import io
from datetime import date
import plotly.express as px

here = pathlib.Path(__file__)

# Step 1: Geocoding the address using OpenStreetMap's Nominatim
def geocode_address(address):
    geolocator = Nominatim(user_agent="your_application_name")
    location = geolocator.geocode(address)
    if location:
        return location.latitude, location.longitude
    else:
        return None, None

# Step 2: Check the legislative district [from GPT-4]
def check_legislative_district(lat, lng, districts_geojson):
    point = Point(lng, lat)
    # Load the legislative districts GeoJSON file
    districts = gpd.read_file(districts_geojson)

    # Create a spatial index
    spatial_index = districts.sindex

    # Possible matches indices using spatial index
    possible_matches_index = list(spatial_index.query(point))
    possible_matches = districts.iloc[possible_matches_index]

    # Check which district the point is in
    precise_matches = possible_matches[possible_matches.contains(point)]

    if not precise_matches.empty:
        # Assuming 'district_name' is the column name with the district names.
        return precise_matches.iloc[0]['NAME']  # Replace 'district_name' with the actual column name

    return None



# path2folder = r"./data/" # fill in the path to your folder here.
# assert len(path2folder) > 0

mhvillage_df = pd.read_csv(Path(__file__).parent / "MHVillageDec7_Legislative1.csv")
mhvillage_df['Sites'] = pd.to_numeric(mhvillage_df['Sites'], downcast='integer')
lara_df = pd.read_csv(Path(__file__).parent / "LARA_with_coord_and_legislativedistrict1.csv")
lara_df['County'] = lara_df['County'].str.title()


# Path to your legislative districts GeoJSON file
house_districts_geojson_path = r"Michigan_State_House_Districts_2021.json"
senate_districts_geojson_path = r"Michigan_State_Senate_Districts_2021.json"
#tracts_shapefile = gpd.read_file(path2folder+r"tl_2019_26_tract.shp")

circlelist_lara = []
circlelist_mh = []
#circleMHlist = []
mklist_mh = []
mklist_lara = []
upper_layers = []
lower_layers = []

labels_df =  pd.DataFrame(range(1, 51), columns=['Numbers'])



def build_district_layers(upper=0):
    if upper == 1:
        if len(upper_layers) > 0:
            return
        #tracts_shapefile = gpd.read_file(path2folder+"/cb_2022_26_sldu_500k.shp")
        color = 'green'
        geojson_path = senate_districts_geojson_path
        with open(here.parent / geojson_path, 'r') as f:
            michigan_districts_data = json.load(f)
    else:
        if len(lower_layers) > 0:
            return
        color = 'purple'
        geojson_path = house_districts_geojson_path
        with open(here.parent / geojson_path, 'r') as f:
            michigan_districts_data = json.load(f)
    layerk =  L.GeoJSON(
            data=michigan_districts_data,
            name='Michigan House Legislative Districts',
            style={
                'color': color,
                'weight': 1,
                'fillOpacity': 0.3
            },
            hover_style={
                'color': 'orange',
                'weight': 3
            }
        )
    if upper == 1:
        upper_layers.append(layerk)
    else:
        lower_layers.append(layerk)
    return


def build_marker_layer(LARA_C):
    #if len(circlelist) >0  and len(mklist)>0:
    #    return
    leng = 0
    if not LARA_C:
        if len(circlelist_mh) >0  and len(mklist_mh)>0:
            return
        for ind in range(len(mhvillage_df)):
            lon = float(mhvillage_df['longitude'].iloc[ind])
            lat = float(mhvillage_df['latitude'].iloc[ind])

    ########Handle missing entries
            if pd.isna(lara_df['House district'].iloc[ind]) or pd.isna(lara_df['Senate district'].iloc[ind]):
                house_lara = "missing"
                senate_lara = "missing"
            else:
                house_lara = round(lara_df['House district'].iloc[ind])
                senate_lara = round(lara_df['Senate district'].iloc[ind])
            if pd.isna(mhvillage_df['House district'].iloc[ind]) or pd.isna(mhvillage_df['Senate district'].iloc[ind]):
                house_mh = "missing"
                senate_mh = "missing"
            else:
                house_mh = round(mhvillage_df['House district'].iloc[ind])
                senate_mh = round(mhvillage_df['Senate district'].iloc[ind])

            if pd.isna(mhvillage_df['Sites'].iloc[ind]):
                mhsites = "missing"
            else:
                mhsites = round(mhvillage_df['Sites'].iloc[ind])
    ########Make markers
            markeri = L.Marker(
                location=(lat,lon),
                draggable=False,
                title=str(mhvillage_df['Name'].iloc[ind])+
                ' , number of sites: '+str(mhsites)+
                ' , average rent: '+str(mhvillage_df['Average_rent'].iloc[ind])+
                ' , House district: '+str(house_mh)+
                ' , Senate district: '+str(senate_mh)+
                ' , url: %s'%str(mhvillage_df['Url'].iloc[ind]) +
                ' , MHVillage')
            circleMHi = L.Circle(location=(lat,lon), radius=1, color="orange", fill_color= "orange")
            circlelist_mh.append(circleMHi)
            mklist_mh.append(markeri) 

    else:
        if len(circlelist_lara) >0  and len(mklist_lara)>0:
            return
        for ind in range(len(lara_df)):
            lon = float(lara_df['longitude'].iloc[ind])
            lat = float(lara_df['latitude'].iloc[ind])
            house_lara = "missing"
            senate_lara = "missing"

            if pd.isna(lara_df['House district'].iloc[ind]) or pd.isna(lara_df['Senate district'].iloc[ind]):
                house_lara = "missing"
                senate_lara = "missing"
            else:
                house_lara = int(lara_df['House district'].iloc[ind])
                senate_lara = int(lara_df['Senate district'].iloc[ind])

            if pd.isna(lara_df['Total_#_Sites'].iloc[ind]):
                larasites = "missing"
            else:
                larasites = round(lara_df['Total_#_Sites'].iloc[ind])

            if lon == 0 and lat == 0:
                continue
            try:
                markeri = L.Marker(
                    location=(lat,lon),
                    draggable=False,
                    title=str(lara_df['Owner / Community_Name'].iloc[ind])+
                    ' , number of sites: '+str(round(lara_df['Total_#_Sites'].iloc[ind]))+
                    ' , House district: '+ str(house_lara)+
                    ' , Senate district: '+ str(senate_lara)+
                    ', LARA')
                circlei = L.Circle(location=(lat,lon), radius=1, color="blue", fill_color="blue")
                circlelist_lara.append(circlei)

            except:
                #print(lon,lat)
                continue


            mklist_lara.append(markeri)
    return


def build_infographics1():
    total_sites_by_name = lara_df[['County', "Total_#_Sites"]].dropna().groupby('County').sum()
    total_sites_by_name = total_sites_by_name.sort_values(by="Total_#_Sites", ascending=False)
    totnum = 20
    total_sites_by_name = total_sites_by_name.iloc[:totnum, :]
    sns.set_color_codes("pastel")

    cmap = plt.get_cmap('viridis')
    norm = mcolors.Normalize(vmin=total_sites_by_name["Total_#_Sites"].min(),
                             vmax=total_sites_by_name["Total_#_Sites"].max())
    colors = [cmap(norm(value)) for value in total_sites_by_name["Total_#_Sites"]]

    ax = sns.barplot(x="Total_#_Sites", y="County", data=total_sites_by_name,
                     palette=colors, edgecolor='w')
    ax.set(xlabel="Total Number of Sites", title='Top 20 Michigan Counties by number of manufactured home sites (LARA)')

    ax.xaxis.set_major_formatter(FuncFormatter(lambda x, _: f'{x:,.0f}'))

    return ax

def build_infographics2():
    total_sites_by_name = mhvillage_df[['County',"Average_rent"]].dropna().groupby('County').mean()
    total_sites_by_name = total_sites_by_name.sort_values(by="Average_rent",ascending=True)
    # Drop rows where 'second_column' is empty
    df_clean = mhvillage_df[['County',"Average_rent"]].dropna()
    county_counts = df_clean['County'].value_counts()
    total_sites_by_name_count = pd.concat([total_sites_by_name,county_counts], axis=1)
    total_sites_by_name_count_20 = total_sites_by_name_count.sort_values(by="count",ascending=False)
    total_sites_by_name_count_20 = total_sites_by_name_count_20[:20].sort_values(by="Average_rent",ascending=False)
    totnum = -1

    county = total_sites_by_name_count_20[:totnum].index
    count0 = total_sites_by_name_count_20['count'][:totnum]
    y_pos = range(len(total_sites_by_name_count_20[:totnum]))

    totnum = -1
    total_sites_by_name_count_20 = total_sites_by_name_count_20.iloc[:totnum, :].reset_index()

    # Create a color gradient based on the average rent
    cmap = plt.get_cmap('viridis')  # Choose the colormap
    norm = mcolors.Normalize(vmin=total_sites_by_name_count_20["Average_rent"].min(),
                             vmax=total_sites_by_name_count_20["Average_rent"].max())
    colors = [cmap(norm(value)) for value in total_sites_by_name_count_20["Average_rent"]]

    ax = sns.barplot(x="Average_rent", y="County", data=total_sites_by_name_count_20,
                     label="Average rent", palette=colors, edgecolor='w')
    ax.set(xlabel='Average rent', title="Average rent by county (MHVillage)")

    for i, bar in enumerate(ax.patches):
        ax.text(bar.get_width(), bar.get_y() + bar.get_height() / 2,
                f'{total_sites_by_name_count_20["count"][i]:.0f}',
                ha='left', va='center', fontsize=10, color='black')

    return ax


basemaps = {
  "OpenStreetMap": L.basemaps.OpenStreetMap.Mapnik,
  "Satellite": L.basemaps.Gaode.Satellite
}

options = list([])


geographic_regions = [
'County','House district','Senate district'
]


layernames = ["Marker MHVillage (name, address, # sites, source)",
"Marker LARA (name, address, # sites, source)",
    "Circle MHVillage (location only)", #"Circle (MHVillage location only)",
    "Circle LARA (location only)",
    "Legislative districts (Michigan State Senate)",
    "Legislative districts (Michigan State House of Representatives)"]

app_ui = ui.page_fluid(
    ui.HTML("""
        <hr>
        <h1 style="text-align: center; margin-bottom: 10px;"><b>Manufactured Housing Communities in Michigan</b></h1>
        <h2 style="text-align: center; margin-bottom: 40px;
        font-size: 18px; ">Project by <a href="https://www.mhaction.org"
        target="_blank"><i>MH Action</i></a> and
        <a href="https://informs.engin.umich.edu/" target="_blank"><i>INFORMS at the University of Michigan</i></a>
        </h2>
    """),
    ui.row(
        ui.column(5,
                  ui.HTML("""
                    <h2 style="text-align: left; font-size: 20px;"><b>About</b></h2>
                    <h3 style="font-size: 16px;">
                    This app is a visualization tool designed to highlight the distribution of manufactured housing communities across Michigan. LARA data was obtained in January 2024 from the Michigan <a href="https://www.michigan.gov/lara" target="_blank">Department of Licensing and Regulatory Affairs</a> via a Freedom of Information Act (<a href="https://michiganlara.govqa.us/WEBAPP/_rs/(S(yu3ftx4zmh34spiozdwicnsn))/supporthome.aspx" target="_blank">FOIA</a>) Request. <a href="https://www.mhvillage.com/Communities/CommunityReport.php" target="_blank">MHVillage</a> data was scraped in December 2023. For more information, visit <a href="https://www.mhaction.org" target="_blank">MHAction.org</a>.

                    <br><br>
                    <h2 style="text-align: left; font-size: 18px;">Definitions</h2>
                    <h3 style="font-size: 16px;">
                    <ul>
                    <li><b>MHC:</b> Manufactured Housing Community</li>
                    <li><b>LARA:</b> Michigan Department of Licensing and Regulatory Affairs. Michigan MHC's are required to register with LARA.</li>
                    <li><b>MHVillage:</b> Online marketplace for buying and selling manufactured homes.</li>
                    </ul>
                    <h2 style="font-size: 18px;"><br>Add Map Layers</h2>
                """),
                  ui.input_select("basemap", "Choose a basemap:", choices=list(basemaps.keys())),
                  ui.input_selectize("layers", "Layers to visualize:", layernames, multiple=True, selected=None)
                  ),
        ui.column(7, output_widget("map", width="auto", height="600px",),
            ui.HTML("</h3> <p style='text-align: center; font-size: 16px;'><i> NOTE: Blue circles are MHC's reported by LARA, orange circles are reported by MHVillage.</i></p>"),),
    ),
    ui.HTML("<hr> <h1><b>Infographics</b></h1>"),
    ui.row(
        ui.column(10, ui.output_plot("infographics1")),
        ui.column(2, ui.HTML("<br><br>Need other county data? Download the full table "), ui.download_link("download_info1", "here."))
    ),

    ui.row(
        ui.column(10, ui.output_plot("infographics2")),
        ui.column(2, ui.HTML("<br><br>More rent values "), ui.download_link("download_info2", "here."))
    ),

    ui.HTML("""
        <h2 style="text-align: left; margin-bottom: 10px;
        font-size: 16px; "><i>NOTE: Black numbers next to the bars represent the number of MHC's included in the calculated average, based on availability of data on MHVillage. For example, the average rent across the 14 reported MHC's in Oakland County is approximately $575.</i></h2>
    """),

    ui.HTML("<hr> <h1><b>Tables</b></h1>"),
    ui.row(
        ui.column(3,
            ui.input_selectize("main_category", "Select a geographic boundary:", choices=geographic_regions),
            ui.output_ui("sub_category_ui"),
            ui.input_selectize("datasource", "Select a source:", choices=[ 'LARA', 'MHVillage'], ),
        ),

    ),
    ui.row(
        ui.column(6,ui.output_table("site_list")),
        ui.column(3, ui.HTML("""
                <h1 style="text-align: left; margin-bottom: 1px;
                font-size: 18px; "<br><br><b>Summary of Location Totals</b></h2>
            """),
            ui.output_table("site_list_summary"),
            ui.download_button("download_data", "Download Table")
        )
    ),
    #ui.tags.div(ui.output_html("district_map"))

    ui.HTML("""
        <hr>
        <h1 style="text-align: left; margin-bottom: 10px;"><b>Credits</b></h1>
        <h2 style="text-align: left; margin-bottom: 10px;
        font-size: 18px; ">Project lead: <a href="mailto:hessakh@umich.edu" target="_blank">Hessa Al-Thani</a><br>
        MHAction contact: <a href="mailto:pterranova@mhaction.org" target="_blank">Paul Terranova</a> with support from <a href="mailto:dcampbell@ionia-mi.net" target="_blank">Deb Campbell</a> <br>
        Website development: Naichen Shi <br>
        Web design: Vicky Wang <br>
        Data scraping and collection: Bingqing Xiang<br>
        In partnership with the <a href="https://ginsberg.umich.edu/ctac"
        target="_blank">Community Technical Assistance Collaborative</a> at the University of Michigan.</h2>
    """),

    ui.HTML("""
        <hr>
        <h1 style="text-align: left; margin-bottom: 10px;"><b>Reference Files</b></h1>
    """),
    ui.download_link("download_mhvillage", "Raw data: MHVillage with coordinates and legislative district .csv"),
    ui.HTML("""
        <br>
    """),
    ui.download_link("download_lara", "Raw data: LARA with coordinates and legislative distric .csv"),
    ui.HTML("""
        <br>
    """),
    ui.download_link("download_house_districts", "Michigan State House Districts 2021 .GeoJSON"),
    ui.HTML("""
        <br>
    """),
    ui.download_link("download_senate_districts", "Michigan State Senate Districts 2021 .GeoJSON"),

    ui.HTML("""
        <hr>
        <h2 style="text-align: left; margin-bottom: 10px; font-size: 16px;">This is an updated version from June 2024. The original app can be found <a href="https://hessakh.shinyapps.io/michigan_housing1/" target="_blank">here.</a> Updated source code can be found on <a href="https://github.com/viwaumich/mhc" target="_blank">Git.</a> Please reach out to Vicky Wang (<a href="mailto:viwa@umich.edu" target="_blank">viwa@umich.edu</a>) with questions.</h2>
    """),
     #       <h2 style="text-align: left; margin-bottom: 10px;font-size: 18px;
      #  Source code can be found on
       # <a href="https://github.com/soundsinteresting/Michigan_housing/" target="_blank">Git</a> </h2>
)



def server(input, output, session):
# Use a reactive expression to determine the subcategory options
    @reactive.Calc
    def sub_category_options():
        main_category = input.main_category()
        df_name = input.datasource()
        if main_category and df_name == 'MHVillage':
            return mhvillage_df[main_category].dropna().tolist()
        elif main_category :
            if main_category == "House district" or main_category == "Senate district":
                return lara_df[main_category].dropna().astype(int).unique().tolist()
            else:
                return lara_df[main_category].dropna().unique().tolist()

        return []

    # Use render functions to create UI elements, output_text_verbatim is used here for simplicity to show the results
    @output
    @render.ui
    def sub_category_ui():
        options = sub_category_options()
        options.sort()
        return ui.input_select("sub_category", "Select district/county of interest (Note- only locations with MHC data will generate a table):",
            options)


    def create_map(basemap, layerlist):
        the_map = L.Map(basemap=basemap,
                        center=[44.44343571548758, -84.36155640717737],
                        zoom=6,
                        layout=Layout(width="100%", height="100%"),
                        scroll_wheel_zoom=True)
        markerorcircle = False

        if "Marker MHVillage (name, address, # sites, source)" in layerlist:
            build_marker_layer(LARA_C = 0)
            marker_cluster = L.MarkerCluster(
                name='location markers',
                markers=tuple(mklist_mh)
                )
            the_map.add_layer(marker_cluster)
            markerorcircle = True
        if "Marker LARA (name, address, # sites, source)" in layerlist:
            build_marker_layer(LARA_C = 1)
            marker_cluster = L.MarkerCluster(
                name='location markers',
                markers=tuple(mklist_lara)
                )
            the_map.add_layer(marker_cluster)
            markerorcircle = True
        if "Circle MHVillage (location only)" in layerlist:
            if not markerorcircle:
                build_marker_layer(LARA_C = 0)
            layergroup = L.LayerGroup(name = 'location circles',layers=circlelist_mh)
            the_map.add_layer(layergroup)
            markerorcircle = True
        if "Circle LARA (location only)" in layerlist:
            if not markerorcircle:
                build_marker_layer(LARA_C = 1)
            layergroup = L.LayerGroup(name = 'location circles MH',layers=circlelist_lara)
            the_map.add_layer(layergroup)
            markerorcircle = True
        if "Legislative districts (Michigan State Senate)" in layerlist:
            build_district_layers(upper = 1)
            the_map.add_layer(upper_layers[0])
        if "Legislative districts (Michigan State House of Representatives)" in layerlist:
            build_district_layers(upper = 0)
            the_map.add_layer(lower_layers[0])

        lara_layer_group = L.LayerGroup()
        mhvillage_layer_group = L.LayerGroup()

        return the_map

    @output
    @render_widget
    def map():
        # Use input values to get the selected basemap and layers
        basemap = basemaps[input.basemap()]
        layerlist = input.layers()

        return create_map(basemap, layerlist)

# # Define server logic
# def server(input, output, session):

    @output
    @render.plot
    def infographics1():
        build_infographics1()

    @output
    @render.download(filename=lambda: f"all-mhc-counts.csv")
    def download_info1():
        df = lara_df[['County', 'Total_#_Sites']].dropna()
        county_sites_df = df.groupby('County')['Total_#_Sites'].sum().reset_index()

        county_sites_df = county_sites_df.rename(columns={'Total_#_Sites': 'Number of Sites'})

        county_sites_df = county_sites_df.sort_values('Number of Sites', ascending=False)

        output = io.StringIO()
        county_sites_df.to_csv(output, index=False)
        output.seek(0)

        return output.getvalue(), ""

    @output
    @render.plot
    def infographics2():
        build_infographics2()

    @output
    @render.download(filename=lambda: f"all-mhc-rents.csv")
    def download_info2():
        df = mhvillage_df[['County', 'Average_rent']].dropna()
        county_sites_df = df.groupby('County')['Average_rent'].mean().reset_index()

        county_sites_df = county_sites_df.rename(columns={'Average_rent': 'Average Rent'})

        county_sites_df = county_sites_df.sort_values('Average Rent', ascending=False)
        county_sites_df['Average Rent'] = county_sites_df['Average Rent'].round(2)

        output = io.StringIO()
        county_sites_df.to_csv(output, index=False)
        output.seek(0)

        return output.getvalue(), ""

    @reactive.Calc
    def reactive_site_list():
        if input.datasource() == 'MHVillage':
            if input.main_category() == 'County':
                df = (mhvillage_df[mhvillage_df['County'] == input.sub_category()]
                      [['Name','Sites','FullstreetAddress']])
            else:
                df = (mhvillage_df[mhvillage_df[input.main_category()] == int(float(input.sub_category()))]
                      [['Name','Sites','FullstreetAddress']])
        else:
            if input.main_category() == 'County':
                df = (lara_df[lara_df[input.main_category()] == input.sub_category()]
                      [['Owner / Community_Name','Total_#_Sites','Location_Address']])
            else:
                house_district = int(float(input.sub_category()))
                df = (lara_df[lara_df[input.main_category()] == house_district]
                      [['Owner / Community_Name','Total_#_Sites','Location_Address']])

        # Clean up column names by removing underscores
        df = df.rename(columns=lambda x: x.replace('_', ' '))
        df = df.rename(columns=lambda x: x.replace('Owner / Community Name', 'Owner/Community Name'))
        df = df.rename(columns=lambda x: x.replace('Total_#_Sites', 'Number of Sites'))
        df = df.rename(columns=lambda x: x.replace('FullstreetAddress', 'Address'))

        # Further processing if necessary
        df = df.dropna().astype({'Sites': int} if 'Sites' in df.columns else {})
        df = df.sort_values('Sites' if 'Sites' in df.columns else 'Total # Sites', ascending=False)


        return df

    @output
    @render.table
    def site_list():
        return reactive_site_list()

    @output
    @render.table
    def site_list_summary():
        df = reactive_site_list()  # Access the reactive value which is always up to date
        site_count_column = 'Sites' if 'Sites' in df.columns else 'Total # Sites'

        num_mhcs = len(df)
        num_sites = pd.to_numeric(df[site_count_column], errors='coerce').sum()

        summary_df = pd.DataFrame({
            'Number of MHC\'s': [num_mhcs],
            '# of Sites': [num_sites]
        })
        return summary_df

    @output
    @render.download(filename=lambda: f"data-{date.today().isoformat()}-mhc.csv"
    )
    def download_data():
        if input.datasource() == 'MHVillage':
            if input.main_category() == 'County':
                df = (mhvillage_df[mhvillage_df['County'] == input.sub_category()]
                      [['Name', 'Sites', 'FullstreetAddress']])
            else:
                df = (mhvillage_df[mhvillage_df[input.main_category()] == int(float(input.sub_category()))]
                      [['Name', 'Sites', 'FullstreetAddress']])
        else:
            if input.main_category() == 'County':
                df = (lara_df[lara_df[input.main_category()] == input.sub_category()]
                      [['Owner / Community_Name', 'Total_#_Sites', 'Location_Address']])
            else:
                house_district = int(float(input.sub_category()))
                df = (lara_df[lara_df[input.main_category()] == house_district]
                      [['Owner / Community_Name', 'Total_#_Sites', 'Location_Address']])

        # Clean up column names by removing underscores
        df = df.rename(columns=lambda x: x.replace('_', ' '))
        df = df.rename(columns=lambda x: x.replace('Owner / Community Name', 'Owner/Community Name'))
        df = df.rename(columns=lambda x: x.replace('Total_#_Sites', 'Number of Sites'))
        df = df.rename(columns=lambda x: x.replace('FullstreetAddress', 'Address'))

        # Further processing if necessary
        df = df.dropna().astype({'Sites': int} if 'Sites' in df.columns else {})
        df = df.sort_values('Sites' if 'Sites' in df.columns else 'Total # Sites', ascending=False)

        df2 = reactive_site_list()
        site_count_column = 'Sites' if 'Sites' in df2.columns else 'Total # Sites'

        num_mhcs = len(df2)
        num_sites = pd.to_numeric(df2[site_count_column], errors='coerce').sum()

        summary_df = pd.DataFrame({
            'Number of MHC\'s': [num_mhcs],
            '# of Sites': [num_sites]
        })

        output = io.StringIO()
        df.to_csv(output, index=False)
        summary_df.to_csv(output, index=False)
        output.seek(0)

        return output.getvalue(), ""

    @output
    @render.download(filename=lambda: f"lara_with_coord_and_legislativedistrict.csv")
    def download_mhvillage():
        output = io.StringIO()
        mhvillage_df.to_csv(output, index=False)
        output.seek(0)
        return output.getvalue(), ""

    @output
    @render.download(filename=lambda: f"MHVillageDec7_Legislative1.csv")
    def download_mhvillage():
        output = io.StringIO()
        mhvillage_df.to_csv(output, index=False)
        output.seek(0)
        return output.getvalue(), ""

    @output
    @render.download(filename=lambda: f"LARA_with_coord_and_legislativedistrict1.csv")
    def download_lara():
        output = io.StringIO()
        lara_df.to_csv(output, index=False)
        output.seek(0)
        return output.getvalue(), ""

    @output
    @render.download(filename=lambda: f"Michigan_State_House_Districts_2021.json")
    def download_house_districts():
        output = io.StringIO()
        with open(here.parent / house_districts_geojson_path, 'r') as f:
            output.write(f.read())
        output.seek(0)
        return output.getvalue(), ""

    @output
    @render.download(filename=lambda:
    f"Michigan_State_Senate_Districts_2021.json")
    def download_senate_districts():
        output = io.StringIO()
        with open(here.parent / senate_districts_geojson_path, 'r') as f:
            output.write(f.read())
        output.seek(0)
        return output.getvalue(), ""

    @render.code
    def info():
        return str([type(hist.widget), type(hist.value)])



#removed to run on shiny.io
app = App(app_ui, server, debug = True)

