# GSL
Great Salt Lake data analysis scripts
by Carie Frantz cariefrantz@weber.edu

## List of scripts
<table>
<tr><th>Script</th><th>Description</th><th>Data files used</th><th>Other requirements</th></tr>
<tr><td>DataProcessing.py</td><td>Master data processing script. Builds <a href="https://faculty.weber.edu/cariefrantz/GSL/GSLMO_plots_bokeh.html">HTML page</a> of static and <a href="https://docs.bokeh.org">bokeh</a> interactive plots for GSLMO website updating. Updates web files with new logger data. Right now it only plots HOBO data.</td><td>Files on faculty page: SiteA_combined.csv, SiteB_combined.csv, LakeElevationSaltair.csv, plus raw offloaded HOBO csv files</td><td>StationWeather.py code must be edited to add API keys before using this script.</td></tr>
<tr><td>DensityDiff.py</td><td>Determines the relative difference that different water density assumptions make on the calculated lake depth from HOBO logger water pressure data and weather station air pressure data.</td><td>HOBO_SiteA.csv, HOBO_SiteB.csv</td><td></td></tr>
<tr><td>fanDiagram_2.6.py</td><td>Builds fan diagrams with process arrows from PHREEQC saturation calculations.</td><td>PHREEQC-Out.csv</td><td></td></tr>
<tr><td>fanDiagram_pH-T-points.py</td><td>Plots fan diagrams for all available minerals from PHREEQC saturation calculations. Overlays measured pH and T points from the field.</td><td>PHREEQC-Out.csv, GSL_FieldData.csv</td><td></td></tr>
<tr><td>StationWeather.py</td><td>Downloads weather station data from remote weather station. Requires valid API key for remote weather station to work, the version in this code is intentionally invalid for security purposes. Requires additional dependencies not listed below.</td><td></td><td>Weather station API key</td></tr>
<tr><td>WUNDERScrape.py</td><td>Scrapes the <a href="https://www.wunderground.com">Weather Underground</a> website for a personal weather station to download daily data for a date range.</td><td></td><td>This script worked with wunderground.com PWS page formatting on 6/30/2021. Any changes to the page HTML may break this script.</td></tr>
<tr><td>WUNDERCompare.py</td><td>Generates a <a href="https://faculty.weber.edu/cariefrantz/GSL/WUNDERplots.html">website</a> with interactive <a href="https://docs.bokeh.org">bokeh</a> plots from scraped <a href="https://www.wunderground.com">Weather Underground</a> data generated by WUNDERScrape.py. Allows easy and pretty comparison of data from different stations.</td><td>A set of wu_STATION.csv files generated by WUNDERScrape.py</td><td></td></tr>
</table>

## Shared scripts
The following scripts are called by several of the main scripts listed above. Download these to the same directory as the scripts above.
<table>
<tr><th>Script</th><th>Description</th></tr>
<tr><td>ResearchModules.py</td><td>Common functions used by multiple other scripts.</td></tr>
<tr><td>ResearchModules_old.py</td><td>Contains code for timeseries plots no longer used by DataProcessing script.</td></tr>
</table>

## Setting up
The code for this project requires the following list of packages in order to run.
<ul>
<li>beautifulsoup4</li>
<li>bokeh</li>
<li>datetime</li>
<li>math</li>
<li>matplotlib</li>
<li>numpy</li>
<li>os</li>
<li>pandas</li>
<li>progress</li>
<li>requests</li>
<li>subprocess</li>
<li>sys</li>
<li>time</li>
<li>tkinter</li>
</ul>

To install using conda, execute the command:

	conda install tkinter
	conda install progress
	
...and so on

To install using pip, execute the command:

	pip install tkinter
	pip install progress
	
...and so on

## Running
Once python and the packages listed above have been installed, to run a script from command line, execute the command:

	python DensityDiff.py
	python WebTaxBarplotsSimple.py
	
...and so on