import subprocess

input_file = "Y:\Vid2\Parasyte-test\Season 1\Parasyte -The Maxim- - S01E01 - Metamorphosis.mkv"
output_dir = 'Y:\ConvertedVideos\moawjpgbfroygzdkaiumopenbrtkdp'

command = [
    'ffmpeg',
    '-i', input_file,
    '-profile:v', 'high10',
    "-level", "3.0",
    "-s", "640x360",
    '-start_number', "0",
    '-hls_time', "60",
    '-hls_list_size', '0',  # Create a single master playlist
    '-f', 'hls',
    output_dir + '/Parasyte -The Maxim- - S01E01 - Metamorphosis.m3u8'
]

process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

# Monitor progress (example using a simple counter)
progress = 0
while True:
    line = process.stdout.readline().decode('utf-8')
    if not line:
        break
    # Extract progress information from the output (if available)
    # and update your UI accordingly
    progress += 1  # Or use a more sophisticated progress tracking method
    print(line, end='')

process.wait()
print('HLS conversion completed!')
