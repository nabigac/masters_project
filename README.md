# Master's Project
## Changing Climate Impacts: Analytics to Characterize Extreme Temperature Events in California

<img
  src="./images/static/return_value/cesm2_hist_1980_rv_geo_plot.svg"
  width="500"
  height="350"
/>
<img
  src="./images/static/return_value/cesm2_ssp370_2080_rv_geo_plot.svg"
  width="500"
  height="350"
/>

**A repository containing the code, datasets, visualizations, and data products that correspond to the analytics in the UC Berkeley Energy & Resources Master's Project paper by Nabig Chaudhry.**

Please contact nabigac@berkeley.edu if you have any questions or issues regarding the code.
<br />
<br />
### Abstract <br />
Climate change will alter extreme weather event exposure and consequently intensify climate impact on human and natural systems. Assessment of exposure and impact is critical for understanding system vulnerabilities and building adaptation and resilience to climate change. However, this information is complex, difficult to use, and often too broad for stakeholders -- many of whom require very context-specific information on particular geographies, events types, or critical thresholds. One promising solution is to develop customizable analytics and/or analytic tools that demonstrate scientifically defensible approaches of extracting context-specific information for decision applications, which can be adapted to different geographies and user-specific metrics. In this paper, I demonstrate the application of customizable analytics to quantify extreme weather event exposure by evaluating the return value of 1-in-10-year extreme temperature events in California from periods starting in 1980 and ending in 2100. Through extreme value analysis supported by L-moments and the generalized extreme value distribution, I produce data products that detail return values of 1-in-10-year extreme temperature events across two global climate models (CESM2 and CNRM-ESM2-1), one projected scenario (SSP3-7.0), five 20-year temporal periods (1980-1999, 2020-2039, 2040-2059, 2060-2079, and 2080-2099), and every 9-km gridded area in California. The data products I produced highlight an approach to using customizable analytics to deliver decision-relevant insights on climate impact to stakeholders.
<br />
<br />
### File Directory
```
├── data
│   ├── intial_resampled            <- Initial annual maximum series datasets resampled from raw GCM data.
│   │   ├── 45km
│   │   └── 9km
│   │
│   ├── intermediate_processed      <- Intermediate processed and formatted data to prepare for analysis.
│   └── final_for_analysis          <- Final KS test and return value results used for visualizations and analysis.                      
│                          
├── images
│   ├── interactive                 <- Interactive HTML plots of results. Open using web browser.
│   │   ├── ks_test
│   │   ├── percent_change
│   │   └── return_value
│   │
│   └── static                      <- Static SVG images of results.
│       ├── ks_test
│       ├── percent_change
│       └── return_value
│                               
├── notebooks                       <- Jupyter notebooks containing code (ordered). 
│  
├── LICENSE                          
├── README.md                       <- Top-level README for developers using this project.  
├── environment.yml                 <- Conda environment file. Create using `conda env create -f environment.yml`.
│                     
└── masters_project_functions.py    <- Core Python functions used in notebooks.
```
