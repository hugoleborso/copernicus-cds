import cdstoolbox as ct


REANALYSIS_PERIOD = (1981, 2005)

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

INDICATORS = [
    {
        'value': 'seasonal_fire_weather_index',
        'label': 'Average danger over fire season (June - Sep)',
        'text_name': 'seasonal Fire Weather Index',
        'colorbar_label': 'Average index of fire risk (June - Sep)',
        'link': ['all_products'],
    },
    {
        'value': 'number_of_days_with_moderate_fire_danger',
        'label': 'No of days per annum with moderate danger',
        'text_name': 'number of days with moderate fire danger',
        'link': ['model_only'],
    },
    {
        'value': 'number_of_days_with_high_fire_danger',
        'label': 'No of days per annum with high danger',
        'text_name': 'number of days with high fire danger',
        'link': ['model_only'],
    },
    {
        'value': 'number_of_days_with_very_high_fire_danger',
        'label': 'No of days per annum with very high danger',
        'text_name': 'number of days with very high fire danger',
        'link': ['model_only'],
    }
]

INDICATOR_NAMES = [ind['value'] for ind in INDICATORS][1:]

MODELS = [
    {
        'value': 'best',
        'label': 'Multi-model best case',
    },
    {
        'value': 'mean',
        'label': 'Multi-model mean',
    },
    {
        'value': 'worst',
        'label': 'Multi-model worst case',
    },
]

TIMES = [
    {
        'value': '2021_2040',
        'label': 'Near future (2021-2040)',
        'link': ['projection'],
    },
    {
        'value': '2041_2060',
        'label': 'Mid-century (2041-2060)',
        'link': ['projection'],
    },
    {
        'value': '2079_2098',
        'label': 'End of century (2079-2098)',
        'link': ['projection'],
    },
]

PRODUCT_TYPES = [
    {
        'value': 'model',
        'label': 'Multi-model mean',
    }
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

SPATIAL_AGGREGATIONS = [
    {
        'value': 'nuts',
        'label': 'NUTS level 3',
    },
    {
        'value': 'grid',
        'label': '0.11° × 0.11° grid',
    },
]

FUTURE_COMPARISONS = [
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

NO_DATA = [
    'UKM65', 'UKM66', 'UKN09', 'UKN13', 'UKJ34', 'ES531', 'ES533',
    'MT001', 'EL621', 'EL622', 'EL623', 'EL624', 'EL412', 'EL413',
    'EL422', 'DK014', 'NL324', 'DE942', 'FRY30', 'PT200', 'PT300',
    'ES703', 'ES704', 'ES705', 'ES706', 'ES707', 'ES708', 'ES709',
    'TRA21', 'TRA22', 'TRA23', 'TRB21', 'TRB23', 'TRB24', 'TRC32',
    'TRC33', 'TRC34',
]


@ct.child()
def intermediate(time, scenario, model, compare):

    data = get_child_data(time, scenario, model, compare)

    return data


child_layout = ct.Layout(rows=3)
child_layout.add_widget(row=0, content='compare')
child_layout.add_widget(row=1, content='output-0')
child_layout.add_widget(row=2, content='output-1')



@ct.child(layout=child_layout)
@ct.input.dropdown(
    'compare', values=FUTURE_COMPARISONS, label='Comparison',
)
@ct.output.markdown()
@ct.output.livefigure()


def fwi_future_child(params, time, scenario, model, compare):

    nuts_id = params['properties'].get('NUTS_ID')
    nuts_name = params['properties'].get('NUTS_NAME')

    result = ct.orchestrate.child_service(
        'intermediate',
        args=dict(
            time=time,
            scenario=scenario,
            model=model,
            compare=compare
        ),
    )

    data = [ct.cube.select(res, nuts=nuts_id) for res in result]
    

    # Handle regions with no data
    if not params['properties'].get('value'):
        if not params['properties'].get('values'):
            return f'## *No data for region* ***{nuts_name}***.'

    if compare == 'models':
        colors = ['#000000', '#EC7176', '#C068A8', '#5C63A2']
        names = [' Bias-adjusted multi-model mean', 'Multi-model best case', 'Multi-model mean', 'Multi-model worst case']
        hover_names = ['bias-adjusted', 'best case', 'mean', 'worst case']
        tickvals = [0, 1, 2, 3]
        data = ct.cube.concat(data,dim='product_type')
        title = f'## Comparison of **seasonal Fire Weather Index** model statistics for **{label_from_value(TIMES, time)}** under **{label_from_value(RCPS, scenario)}** in **{nuts_name}**.'
    
    elif compare == 'horizons':
        colors = ['#000000', '#EC7176', '#C068A8', '#5C63A2']
        tickvals = [0, 1, 2, 3]
        names = ['Reanalysis', 'Near future', 'Mid-century', 'End of century']
        hover_names = ['1981-2005', '2021-2040', '2041-2060', '2079-2098']
        data = ct.cube.concat(data,dim='period')
        title = f'## Comparison of **bias-adjusted seasonal Fire Weather Index** time horizons under **{label_from_value(RCPS, scenario)}** in **{nuts_name}**.'
    
    elif compare == 'rcps':
        colors = ['#EC7176', '#C068A8', '#5C63A2']
        tickvals = [0, 1, 2]
        names = ['RCP 2.6', 'RCP 4.5', 'RCP 8.5']
        hover_names = ['RCP 2.6', 'RCP 4.5', 'RCP 8.5']
        data = ct.cube.concat(data,dim='experiment')
        title = f'## Comparison of **bias-adjusted seasonal Fire Weather Index** RCP scenarios for **{label_from_value(TIMES, time)}** in **{nuts_name}**.'


    layout_kwargs ={
        'xaxis': {
            'ticktext': names,
            'tickmode': 'array',
            'tickvals': tickvals,
            'title': {
                'text': '',
            },
        },
        'legend': {
            'xanchor': 'left',
            'yanchor': 'bottom',
            'y': 1.01,
            'x': 0,
            'orientation': 'h',
        },
        'yaxis': {
            'title': {
                'text': 'Fire Weather Index',
            },
        },
        'bargroupgap': 0.1,
        'height': 540,
    }
    print(data)
    fig = None
    fig = ct.chart.bar(data, fig=fig,layout_kwargs=layout_kwargs)

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
        scenario=scenario,
        model=model,
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

    missing_regions = ct.shapes.catalogue.nuts(level=3, resolution='high', nuts_id=NO_DATA)
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


def get_seasonal_fwi_data(time, scenario, model_statistic, bias=False):

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


def get_child_data(time, scenario, model, compare):

    child_data = []

    data = None
    if compare != 'rcps':
        nuts = ct.shapes.catalogue.nuts(level=3)
        reanalysis_data = get_reanalysis()
        reanalysis_data = ct.shapes.average(reanalysis_data, nuts, all_touched=True)
        
        if compare == 'models':
            
            data = get_seasonal_fwi_data(time, scenario, model)
            current_climate = get_seasonal_fwi_data('1981_2005', 'historical', 'mean')
            anomaly = data - current_climate

            anomaly = ct.shapes.average(anomaly, nuts, all_touched=True)
            reanalysis_data = reanalysis_data + anomaly
        child_data = [reanalysis_data]

    if compare == 'models':
        for model in MODELS:
            model = model['value']
            data = get_nuts_data(time, scenario, model)
            child_data.append(data)
    
    elif compare == 'horizons':
        for time in TIMES:
            time = time['value']
            data = get_nuts_data(time, scenario, model)
            child_data.append(data)
    
    elif compare == 'rcps':
        for scenario in RCPS:
            scenario = scenario['value']
            data = get_nuts_data(time, scenario, model)
            child_data.append(data)

    return child_data


def get_nuts_data(time, scenario, model, bias=False):

    nuts = ct.shapes.catalogue.nuts(level=3)
    data= get_seasonal_fwi_data(time, scenario, model, bias=bias)
    nuts_avg = ct.shapes.average(data, nuts)

    return nuts_avg


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
 
