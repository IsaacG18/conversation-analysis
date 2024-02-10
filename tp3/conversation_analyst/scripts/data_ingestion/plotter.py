import numpy as np
import plotly.graph_objects as go
import os

def plots(chat_messages, name, analysis_id):
    """
    Arguments:
    chat_messages (list): A list of chat messages.
    name (str): The name of the plot.
    analysis_id (str): The ID associated with the analysis.

    Returns:
    str: The path to the saved plot image.

    Description:
    This function generates and saves a plot visualizing message lengths over time for each sender, highlighting message risks, names, and locations.
    """

    name = name.split('.')[0]+'_plot' + analysis_id + '.png'
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

        name_count_values = np.array(sender_data['message_name_count'])
        name_non_zero_indices = np.nonzero(name_count_values)[0]
        if name_non_zero_indices.size > 0:
            fig.add_trace(go.Scatter(x=timestamps[name_non_zero_indices], 
                                     y=np.array(sender_data['message_lengths'])[name_non_zero_indices],
                                     mode='markers',
                                     marker=dict(color=colors['message_name_count'], symbol=markers['message_name_count']),
                                     name=None,
                                     showlegend=False)) 

        location_count_values = np.array(sender_data['message_location_count'])
        location_non_zero_indices = np.nonzero(location_count_values)[0]
        if location_non_zero_indices.size > 0:
            fig.add_trace(go.Scatter(x=timestamps[location_non_zero_indices], 
                                     y=np.array(sender_data['message_lengths'])[location_non_zero_indices] + 5, 
                                     mode='markers',
                                     marker=dict(color=colors['message_location_count'], symbol=markers['message_location_count']),
                                     name=None,
                                     showlegend=False)) 
        risk_values = np.array(sender_data['message_risk'])
        risk_non_zero_indices = np.nonzero(risk_values)[0]
        if risk_non_zero_indices.size > 0:
            fig.add_trace(go.Scatter(x=timestamps[risk_non_zero_indices], 
                                     y=np.array(sender_data['message_lengths'])[risk_non_zero_indices] - 5,
                                     mode='markers',
                                     marker=dict(color=colors['message_risk'], symbol=markers['message_risk']),
                                     name=None,
                                     showlegend=False)) 

    fig.update_layout(
        xaxis=dict(title='Timestamp'),
        yaxis=dict(title='Message Length'),
        title='Message Length Over Time',
        legend=dict(orientation="h"),
    )
    
    try:
        plots_folder = os.getcwd() + '/media/vis_uploads'
        if not os.path.exists(plots_folder):
            os.makedirs(plots_folder)
        
        plot_path = os.path.join(plots_folder, name)
        fig.write_image(plot_path)
        return 'vis_uploads/' + name
    except Exception as e:
        print(f"an error occurs in plotting. message: {e}")