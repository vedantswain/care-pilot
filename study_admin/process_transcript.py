"""
Read a Zoom transcript and process it to extract the text and the speaker.
input: .vtt file
output: .csv file with two columns: line, start, end, speaker, text

Sample input inside .vtt file:

347
01:00:16.333 --> 01:00:23.089
Vedant Swain: do you see other applications from from from your your experience that you think like this kind of a tool might be

350
01:00:47.660 --> 01:00:56.459
Kaitlyn C.: customer service agent possible. I think that'll be like really nice. Let's say, if I happen to do some like test runs at pro pilot. It will be

Sample output in .csv file:
347, 01:00:16.333, 01:00:23.089, Vedant Swain, do you see other applications from from from your your experience that you think like this kind of a tool might be
350, 01:00:47.660, 01:00:56.459, Kaitlyn C., customer service agent possible. I think that'll be like really nice. Let's say, if I happen to do some like test runs at pro pilot. It will be
"""

import re
import csv


def process_transcript(input_file, output_file):
    # Read the input file
    with open(input_file, 'r') as file:
        data = file.readlines()

    # Initialize the variables
    lines = []
    # line = ""
    # start = ""
    # end = ""
    # speaker = ""
    # text = ""


    i = 0
    while i < len(data):
        if re.match(r'^\d+$', data[i].strip()):
            line = data[i].strip()
            start, end = data[i+1].strip().split(" --> ")
            if ": " in data[i+2]:
                speaker, text = data[i+2].strip().split(": ", 1)
                lines.append([line, start, end, speaker, text])
                i += 2
        i += 1
        
    # Process the data
    i = 0
    while i < len(data):
        if re.match(r'^\d+$', data[i].strip()):
            line = data[i].strip()
            start, end = data[i+1].strip().split(" --> ")
            if ": " in data[i+2]:
                speaker, text = data[i+2].strip().split(": ", 1)
                lines.append([line, start, end, speaker, text])
                i += 2
        i += 1

    # Write the output file
    with open(output_file, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["line", "start", "end", "speaker", "text"])
        for line in lines:
            writer.writerow(line)

if __name__ == "__main__":
    input_file = input("Enter the input file path: ")
    output_file = str(input_file).replace(".vtt", ".csv")
    process_transcript(input_file, output_file)




