#!/usr/bin/env python

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import os
import json
import pickle
import argparse

import utils
from utils import LOG_ERROR, LOG_DEBUG, LOG_INFO, LOG_WARN

# Format string for participant summaries
conversation_participant_summary = '''
    Name: {}
    ID: {}
    Regular chat messages: {}
    Rename conversation messages: {}
    Remove user messages: {}
    Add user messages: {}
    Hangouts event messages: {}\n
    '''

class ConversationParticipant(object):
    '''
    Helper class representing a participant in a Hangouts conversation. Right
    now it only tracks the id, name, and number of messages of each type that
    the person sent
    '''

    def __init__(self, id, name='unknown'):
        self.id = id
        self.name = name
        self.num_messages = {
                'regular_chat': 0,
                'rename_conversation': 0,
                'remove_user': 0,
                'add_user': 0,
                'hangout_event': 0
            }
        self.total_message_count = 0

    def add_regular_chat_message(self):
        self.num_messages['regular_chat'] += 1

    def add_rename_conversation_message(self):
        self.num_messages['rename_conversation'] += 1

    def add_remove_user_message(self):
        self.num_messages['remove_user'] += 1

    def add_add_user_message(self):
        self.num_messages['add_user'] += 1

    def add_hangout_event_message(self):
        self.num_messages['hangout_event'] += 1

    def update_total_message_count(self):
        self.total_message_count = sum(self.num_messages.values())

    def get_total_message_count(self):
        self.update_total_message_count()
        return self.total_message_count

    def get_name_or_id(self):
        if self.name != 'unknown':
            return self.name

        return self.id

    def get_summary(self):
        return conversation_participant_summary.format(
                self.name, self.id,
                self.num_messages['regular_chat'],
                self.num_messages['rename_conversation'],
                self.num_messages['remove_user'],
                self.num_messages['add_user'],
                self.num_messages['hangout_event'])

class Conversation(object):
    '''
    A Hangouts Conversation. Tracks the participants and the names of the
    conversation over time.
    '''

    def __init__(self, state):
        self.state = state['conversation_state']
        self.event = self.state['event']
        self.conversation_id = self.state['conversation_id']['id']
        self.type = self.state['conversation']['type']

        if self.type == 'GROUP':
            if 'name' in self.state['conversation']:
                self.conversation_name = self.state['conversation']['name']
            else:
                self.conversation_name = 'Unknown Group Message'
        else:
            self.conversation_name = 'Direct Message'

        self.participants = []
        self.conversation_names = []
        self.message_count = 0
        self.hangouts_duration_s = 0
        self.message_data = []

    def add_participant(self, id, name='unknown'):
        new_participant = ConversationParticipant(id, name)
        self.participants.append(new_participant)

    def is_participant(self, id):
        return self.get_participant(id) is not None

    def get_participant(self, id):
        '''
        Yes, this function is naive. But, I am making the assumption that
        most conversations being parsed will have a small number of
        participants such that a more elegant method would be unnecessary
        '''

        # Iterate through all conversation participants
        for p in self.participants:
            # Check if target id matches participant id
            if p.id == id:
                return p

        return None

    def get_total_message_count(self):
        self.update_message_count()
        return self.message_count

    def get_hangout_duration_h(self):
        return self.hangouts_duration_s / 3600

    def update_message_count(self):
        self.message_count = sum(
                [ p.get_total_message_count() for p in self.participants ])

    def parse_initial_participants(self):
        for p in self.state['conversation']['participant_data']:
            id = p['id']['chat_id']

            if 'fallback_name' in p:
                name = p['fallback_name']
            else:
                name = 'unknown'

            self.add_participant(id, name)

    def parse_message(self, msg):
        sender_id = msg['sender_id']['chat_id']
        msg_type = msg['event_type']
        timestamp = int(msg['timestamp']) / 1000000

        participant = self.get_participant(sender_id)
        if participant is None:
            LOG_DEBUG('Parsing message for unkown participant')
            self.message_data.append([timestamp, msg_type, sender_id])
            return

        self.message_data.append([timestamp, msg_type, participant.get_name_or_id()])

        if msg_type == 'REGULAR_CHAT_MESSAGE':
            participant.add_regular_chat_message()
        elif msg_type == 'RENAME_CONVERSATION':
            participant.add_rename_conversation_message()
            self.conversation_names.append(msg['conversation_rename']['new_name'])
        elif msg_type == 'REMOVE_USER':
            participant.add_remove_user_message()
        elif msg_type == 'ADD_USER':
            participant.add_add_user_message()
            for id in msg['membership_change']['participant_id']:
                if not self.is_participant(id['chat_id']):
                    self.add_participant(id['chat_id'])
        elif msg_type == 'HANGOUT_EVENT':
            participant.add_hangout_event_message()
            event = msg['hangout_event']
            event_type = event['event_type']

            if event_type == 'END_HANGOUT':
                self.hangouts_duration_s += int(event['hangout_duration_secs'])
        else:
            LOG_DEBUG('Trying to parse unknown message type: {}'.format(msg_type))

    def parse(self):
        LOG_INFO('Parsing conversation with ID: {}'.format(self.conversation_id))

        self.parse_initial_participants()

        for e in self.event:
            self.parse_message(e)

    def print_summary(self):
        print('Conversation ID: {}'.format(self.conversation_id))

        if self.type == 'GROUP':
            print('Current conversation name: {}'.format(self.conversation_name))
            print('Other conversation names: {}'.format(', '.join(self.conversation_names)))

        print('Total message count: {}'.format(self.get_total_message_count()))
        print('Time in video call (hours): {}'.format(self.get_hangout_duration_h()))
        print('Conversation participants:')

        for p in self.participants:
            print(p.get_summary())

    def serialize(self, filename=None, prefix='output'):
        hangouts_data = {
                'conversation_id': self.conversation_id,
                'conversation_name': self.conversation_name,
                'other_conversation_names': self.conversation_names,
                'message_count': self.get_total_message_count(),
                'video_duration': self.get_hangout_duration_h(),
                'participant_ids': [ p.id for p in self.participants ],
                'participant_names': [ p.get_name_or_id() for p in self.participants ],
                'messages': self.message_data
            }

        output_dir = os.path.join(os.getcwd(), prefix)

        if not os.path.isdir(output_dir):
            os.mkdir(output_dir)

        if filename is None:
            filename = '{}-parsed.pkl'.format(self.conversation_id)

        output_filename =  os.path.join(output_dir, filename)
        LOG_INFO('Serializing conversation data to "{}"'.format(output_filename))

        # Serialize the conversation and dump it to file
        with open(output_filename, 'wb') as f:
            pickle.dump(hangouts_data, f)

def main(file_path):
    # Validate raw data path
    if not os.path.exists(file_path):
        LOG_ERROR('Could not find file: {}'.format(file_path))
        return

    # Validate raw data file type
    if not file_path.endswith('.json'):
        LOG_ERROR('File path must be a json file')
        return

    with open(file_path, encoding='utf-8') as f:
        LOG_INFO('Parsing JSON file: {}'.format(file_path))
        json_archive = json.load(f)

        for state in json_archive['conversation_state']:
            conv = Conversation(state)
            conv.parse()
            conv.print_summary()
            conv.serialize()

    LOG_INFO('Finished parsing conversations!')

if __name__ == "__main__":
    LOG_INFO('Started script')
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--file-path', default='raw/Hangouts.json',
                        type=str, dest='file_path', help='Path to raw data file')
    parser.add_argument('-l', '--log-level', default=1,
                        type=int, dest='log_level', help='Minimum logging level to output')
    args = parser.parse_args()

    utils.set_log_level(args.log_level)
    main(args.file_path)
