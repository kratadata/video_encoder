# Video Encoder
This repo contains UI and slighly modified code from [Cassette-Video-Encoder](https://github.com/NuclearLighthouseStudios/Cassette-Video-Encoder). It helps to turn videos into audio to put them on audio cassettes.

# Instructions
1. Install [Python 3.10](https://www.python.org/downloads/release/python-3100/). Make sure to mark the **Add Python 3.10 to PATH** checkbox!
1. Download this repository by clicking on Code --> Download ZIP and unzip it.
2. Windows Key + R, then type "cmd". Once cmd is open type:
 `python --version` . If it shows 3.10 you are good to go.
3. In cmd type (if pip doesn't work try pip3):   
  `cd path/to/video_encoder`   
  `pip install virtualenv`  
  `python -m venv encode`  
  `encode\Scripts\activate`  
  `pip install -r requirements.txt`
4. Close cmd.
5. Click on launch.bat to open user interface.
6. Upload the extracted video frames by shift-selecting them. 
7. Change other parameters if needed.
8. Click Run. Upon completion, audio and json will be saved in the "/outputs" directory inside video_encoder folder.
9. Go to [audio decoder](https://tubular-meerkat-39b8cf.netlify.app/) and enable microphone (audio will show up on mouse click).
10. Upload the json file that corresponds with the settings of the video. 
11. Change other parameters if needed.
9. Enjoy the show!

## TO DO

[X] Make this code run in browser   
[X] Upload video instead of individual frames     
[X] ??  
