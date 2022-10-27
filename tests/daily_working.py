import cdstoolbox as ct

layout = {
    'input_ncols': 1,
    'output_align': 'right'
}

### General variables ###
NO_DATA = [
    'UKM65', 'UKM66', 'UKN09', 'UKN13', 'UKJ34', 'ES531', 'ES533',
    'MT001', 'EL621', 'EL622', 'EL623', 'EL624', 'EL412', 'EL413',
    'EL422', 'DK014', 'NL324', 'DE942', 'FRY30', 'PT200', 'PT300',
    'ES703', 'ES704', 'ES705', 'ES706', 'ES707', 'ES708', 'ES709',
    'TRA21', 'TRA22', 'TRA23', 'TRB21', 'TRB23', 'TRB24', 'TRC32',
    'TRC33', 'TRC34',
]

GCM_MODELS=[
    {
        'value': 'cnrm_cm5',
        'label': 'CNRM-CM5 (CNRM-CERFACS, France)',
    },
    {
        'value': 'ec_earth',
        'label': 'EC-EARTH (ICHEC, Ireland)',
    },
    {
        'value': 'hadgem2_es',
        'label': 'HadGEM2-ES (UK Met Office, UK)',
    },
    {
        'value': 'ipsl_cm5a_mr',
        'label': 'IPSL-CM5A-MR (IPSL, France)',
    },
    {
        'value': 'mpi_esm_lr',
        'label': 'MPI-ESM-LR (MPI, Germany)',
    },
    {
        'value': 'noresm1_m',
        'label': 'NorESM1-M (NCC, Norway)',
    }
]

AVAILABLE_MODELS={
    'rcp8_5':['cnrm_cm5','ec_earth','hadgem2_es','ipsl_cm5a_mr','mpi_esm_lr','noresm1_m'],
    'rcp4_5':['cnrm_cm5','ec_earth','hadgem2_es','ipsl_cm5a_mr','mpi_esm_lr'],
    'rcp2_6':['ec_earth','hadgem2_es','mpi_esm_lr','noresm1_m']
}

RCPS = [
    {
        'value': 'rcp2_6',
        'label': 'Ambitious mitigation policies (RCP2.6)',
    },
    {
        'value': 'rcp4_5',
        'label': 'Moderately ambitious mitigation policies (RCP4.5)',
    },
    {
        'value': 'rcp8_5',
        'label': 'Unambitious mitigation policies (RCP8.5)',
    },
]

DEPT_DATA = [
    {
        'value': 'daily',
        'label': 'Daily fire risk',
    },
    {
        'value': 'models',
        'label': 'Model statistics',
    },
    {
        'value': 'horizons',
        'label': 'Time horizons',
    },
    {
        'value': 'rcps',
        'label': 'RCP scenarios',
    },
]

REANALYSIS_PERIOD = (1981, 2005)

TIME_HORIZONS = [
    {
        'value':'2021_2040',
        'label':'2021-2040'
    },
    {
        'value':'2041_2060',
        'label':'2041-2060'
    },
    {
        'value':['2061_2065','2066_2070','2071_2075','2076_2080'],
        'label':'2061-2080'
    },
    {
        'value':['2081_2085','2086_2090','2091_2095','2096_2098'],
        'label':'2081-2098'
    },
]


@ct.input.dropdown('rcp', default=RCPS[-1]['value'], values=RCPS)

@ct.input.slider(
    'time_period', min = 2006, max = 2098, step = 1,
    default=[2009,2010],
    label='Time range',
    description= 'Select the start and top year of the period of interest.',
    help= 'Time period selection.',
)



@ct.child(position='bottom')
@ct.input.dropdown(
    'data_choice', values=DEPT_DATA, label='Comparison',
)
@ct.output.livefigure()

def child(params,data,data_choice,rcp,time_period):
    """
    This sub app displays the selected data in a plot for the selected departement and the selected years.
    """

    # Instantiate fig as None
    fig = None


    # Extract the country name for plot label
    id_dept = params['properties']['name']
    
    
    # Select data for the clicked NUTS shape
    if data_choice=='daily':
        data_sel = ct.cube.select(data, nuts=params['properties']['NUTS_ID'])

        # Plot time series
        if fig is None:
            fig = ct.chart.line(
                data_sel,
                layout_kwargs={
                    'title': 'Daily fire risk',
                    'xaxis': {'title': ''},
                    'yaxis': {'title': 'Daily fire risk'}
                },
                scatter_kwargs={
                    'name': id_dept
                }
            )
        else:
            fig = ct.chart.line(
                data_sel,
                fig=fig,
                layout_kwargs={
                    'title': 'Daily fire risk',
                    'xaxis': {'title': ''},
                    'yaxis': {'title': 'Daily fire risk'}
                },
                scatter_kwargs={
                    'name': id_dept
                }

            )
    else:

        if data_choice=='models':
            pass
        
        elif data_choice=='horizons':
            horizons_data=[]
            for time in TIME_HORIZONS:
                data = ct.catalogue.retrieve(
                    'sis-tourism-fire-danger-indicators',
                    {
                        'time_aggregation': 'seasonal_indicators',
                        'product_type': 'single_model',
                        'variable': 'seasonal_fire_weather_index',
                        'gcm_model': AVAILABLE_MODELS[rcp],
                        'experiment': rcp,
                        'period': time['value'],
                    }
                )
                data = ct.geo.make_regular(data, xref='rlon', yref='rlat',
                                           drop_encoding=['rlon', 'rlat'])
                data = ct.cdm.standardise_time(data)
                data = ct.cube.average(data, dim='time')
                horizons_data.append(data)
            for hd in range(len(horizons_data)):
                fig = ct.chart.bar(hd, fig=fig)
    
        elif data_choice=='rcps':
            pass

    return fig


@ct.input.dropdown('gcm_model', default=GCM_MODELS[-1]['value'], values=GCM_MODELS)

@ct.input.dropdown('rcp', default=RCPS[-1]['value'], values=RCPS)

@ct.input.slider(
    'time_period', min = 2006, max = 2098, step = 1,
    default=[2009,2010],
    label='Time range',
    description= 'Select the start and top year of the period of interest.',
    help= 'Time period selection.',
)



### Main live map ###
@ct.application(title='Live map of the daily indicators',layout=layout)
@ct.output.livemap(click_on_feature=child)
def application(gcm_model,rcp,time_period):
    
    if gcm_model not in AVAILABLE_MODELS[rcp]:
        print('The model '+gcm_model+' is not available for '+rcp)
    
        
    data = ct.catalogue.retrieve(
        'sis-tourism-fire-danger-indicators',
        {
            'time_aggregation': 'daily_indicators',
            'product_type': 'single_model',
            'variable': 'daily_fire_weather_index',
            'gcm_model': gcm_model,
            'experiment': rcp,
            'period': [str(year) for year in time_period]
        }
    )
    
    
    # Make the data plotable
    data = ct.geo.make_regular(data, xref='rlon', yref='rlat',
                               drop_encoding=['rlon', 'rlat'])
    data = ct.cdm.standardise_time(data)
    
    # Define the clickable NUTS shapes
    nuts = ct.shapes.catalogue.nuts(level=3)

    # Average the retrieved data over the defined shapes
    nuts_average = ct.shapes.average(data, nuts)
    


    nuts_average = ct.cdm.update_attributes(
        nuts_average,
        {'cds_magics_style_name': 'turbo_lt-20_gt40_continuous'}
    )
    

    data_layers = [
        {
            'data': nuts_average,
            'type': 'layer',
            'click_kwargs': {'data': nuts_average},
            'no_data_value': 'No data',
            'no_data_style': {'fillOpacity': 0},
            'label_template': '%{NUTS_NAME} (%{value:+.1f})',
            'zoom_to_selected': False,
            'style_selected': {'weight': 2},
            'cmap': 'RdBu_r',
            'bins': 13,
            'vmin': 0,
            'vmax': 60,
        },
    ]

    missing_depts = ct.shapes.catalogue.nuts(level=3, resolution='high', nuts_id=NO_DATA)
    
    data_layers.append(
        {
            'data': ct.shapes.get_geojson(missing_depts),
            'style': {'fillOpacity': 0, 'opacity': 0},
            'label_template': '%{NUTS_NAME} (No data)',
        }
    )

    fig = ct.livemap.plot(
        data_layers,
        show_legend=True,
        zoom=3,
        lat=49.5,
        lon=16,
        click_foreground_layer=True,
        date_format='dd mmmm yyyy',
    )
    return fig


### Additional functions ###

def get_reanalysis():
    yearly_data = []
    for year in REANALYSIS_PERIOD:
        data = ct.catalogue.retrieve(
            'cems-fire-historical',
            {
                'product_type': 'reanalysis',
                'variable': 'fire_weather_index',
                'version': '3.1',
                'dataset': 'Consolidated dataset',
                'year': str(year),
                'month': [
                    '06', '07', '08',
                    '09',
                ],
                'day': [
                    '01', '02', '03',
                    '04', '05', '06',
                    '07', '08', '09',
                    '10', '11', '12',
                    '13', '14', '15',
                    '16', '17', '18',
                    '19', '20', '21',
                    '22', '23', '24',
                    '25', '26', '27',
                    '28', '29', '30',
                    '31',
                ],
            }
        )
        data = ct.cube.average(data, dim='time')
        yearly_data.append(data)
    data = ct.cube.concat(yearly_data, dim='time')
    data = ct.cube.average(data, dim='time')
    data = ct.cube.select(data, [-25, 46, 32, 72])
    return data

def get_data(time, scenario, model_statistic):


    data = ct.catalogue.retrieve(
        'sis-tourism-fire-danger-indicators',
        {
            'time_aggregation': 'seasonal_indicators',
            'product_type': 'single_model',
            'variable': 'seasonal_fire_weather_index',
            'gcm_model': AVAILABLE_MODELS[scenario],
            'experiment': scenario.lower(),
            'period': time,
        }
    )
    data = ct.geo.make_regular(data, xref='rlon', yref='rlat',
                               drop_encoding=['rlon', 'rlat'])
    data = ct.cube.average(data, dim='time')

    if time != '1981_2005':
        current_climate, _ = get_data(
            'seasonal_indicators', '1981_2005', 'historical', model_statistic)
        anomaly = data - current_climate
        reanalysis = ct.geo.regrid(get_reanalysis(), data)
        data = reanalysis + anomaly
        data = ct.cdm.update_attributes(
            data, {'standard_name': 'fwi-mean-jjas'},
        )

    return data, anomaly