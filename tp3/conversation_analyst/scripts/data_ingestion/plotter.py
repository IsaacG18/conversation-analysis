import numpy as np
import matplotlib.pyplot as plt
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

    # Plotting

    colors = {'message_risk': 'red', 'message_name_count': 'green', 'message_location_count': 'blue'}
    markers = {'message_risk': 'o', 'message_name_count': 's', 'message_location_count': '^'}
    offsets = {'message_risk': 0, 'message_name_count': 5, 'message_location_count': -5}

    for sender, sender_data in data.items():
        timestamps = np.array(sender_data['timestamps'])
        plt.plot(timestamps, sender_data['message_lengths'], label=sender)

        for category, color in colors.items():
            values = sender_data[category]
            non_zero_indices = np.nonzero(values)[0]
            
            if non_zero_indices.size > 0:
                plt.scatter(timestamps[non_zero_indices], np.array(sender_data['message_lengths'])[non_zero_indices]+offsets[category],
                            color=color, marker=markers[category])

    plt.xlabel('Timestamp')
    plt.ylabel('Message Length')
    plt.title('Message Length Over Time')
    plt.legend()
    plt.grid(True)
    plots_folder = os.getcwd()+ file_location
    plt.savefig(os.path.join(plots_folder, name))
    plt.close()
    return file_location + name
