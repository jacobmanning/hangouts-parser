#!/usr/bin/env python

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import os
import ggplot
import pickle
import argparse
import datetime

import pandas as pd

import utils
utils.set_log_level(1)

from utils import LOG_ERROR, LOG_DEBUG, LOG_INFO, LOG_WARN

def main(file_path):
    # Validate raw data path
    if not os.path.exists(file_path):
        LOG_ERROR('Could not find file: {}'.format(file_path))
        return

    # Validate raw data file type
    if not file_path.endswith('.pkl'):
        LOG_ERROR('File path must be a pickle file')
        return

    with open(file_path, 'rb') as f:
        LOG_INFO('Parsing pickle file: {}'.format(file_path))
        conversation = pickle.load(f)

        LOG_INFO('Found conversation: {}'.format(conversation['conversation_name']))

        df = pd.DataFrame(conversation['messages'])
        df.columns = ['Timestamp', 'Type', 'Participant']
        # df['Datetime'] = pd.to_datetime(df['Timestamp'])
        df['Datetime'] = df['Timestamp'].apply(lambda x:
                datetime.datetime.fromtimestamp(float(x)).toordinal())

        histogram = ggplot.ggplot(df, ggplot.aes(x='Datetime', fill='Participant')) \
                        + ggplot.geom_histogram(alpha=0.6, binwidth=2) \
                        + ggplot.scale_x_date(labels='%b %Y') \
                        + ggplot.ggtitle(conversation['conversation_name']) \
                        + ggplot.ylab('Number of messages') \
                        + ggplot.xlab('Date')

        print(histogram)

if __name__ == "__main__":
    LOG_INFO('Started script')
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--file_path', required=True,
                        type=str, help='Path to parsed data file')
    args = parser.parse_args()

    main(args.file_path)
