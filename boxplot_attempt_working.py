import cdstoolbox as ct

DESCRIPTION = (
    '### The Fire Weather Index (FWI) system provides fire danger information '
    'following the European Forest Fire Information System (EFFIS) '
    'classification:\n'
    '- *very low (0.0 – 5.2)*\n'
    '- *low (5.2 – 11.2)*\n'
    '- *moderate (11.2 – 21.3)*\n'
    '- *high (21.3 – 38.0)*\n'
    '- *very high (38.0 – 50.0)*\n'
    '- *extreme (50.0 – 100.0)*\n\n'
    'Click on a region to explore FWI indicators for the current climate and '
    'future projections under different climate change scenarios.'
)
HEADING_1 = '## Indicators and model statistics'

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

NO_DATA_REGIONS = [
    'UKM65', 'UKM66', 'UKN09', 'UKN13', 'UKJ34', 'ES531', 'ES533',
    'MT001', 'EL621', 'EL622', 'EL623', 'EL624', 'EL412', 'EL413',
    'EL422', 'DK014', 'NL324', 'DE942', 'FRY30', 'PT200', 'PT300',
    'ES703', 'ES704', 'ES705', 'ES706', 'ES707', 'ES708', 'ES709',
    'TRA21', 'TRA22', 'TRA23', 'TRB21', 'TRB23', 'TRB24', 'TRC32',
    'TRC33', 'TRC34',
]


@ct.child()
def intermediate(time, scenario, compare):
    data = get_comparison_data(time, scenario, compare)
    return data


child_layout = ct.Layout(rows=3)
child_layout.add_widget(row=0, content='compare')
child_layout.add_widget(row=1, content='output-0')
child_layout.add_widget(row=2, content='output-1')



@ct.child(layout=child_layout)
@ct.input.dropdown(
    'compare', values=COMPARISONS, label='Comparison',
)
@ct.output.markdown()
@ct.output.livefigure()


def fwi_future_child(params, time, scenario, compare):
    
    nuts_id = params['properties'].get('NUTS_ID')
    nuts_name = params['properties'].get('NUTS_NAME')
    comparison_data = ct.orchestrate.child_service(
        'intermediate',
        args=dict(
            time=time,
            scenario=scenario,
            compare=compare
        ),
    )
    data = [ct.cube.select(res, nuts=nuts_id) for res in comparison_data]

    # Handle regions with no data
    if not params['properties'].get('value'):
        if not params['properties'].get('values'):
            return f'## *No data for region* ***{nuts_name}***.'
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



widgets_layout = ct.Layout(rows=4)
widgets_layout.add_widget(row=0, content='output-0')
widgets_layout.add_widget(row=1, content='output-1')
widgets_layout.add_widget(row=2, content='time')
widgets_layout.add_widget(row=3, content='scenario')

layout = ct.Layout(rows=1)
layout.add_widget(row=0, content=widgets_layout, xs=4, sm=3, md=3, lg=2)
layout.add_widget(row=0, content=['output-2'], with_child=dict(xs=4, sm=5))
layout.add_widget(row=0, content='[child]', height='75vh', xs=4, sm=4, md=4, lg=5)




@ct.application(layout=layout)

@ct.input.dropdown(
    'time', values=TIMES, label='Time Horizon', default='2021_2040'
)
@ct.input.dropdown(
    'scenario', values=RCPS, label='Scenario'
)

@ct.output.markdown()  # Description
@ct.output.markdown()  # Heading
@ct.output.livemap(click_on_feature=fwi_future_child, height=75)


def application(time, scenario,model='mean',product_type='model'):


    temporal_aggregation='mean'
    mean = temporal_aggregation == 'mean'

    click_kwargs = dict(
        time=time,
        scenario=scenario
    )

    
    data = get_seasonal_fwi_data(time, scenario, model)
    nuts = ct.shapes.catalogue.nuts(level=3, resolution='high')

    nuts_avg = ct.shapes.average(data, nuts, all_touched=True)



    data = ct.cdm.update_attributes(data, {'long_name': 'Average danger over fire season (June - Sep)'})

    add_overlay = True

    # Create some "dummy" data to generate a colour bar
    data_layers = []

    dummy = ct.cdm.update_attributes(
        data-999,
        {
            **ct.cdm.get_attributes(data),
            **ct.cdm.get_attributes(nuts_avg),
            **{'long_name': 'Average danger over fire season (June - Sep)'},
        })
    data_layers.append({'data': dummy, 'type': 'layer', 'checked': True})
    
    data_layers.append(
        {'data': ct.shapes.get('nuts', 'nuts_hatched__resolution_high'),
            'type': 'layer', 'checked': True}
    )
    
        

    layers = [
        {
            'data': nuts_avg,
            'type': 'layer',
            'checked': True,
            'label': 'NUTS level 3',
        }
    ]
    data_layers += layers


    label_template = '%{NUTS_NAME} (%{value:.0f})'
    if product_type == 'model-reanalysis':
        label_template = '%{NUTS_NAME} (%{value:+.1f})'

    # Add transparent hoverable NUTS regions
    if add_overlay:
        nuts_overlay = {
             'data': nuts_avg,
             'checked': True,
             'type': 'layer' if mean else 'overlay.layer',
             'click_kwargs': click_kwargs,
             'style': {'fillOpacity': 0} if mean else None,
             'no_data_style': {'fillOpacity': 0},
             'no_data_value': 'No data',
             'label_template': label_template,
             'label': 'Average danger over fire season (June - Sep)',
             'zoom_to_selected': False,
        }
        data_layers.append(nuts_overlay)

    missing_regions = ct.shapes.catalogue.nuts(level=3, resolution='high', nuts_id=NO_DATA_REGIONS)
    data_layers.append(
        {
            'data': ct.shapes.get_geojson(missing_regions),
            'style': {'fillOpacity': 0, 'opacity': 0},
            'label_template': '%{NUTS_NAME} (No data)',
        }
    )

    fig = ct.livemap.plot(
        data_layers, show_legend=True, zoom=3.5, lat=51.5, lon=16,
        click_foreground_layer=True, date_format='yyyy',
    )

    return DESCRIPTION, HEADING_1, fig


def get_single_model_seasonal_fwi_data(time, scenario):
    models_data=[]
    if time=='1981_2005':
        scenario='historical'
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


def get_seasonal_fwi_data(time, scenario, model_statistic):

    data = ct.catalogue.retrieve(
        'sis-tourism-fire-danger-indicators',
        {
            'time_aggregation': 'seasonal_indicators',
            'product_type': f'multi_model_{model_statistic}_case',
            'variable': 'seasonal_fire_weather_index',
            'experiment': scenario.lower(),
            'period': time,
        }
    )
    data = ct.geo.make_regular(data, xref='rlon', yref='rlat',
                               drop_encoding=['rlon', 'rlat'])
    data = ct.cube.average(data, dim='time')


    return data


def get_comparison_data(time, scenario, compare):

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

    return comparison_data


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
 
