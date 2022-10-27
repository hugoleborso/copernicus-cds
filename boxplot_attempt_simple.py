import cdstoolbox as ct

TIMES = [
    {
        'value': '1981_2005',
        'label': 'Past (1981_2005)',
    },
    {
        'value': '2021_2040',
        'label': 'Near future (2021-2040)',
    },
    {
        'value': '2041_2060',
        'label': 'Mid-century (2041-2060)',
    },
    {
        'value': '2079_2098',
        'label': 'End of century (2079-2098)',
    },
]

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

COMPARISONS = [
    {
        'value': 'horizons',
        'label': 'Time horizons',
    },
    {
        'value': 'rcps',
        'label': 'RCP scenarios',
    },
]

AVAILABLE_MODELS={
    'historical':['cnrm_cm5', 'ec_earth', 'hadgem2_es','ipsl_cm5a_mr', 'mpi_esm_lr', 'noresm1_m'],
    'rcp8_5':['cnrm_cm5','ec_earth','hadgem2_es','ipsl_cm5a_mr','mpi_esm_lr','noresm1_m'],
    'rcp4_5':['cnrm_cm5','ec_earth','hadgem2_es','ipsl_cm5a_mr','mpi_esm_lr'],
    'rcp2_6':['ec_earth','hadgem2_es','mpi_esm_lr','noresm1_m']
}


@ct.application()

@ct.input.dropdown(
    'time', values=TIMES, label='Time Horizon', default='2021_2040'
)
@ct.input.dropdown(
    'scenario', values=RCPS, label='Scenario'
)
@ct.input.dropdown(
    'compare', values=COMPARISONS, label='Comparison',
)
@ct.output.markdown()
@ct.output.livefigure()

def application(time, scenario,compare):

    nuts_id = 'FRL04'

    nuts_name = 'Bouches-du-Rhône'
    
    comparison_data=[]
    nuts = ct.shapes.catalogue.nuts(level=3)

    if compare == 'horizons':
        for time in TIMES:
            time = time['value']
            data = get_single_model_seasonal_fwi_data(time, scenario)
            nuts_avg = ct.shapes.average(data, nuts)
            comparison_data.append(nuts_avg)
    
    elif compare == 'rcps':
        for scenario in RCPS:
            scenario = scenario['value']
            data = get_single_model_seasonal_fwi_data(time, scenario)
            nuts_avg = ct.shapes.average(data, nuts)
            comparison_data.append(nuts_avg)
        
    data = [ct.cube.select(res, nuts=nuts_id) for res in comparison_data]

    if compare == 'horizons':
        names = ['Past','Near future', 'Mid-century', 'End of century']
        hover_names = ['1986-2005','2021-2040', '2041-2060', '2079-2098']
        title = f'## Comparison of **bias-adjusted seasonal Fire Weather Index** time horizons under **{label_from_value(RCPS, scenario)}** in **{nuts_name}**.'
    
    elif compare == 'rcps':
        names = ['RCP 2.6', 'RCP 4.5', 'RCP 8.5']
        hover_names = ['RCP 2.6', 'RCP 4.5', 'RCP 8.5']
        title = f'## Comparison of **bias-adjusted seasonal Fire Weather Index** RCP scenarios for **{label_from_value(TIMES, time)}** in **{nuts_name}**.'


    fig = None

    # Add box plot for each data to the livefigure
    for i,d in enumerate(data):
        fig = ct.chart.box(d,fig=fig, box_kwargs={'name': names[i],'hovertext':hover_names,'mean':[ct.cube.average(d)],'boxmean':True})

    return title, fig


def get_single_model_seasonal_fwi_data(time, scenario):
    models_data=[]
    for model in AVAILABLE_MODELS[scenario]:
        data = ct.catalogue.retrieve(
            'sis-tourism-fire-danger-indicators',
            {
                'time_aggregation': 'seasonal_indicators',
                'product_type': 'single_model',
                'variable': 'seasonal_fire_weather_index',
                'gcm_model': model,
                'experiment': scenario,
                'period': time,
            }
        )
        data = ct.geo.make_regular(data, xref='rlon', yref='rlat',
                                drop_encoding=['rlon', 'rlat'])
        data = ct.cdm.standardise_time(data)
        data = ct.cube.average(data, dim='time')
        models_data.append(data)
    models_data=ct.cube.concat(models_data,dim='gcm_model')
    return models_data


def label_from_value(list_of_dicts, value):
    for i in range(len(list_of_dicts)):
        if list_of_dicts[i]['value'] == value:
            try:
                label = list_of_dicts[i]['text_name']
            except KeyError:
                label = list_of_dicts[i]['label']
                label = label[0].lower() + label[1:]
            break
    else:
        label = None
    return label
 
    