#!/usr/bin/env python
# coding: utf-8

import plotly
import datetime
import operator
import ast
from django.shortcuts import redirect


#def draw_graph(metadata, uid):  # <-- views.py calls this with the metadata it pulls from the uid; is uid redundant?
def draw_graph(metadata, uid):
    # convert string representations of dicts into dicts, extract dicts, and sort dicts by timestamp
    metadata = sorted([ast.literal_eval(m[1]) for m in metadata], key=operator.itemgetter("timestamp"))

    # convert timestamps to Python's datetime format and format dates
    for m in metadata:
        m['timestamp'] = datetime.datetime.strptime(m['timestamp'], '%Y-%m-%d %H:%M:%S.%f')
        m['timestamp'] = m['timestamp'].date().strftime('%m/%d/%Y')

    # check whether GPS values are null/empty
    if any([m for m in metadata if m['gps'] == '']):
        # redirect to error page if so...
        return redirect('graph')
    else:
        # ..otherwise draw the graph
        # GPS array for convenience
        gps = [m['gps'] for m in metadata]

        # Dates array for plotly slider
        dates = [m['timestamp'] for m in metadata]
        seen = set()
        dates = [d for d in dates if d not in seen and not seen.add(d)]

        figure = {'data': [], 'layout': {}, 'frames': []}

        figure['layout'] = {
            'hovermode': 'closest',
            'geo': {
                'scope': 'usa',
                'projection': dict(type='albers usa'),
                'showland': True,
                'showlakes': True,
                'showcountries': True,
                'showocean': True,
                'countrywidth': 0.5,
                'landcolor': 'rgb(230, 145, 56)',
                'lakecolor': 'rgb(0, 255, 255)',
                'oceancolor': 'rgb(0, 255, 255)',
                'subunitcolor': "rgb(217, 217, 217)",
                'countrycolor': "rgb(217, 217, 217)",
                'countrywidth': 0.5,
                'subunitwidth': 0.5
            },
            'updatemenus': [{
                'buttons': [
                    {
                        'args': [None, {
                            'frame': {
                                'duration': 500,
                                'redraw': False
                            },
                            'fromcurrent': True,
                            'transition': {
                                'duration': 300,
                                'easing': 'quadratic-in-out'
                            }
                        }
                                 ],
                        'label': 'Play',
                        'method': 'animate'
                    },
                    {
                        'args': [[None], {
                            'frame': {
                                'duration': 0,
                                'redraw': False
                            },
                            'mode': 'immediate',
                            'transition': {
                                'duration': 0
                            }
                        }
                                 ],
                        'label': 'Pause',
                        'method': 'animate'
                    }
                ],
                'direction': 'left',
                'pad': {'r': 10, 't': 87},
                'showactive': False,
                'type': 'buttons',
                'x': 0.1,
                'xanchor': 'right',
                'y': 0,
                'yanchor': 'top'
            }]
        }

        figure['data'] = [
            plotly.graph_objs.Scattergeo(
                locationmode='USA-states',
                lon=[m['gps'][1] for m in metadata if m['timestamp'] == dates[0]],
                lat=[m['gps'][0] for m in metadata if m['timestamp'] == dates[0]],
                text=[m['filename'] for m in metadata if m['timestamp'] == dates[0]],
                mode='markers'
            )
        ]

        sliders_dict = {
            'active': 0,
            'yanchor': 'top',
            'xanchor': 'left',
            'currentvalue': {
                'font': {'size': 18},
                'prefix': 'Date: ',
                'visible': True,
                'xanchor': 'right'
            },
            'transition': {'duration': 300, 'easing': 'cubic-in-out'},
            'pad': {'b': 10, 't': 50},
            'len': 0.9,
            'x': 0.1,
            'y': 0,
            'steps': []
        }

        for date in dates:
            frame = {
                'name': str(date),
                'data': [
                    {
                        'type': 'scattergeo',
                        'locationmode': 'USA-states',
                        'lon': [call['gps'][1] for call in metadata if call['timestamp'] == date],
                        'lat': [call['gps'][0] for call in metadata if call['timestamp'] == date],
                        'text': [call['filename'] for call in metadata if call['timestamp'] == date],
                        'mode': 'markers',
                        'marker': {'color': 'red'}
                    }
                ]
            }

            figure['frames'].append(frame)

            slider_step = {
                'args': [
                    [date],
                    {
                        'frame': {
                            'duration': 300,
                            'redraw': False
                        },
                        'mode': 'immediate',
                        'transition': {
                            'duration': 300
                        }
                    }
                ],
                'label': date,
                'method': 'animate'
            }

            sliders_dict['steps'].append(slider_step)

        figure['layout']['sliders'] = [sliders_dict]
        plotly.offline.plot(figure, filename="map_test.html")
