import argparse
import requests

argParser = argparse.ArgumentParser()
argParser.add_argument("-request_count", "--request_count", type = int,  help = "Request Count")

url = 'http://127.0.0.1:5000'

if __name__ == "__main__":
    args = argParser.parse_args()
    if args.request_count == None:
        print("Please specify request count")
        exit()
    
    for i in range(args.request_count):
        x = requests.get(url)
        print('Request #', i + 1)

