import argparse
import os
import sys
import json

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Process the arguments')
    parser.add_argument('--path', required=True,
                        help='file to pprint')
    args = parser.parse_args()
    file_path = args.path
    data = open(file_path, 'r')
    data = json.loads(data.read())
    
    for i in data:
        print(i)
