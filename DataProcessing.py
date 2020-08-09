#!/usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'Carie Frantz'
__email__ = 'cariefrantz@weber.edu'
"""Title
Created on Mon Jun 29 15:45:09 2020
@author: cariefrantz
@project: GSLMO

Determines relative influence of density assumptions on calculated lake depth
from HOBO logger water pressure data and weather station air pressure data.

This script was created as part of the
Great Salt Lake Microbialite Observatory project

Arguments:  None

Requirements:
    HOBO_SiteA.csv
    HOBO_SiteB.csv

Example in command line:
    python DataProcessing.py

Dependencies Install:
    sudo apt-get install python3-pip python3-dev
    pip install os
    pip install pandas
    pip install numpy
    pip install matplotlib
    pip install bokeh

You will also need to have the following files
    in the same directory as this script.
They contain modules and variables that this script calls.
    ResearchModules.py
If you get an error indicating that one of these modules is not found,
    change the working directory to the directory containing these files.


Copyright (C) 2020  Carie M. Frantz

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>
"""
####################
# TO DO
####################
'''
FIX
    trimPendantData needs to check for any wacky values mid-log
    
AUTOMATE PROCESSING SEQUENCE:
    1. Load in logger data
    2. For pendants, run weather station combiner script
    3. Quality control: remove start and end where logger is out of water based on "jumps"
    4. Match button data to combined pendant data by matching closest time
    5. Add combined data to existing dataset
    6. Grab Saltair elevation data from last point with 'A' to present
        https://waterdata.usgs.gov/ut/nwis/dv/?site_no=10010000&agency_cd=USGS&amp;referred_module=sw
        https://waterdata.usgs.gov/ut/nwis/dv?cb_62614=on&format=rdb&site_no=10010000&referred_module=sw&period=&begin_date=2019-11-07&end_date=2020-07-14
    7. Re-build plots
    8. Enter field data
    9. Enter core data
    
LOAD FIELD NOTES AND ADD FIELD-BASED DATA PLOTS
# Get file and data
filename, directory, data = ResearchModules.fileGet(
    'Select field notes file', tabletype = 'field')
'''

####################
# IMPORTS
####################
import ResearchModules

import os
import sys
import subprocess

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from bokeh.io import show
from bokeh.layouts import column
from bokeh.plotting import figure, output_file, save
from bokeh.models import ColumnDataSource, Div

####################
# GLOBAL VARIABLES
####################

####################
# DATA IMPORT VARIABLES

# Default directory
directory = os.getcwd()

# Types of input files and available variables
filelist_all = {
    'Site A'    : ['HOBO pendant', 'HOBO button top'],
    'Site B'    : ['HOBO pendant', 'HOBO button top', 'HOBO button side']
        }
HOBO_pendant_col_datetime = 'Date Time, GMT-06:00'

# Weather station data import variables
lim_dTemp = 1   # Exclude any lines where the temperature change exceeds this
lim_dDays = 10  # Max number of days to download from remote weater station
                # at a time
AMBIENT_API_KEY = '35c8a71b05324137a0bc3d220d17c6182df7184953d148c4b8fc8cafe6e06192'

# File in which downloaded weather data is archived
DATA_CACHE_FILE = 'weather-data-cache.csv'


####################
# PLOT VARIABLES

# Color Palette
''' Unused colors
'#565D47' # dark green
'#B49C73' # beige
'#62760C' # green
'#523906' # dark brown
'#888888' # gray
'''
clr_WildcatPurple = '#492365'
clr_UniversityGray = '#575047'
clr_Pantone436 = '#aa989c'
clr_Pantone666 = '#a391b1'

# Plot and dataset info
locations = {
    'Site A'    : {
        'water_density' : 1.07,
        #'color'         : 
        #'color'         : 
        'color'         :  clr_WildcatPurple
        },
    'Site B'    : {
        'water_density' : 1.09,
        #'color'         : 
        #'color'         : 
        'color'         :  clr_UniversityGray
        }
    }

plotlist = {
    'depth'         : {
        'y_axis'        : 'Water depth (m)',
        'range'         : 'Auto',
        
        1   : {
            'location'   : 'Site A',
            'filetype'  : 'HOBO',
            'column'    : 'calc_water_depth_m',
            'title'     : 'Site A (calculated)',
            'color'     : locations['Site A']['color']
            },
        2   : {
            'location'   : 'Site B',
            'filetype'  : 'HOBO',
            'column'    : 'calc_water_depth_m',
            'title'     : 'Site B (calculated)',
            'color'     : locations['Site B']['color']
            },
        },
    
    'temperature'   : {
        'y_axis'        : 'Temperature (\degC)',
        'range'         : (-5,35),
        
        1   : {
            'location'   : 'Site A',
            'filetype'  : 'HOBO',
            'column'    : 'ws_air_temp_C',
            'title'     : 'Antelope Island weater station air temp',
            'color'     : clr_Pantone436
            },
        2   : {
            'location'   : 'Site A',
            'filetype'  : 'HOBO',
            'column'    : 'pndt_water_temp_C',
            'title'     : 'Site A water temp - Pendant',
            'color'     : locations['Site A']['color']
            },
        3   : {
            'location'   : 'Site B',
            'filetype'  : 'HOBO',
            'column'    : 'pndt_water_temp_C',
            'title'     : 'Site B water temp - Pendant',
            'color'     : locations['Site B']['color']
            }
        },
    
    'light'         : {
        'y_axis'        : 'Irradiance (lumen/ft2)',
        'range'         : (0, 7000),
        
        1   : {
            'location'   : 'Site A',
            'filetype'  : 'HOBO',
            'column'    : 'bttn_top_light_lumen_ft2',
            'title'     : 'Site A shuttle top',
            'color'     : locations['Site A']['color']
            },
        2   : {
            'location'   : 'Site B',
            'filetype'  : 'HOBO',
            'column'    : 'bttn_top_light_lumen_ft2',
            'title'     : 'Site B shuttle top',
            'color'     : locations['Site B']['color']
            }
        }
    }


####################
# BOKEH PAGE VARIABLES
        
plt_ht = 5
plt_w = 10
plt_pfx = 'GSL_plots_'
toolset = 'xwheel_zoom, pan, box_zoom, reset, save'

td_style = ' style = "padding: 5px"'
bokeh_head = '''
<h1>Great Salt Lake Microbialite Observatory</h1>
<h2>Weber State University College of Science</h2>

<p>Lead investigator: Dr. Carie Frantz, Department of Earth and Environmental 
Sciences, <a href="mailto:cariefrantz@weber.edu">cariefrantz@weber.edu</a></p>
<p>This project is funded by the National Science Foundation,
<a href="https://www.nsf.gov/awardsearch/showAward?AWD_ID=1801760">
Award #1801760</a></p>

<h2>Instrument Sites</h2>
<p>Both GSLMO instrument sites are located on the Northern shore of Antelope
   Island and are accessed and operated under permits from Antelope Island
   State Park and the State of Utah Division of Forestry, Fire, & State Lands.
   </p>
<table border = "1px" style = "border-collapse: collapse">
<tr style = "background-color: ''' + clr_Pantone666 + ''';
 color : white">
    <th''' + td_style + '''>Site</th>
    <th''' + td_style + '''>Description</th>
    <th''' + td_style + '''>Location</th></tr>
<tr>
    <td''' + td_style + '''>Site A</td>
    <td''' + td_style + '''>Muddy auto causeway site near Farmington Bay
    outlet with high total inorganic carbon.</td>
    <td''' + td_style + '''>41.06646, -112.23129
        <a href="https://goo.gl/maps/66u5BPLuk1ykDvCP8">(map)</a></td>
</tr>
<tr><td''' + td_style + '''>Site B</td>
    <td''' + td_style + '''>Microbialite reef site near Buffalo Point</td>
    <td''' + td_style + '''>41.03811, -112.27889
        <a href="https://goo.gl/maps/AsG9b5yYLwbXYKtA9">(map)</a></td>
</tr>
</table>

<h2>Data Logger Plots</h2>
<p>Plots display the daily minimum and maximum of hourly averages of 
   recorded data. 
   Use the tools in the toolbar to the right of each plot to explore the data.
   Click legend items to turn plotted data on and off.</p>
'''


####################
# FUNCTIONS
####################

####################
### SCRIPTS TO GET AND PROCESS HOBO LOGGER DATA
    
def trimHOBOPendant(data):
    ''' This script trims HOBO Pendant data and removes bad values'''
    lim_checkrows = 10
    cols_data = list(data.columns)[:3]
    cols_log = list(data.columns)[3:]
    
    # Delete anything before and after 'Logged'
    toprow = list(data[data[cols_log[0]] == 'Logged'].index)[0] + 1
    botrow = list(data[data[cols_log[1]] == 'Logged'].index)[0]
    
    # Delete any top lines above a T change >= lim_dt
    for row in range(toprow + 1, toprow + lim_checkrows):
        if abs(data.loc[row, cols_data[2]] 
               - data.loc[row-1, cols_data[2]]) >= lim_dTemp:
            toprow = row
    
    # Delete any bottom lines above a T change >= lim_dt
    for row in np.arange(botrow, botrow-lim_checkrows, -1):
        if abs(data.loc[row, cols_data[2]]
               - data.loc[row-1, cols_data[2]]) >= lim_dTemp:
            botrow = row
            
    # Trim
    return data.loc[np.arange(toprow, botrow), cols_data]
    

def loadHOBOFiles():
    '''Loads in the HOBO logger datasets'''
    directory = os.getcwd()
    for location in locations:
        # Get file and data
        filename, directory, data = ResearchModules.fileGet(
            'Select ' + location + ' combined HOBO file',
            tabletype = 'HOBO_comb', directory = directory)
        # Drop na rows (rows with no values)
        data = data.loc[data.index.dropna()]
        # Convert datetime strings to datetime objects
        data['datetime'] = pd.to_datetime(data.index)
        time_min = str(min(data['datetime']).date())
        time_max = str(max(data['datetime']).date())
        # Do depth calculations
        water_density = locations[location]['water_density']
        data['calc_water_depth_m'] = calc_depth(data, water_density)
        
        # Save
        locations[location]['HOBO'] = data
        
    return directory, time_min, time_max

#%% IN PROGRESS
def processNewHOBOData():
    '''
    # Get file and data
    1. Load in logger data
    2. For pendants, run weather station combiner script
    3. Quality control: remove start and end where logger is out of water based on "jumps"
    4. Match button data to combined pendant data by matching closest time
    5. Add combined data to existing dataset
    6. Grab Saltair elevation data from last point with 'A' to present
        https://waterdata.usgs.gov/ut/nwis/dv/?site_no=10010000&agency_cd=USGS&amp;referred_module=sw
        https://waterdata.usgs.gov/ut/nwis/dv?cb_62614=on&format=rdb&site_no=10010000&referred_module=sw&period=&begin_date=2019-11-07&end_date=2020-07-14
    7. Re-build plots
    '''
    
    # Get files and data
    directory = os.getcwd()
    HOBOfiles = {}
    # Ask user for each file, load files
    for loc in filelist_all:
        HOBOfiles[loc] = {}
        for file in filelist_all[loc]:
            if input('Load ' + loc + ' ' + file + ' file? Y/N  > ') == 'Y':
                filename, directory, HOBOfiles[loc][file] = (
                    ResearchModules.fileGet(
                        'Select ' + loc + ' ' + file + ' file',
                        tabletype = 'HOBO_raw', directory = directory))
    # For pendant loggers, run the weather station combiner script
    for loc in HOBOfiles:
        for file in HOBOfiles[loc]:
            if 'pendant' in file:
                # Trim the file
                data = trimHOBOPendant(HOBOfiles[loc][file])
                # Find start and end dates
                data['Date Time, GMT-06:00'] = pd.to_datetime(
                    data[HOBO_pendant_col_datetime ])
                # Convert datetime strings to datetime objects
                data['datetime'] = pd.to_datetime(data.index)
                timestart = min(data[HOBO_pendant_col_datetime])
                timeend = max(data[HOBO_pendant_col_datetime])
                # Download date ranges from weather station
                get_station_data_for_period(timestart, timeend)
                
                
'''                
                num, rem = divmod(timedelta, lim_dDays)
                date_min = timestart
                if timedelta >= lim_dDays:
                    date_max = timestart + pd.DateOffset(days = lim_dDays)
                else:
                    date_max = timestart + pd.DateOffset(days = timedelta)
                for i in range(num+1):
                    get_station_data_for_period(date_min, date_max, timedelta)
                    date_max = date_min
                # Fill this in
                # HOBOfiles[loc]['combined'] = addWeatherData()
                '''

#%%
####################
### SCRIPTS TO DOWNLOAD AND PROCESS WEATHER STATION DATA

def get_station_data_for_period(date_min, date_max):
    """
    This function gets weather data for a period of time
    Data is downloaded by segments.
    If downloading a file fails, the function continue trying
    """
    print("*** Downloading weather station data ***")
    delta = pd.DateOffset(days = lim_dDays)
    date_curr = date_min  # Start date
    while date_curr < date_max:
        sdate_min = date_curr.strftime('%Y-%m-%d')
        # Upper date limit
        if date_curr + delta > date_max:
            sdate_max = date_max.strftime('%Y-%m-%d')
        else:
            sdate_max = (date_curr + delta).strftime('%Y-%m-%d')
        print('Getting data for %s %s' % (sdate_min, sdate_max), end=' ')
        # Try as many times as is needed to obtain the data
        while not get_station_data(sdate_min, sdate_max):
            print('\nTrying again...', end=' ')
        print('... done.')
        # Updating the cache
        update_station_cache(sdate_min, sdate_max)
        # Removing temporary files
        # filename = get_station_data_filename(sdate_min, sdate_max)
        # os.remove(filename)
        # os.remove(filename.replace('.csv', '.txt'))
        # To get the next segment
        date_curr += delta
        # time.sleep(60)
        

def get_station_data(sdate_min, sdate_max):
    '''
    This function runs the external script station_weather.
    Returns true if the data is obtained.
    Data is stored in an local file.
    '''
    
    # Run station_weather.py
    ret = subprocess.run(' '.join(['python', 'StationWeather.py',
                                  sdate_min, sdate_max, AMBIENT_API_KEY]),
                         capture_output=True, timeout=60) 
    # To do: if the subprocess times out, figure out where it stopped and
    # restart at a different date/time
    if ret.returncode != 0:
        # Program execution returns a invalid code
        print('Error: station weather script execution failed')
        print(ret.stdout)
        sys.exit()
    filename = get_station_data_filename(sdate_min, sdate_max)
    data = pd.read_csv(filename)
    if len(data) == 0:
        # Sometimes API requests does not produce any data
        # Print('Error: weather API is not providing data')
        return False
    else:
        return True


def update_station_cache(sdate_min, sdate_max):
    """
    This functions updates the cache of weather data.
    That cache is an accumulative local file in which
    every downloaded data is stored.
    """
    filename = get_station_data_filename(sdate_min, sdate_max)
    if not os.path.isfile(filename):
        # A valid file for the given dates does not exist
        print('Warning: station data for the given date range does not exist')
        return
    last_data = pd.read_csv(filename)
    last_data.columns = ['dt', 'temp', 'pressure', 'abs_pressure']
    if not os.path.isfile(DATA_CACHE_FILE):
        # If the cache file does not exists, it is created
        last_data.to_csv(DATA_CACHE_FILE, index=False)
        return
    # Updating the cache file
    cache_data = pd.read_csv(DATA_CACHE_FILE)
    new_cache = pd.concat([last_data, cache_data]).drop_duplicates()
    new_cache.to_csv(DATA_CACHE_FILE, index=False)
    
    
def get_station_data_filename(date_min, date_max):
    """
    Using a minimum and a maximum dates, this function produces a filaname
    for the station downloaded data.
    """
    filename = (date_min.replace('-', '') + '-' + date_max.replace('-', '')
                + '.csv')
    return filename


#%%
####################
### SCRIPTS TO PROCESS AND PLOT IMPORTED DATA

def calc_depth(hobo_location, water_density):
    '''Calculate water depth from pressure data and assumed density'''
    gravity_factor = 9.80665
    depth = ((hobo_location['pndt_water_pressure_kPa']
              - hobo_location['ws_air_pressure_kPa'])
             * water_density / gravity_factor)
    return depth


def getPlotInfo(plot):
    lines = [m for m in plotlist[plot] if type(m) == int]
    measlist = [plotlist[plot][line]['title'] for line in lines]
    return lines, measlist
    
    
def getLineProperties(plot, line):
    line_info = plotlist[plot][line]
    ds = locations[line_info['location']][line_info['filetype']]
    time_data = list(ds['datetime'])
    y_data = list(pd.to_numeric(ds[line_info['column']], errors = 'coerce'))
    return line_info, time_data, y_data


def buildStaticPlots(directory, time_min, time_max):
    '''Builds set of svg plots of timeseries data and HTML file for display'''
    for plot in plotlist:

        '''Builds set of svg plots of timeseries data'''
        fig, ax = plt.subplots(figsize = (plt_w, plt_ht))
        lines, measlist = getPlotInfo(plot)
        
        # Gather and plot the raw data for each line
        for line in lines:
            line_info, time_data, y_data = getLineProperties(plot, line)
            
            ax.plot(time_data, y_data, linewidth = 0.5, color = line_info['color'])
            
        ax.set_xlabel('Date')
        ax.set_ylabel(plotlist[plot]['y_axis'])
        ax.legend(measlist)
        y_range = plotlist[plot]['range']
        if type(y_range) == tuple and len(y_range) == 2:
            ax.set_ylim(y_range)
    
        # Save the plots
        fig.savefig(directory + '\\' + plt_pfx + plot + '.svg',
                    transparent = True)
   
    # Write HTML file
    pageHTML = '''
    <HTML>
    <header>
    <h1>Great Salt Lake Microbialite Observatory</h1>
    <p>Data plotted from ''' + time_min + ' to ' + time_max + '''</p>
    <p>Page last updated ''' + str(pd.datetime.now().date()) + '''
    </header>
    <body>
    <h2>Logger data plots</h2>'''
    for plot in plotlist:
        pageHTML = pageHTML + '''
        <p><img src = "''' + plt_pfx + plot + '.svg" alt = "' + plot + '"></p>'
    pageHTML = pageHTML + '''
    </body>
    </HTML>'''
    # Write HTML String to file.html
    filename = directory + '\\GSLMO_plots.html'
    if os.path.isfile(filename):
        os.remove(filename)
    with open(filename, 'w') as file:
        file.write(pageHTML)  



def buildBokehPlots(directory):
    # Set up the bokeh page
    figures = []
    
    for plot in plotlist:
        lines, measlist = getPlotInfo(plot)
        
        # Build the bokeh figure
        fig = figure(plot_height = plt_ht*100, plot_width = plt_w*100,
                     tools = toolset, x_axis_type = 'datetime',
                     title = plot.title())
        
        # Gather and plot the raw data for each series
        for i,line in enumerate(lines):
            line_info, time_data, y_data = getLineProperties(plot, line)
            
            # Generate smoothed hourly data
            y_df = pd.DataFrame(data = y_data, index = time_data,
                                columns = ['y'], copy = True)
            y_df = y_df[~y_df.index.duplicated()]
            y_df = y_df.resample('1T').interpolate(
                'index', limit = 20, limit_area = 'inside').resample(
                    'h').asfreq().dropna()
            # Find daily min/max values
            daily_mm = y_df.resample('D')['y'].agg(['min','max'])        
            # ax.fill_between(daily_mm.index, daily_mm['min'], daily_mm['max'])
            
            # Format the data for bokeh glyph render
            x = np.hstack((daily_mm.index, np.flip(daily_mm.index)))
            y = np.hstack((daily_mm['min'], np.flip(daily_mm['max'])))
            datasource = ColumnDataSource(dict(x=x, y=y))
            
            # Build the figure
            fig.patch('x', 'y', color = line_info['color'],
                      alpha = 0.6, source = datasource,
                      legend_label = measlist[i])
            
        # Label axes and title
        fig.xaxis.axis_label = 'Date'
        fig.yaxis.axis_label = plotlist[plot]['y_axis']
        
        # Configure legend
        fig.legend.location = 'top_left'
        fig.legend.click_policy = 'hide'

        
        # Link figure axes
        if figures:
            fig.x_range = figures[0].x_range
            
        figures.append(fig)
    
    # Save HTML page
    figures.insert(0, Div(text = bokeh_head))
    # show(column(figures))
    output_file(directory + '\\GSLMO_plots_bokeh.html')
    save(column(figures))
        

#%%
####################
# MAIN FUNCTION
####################
if __name__ == '__main__': 
    
    # Load HOBO files
    directory, time_min, time_max = loadHOBOFiles()

    # Build raw data plots and save HTML file
    buildStaticPlots(directory, time_min, time_max)
    
    # Build Bokeh plots
    buildBokehPlots(directory)


       