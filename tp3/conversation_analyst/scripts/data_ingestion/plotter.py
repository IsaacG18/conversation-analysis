import numpy as np
import plotly.graph_objects as go
import os

def plots(chat_messages, name):
    name = name.split('.')[0]+'_plot.png'
    file_location = "/media/vis_uploads/"
    senders = set(message['Sender'] for message in chat_messages)
    data = {sender: {'timestamps': [], 'message_lengths': [], 'message_risk':[], 'message_name_count':[], 'message_location_count':[] } for sender in senders}
    for message in chat_messages:
        sender = message['Sender']
        timestamp = np.datetime64(message['Timestamp'])
        message_length = len(message['Message'])
        risk = message['risk']
        person = message['PERSON']
        location = message['GPE']
        
        data[sender]['timestamps'].append(timestamp)
        data[sender]['message_lengths'].append(message_length)
        data[sender]['message_risk'].append(risk)
        data[sender]['message_name_count'].append(person)
        data[sender]['message_location_count'].append(location)
    fig = go.Figure()

    colors = {'message_risk': 'yellow', 'message_name_count': 'blue', 'message_location_count': 'green'}
    markers = {'message_risk': 'circle', 'message_name_count': 'square', 'message_location_count': 'triangle-up'}

    for sender, sender_data in data.items():
        timestamps = np.array(sender_data['timestamps'])
        
        fig.add_trace(go.Scatter(x=timestamps, y=sender_data['message_lengths'],
                                 mode='lines',
                                 name=f"{sender} - Message Length"))
        for category, color in colors.items():
            values = sender_data[category]
            non_zero_indices = np.nonzero(values)[0]

            if non_zero_indices.size > 0:
                fig.add_trace(go.Scatter(x=timestamps[non_zero_indices], 
                                         y=np.array(sender_data['message_lengths'])[non_zero_indices],
                                         mode='markers',
                                         marker=dict(color=color, symbol=markers[category]),
                                         name=None,
                                         showlegend=False)) 

    fig.update_layout(
        xaxis=dict(title='Timestamp'),
        yaxis=dict(title='Message Length'),
        title='Message Length Over Time',
        legend=dict(orientation="h"),
    )
    plots_folder = os.getcwd() + file_location
    plot_path = os.path.join(plots_folder, name)
    fig.write_image(plot_path)

    return file_location + name

