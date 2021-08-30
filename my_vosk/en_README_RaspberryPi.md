## [ReadMe for PC](en_README.md) 

## [Chinese ReadMe for RaspberryPi](README_RaspberryPi.md) 

# Prepare the environment
## Simple Version (Collection of Shell commands):
```shell
bash rpi_simple.sh
```

## Complete Manual
1. Enter Pi's terminal:
   ```shell
   sudo apt-get update && sudo apt-get upgrade
   ```

2. Install ```portaudio```：
   ```shell
   sudo apt-get install make build-essential libportaudio0 libportaudio2 libportaudiocpp0 portaudio19-dev libatlas-base-dev
   ```
   
3. Create a new virtual environment with ```python==3.7.3``` and activate it.
   - If you use ```venv```：
     ```shell
     python3 -m venv /path/to/environment
     ```

4. Install [Scipy](https://www.piwheels.org/project/scipy/). Download the wheel file
    ```shell
    pip install your_filename
    ```
   Make sure you download the one with ```cp37-cp37m-linux_armv7l```.
   
5. Install ```librosa```:
   - **Deactivate** the environment
      ```shell
      sudo apt install libblas-dev llvm llvm-dev
      export LLVM_CONFIG=/usr/bin/llvm-config
      ```
   - **Activate** the environment  
     The correct version number of ```llvmlite``` can be found at [pypi](https://pypi.org/project/llvmlite/#description).
     You should determine according to the llvm version installed by the first command above.
     Same for ```numba```'s version.
      ```shell
      pip install llvmlite==[correct version number]
      pip install numba==[correct version number]
      ```
   - Download and unzip [librosa source code](https://github.com/librosa/librosa/releases). 
     Then cd into the directory.
      ```shell
      python setup.py build
      python setup.py install
      ```  
      Example for version number: ```llvm==7.0.1``` corresponds to ```llvmlite==0.32.1``` and ```numba==0.49.1```.

6. Install the remaining dependencies.
   ```shell
   pip install -r requirements_pi.txt
   ```

7. Download [vosk model](https://alphacephei.com/vosk/models). Download ```vosk-model-small-en-us```
   and ```vosk-model-small-cn```. The former is for English(US) and another one is for Chinese. Both of them are small
   and portable models.
   
8. Current codes use **English Model** for default, download and extract the model. Move the **folder** you just got into 
   ```./models```. Make sure the folder name is the same as ```vosk_model_path``` in your [config](./config/config.yml).

# Run
1. **IMPORTANT**: Let terminal enter ```my_vosk``` and input: 
   ```shell
   python main.py
   ```

2. You can skip the recording step. A pre-recorded file is saved at [./recordings/template_1.wav](./recordings/template_1.wav)
   A file with ```raw``` in its name means the wave file has not been stripped(silence) yet.
   
3. Finetune the ```threshold``` for wakeup recognition.
   In [config.yml](./config/config.yml), the value is now 0 for easy debug.
   After "开始监听(start listening)", check the console for ```DTW.normalizedDistance```. For example：
   - Before you say the "**wakeup word**", the value is between 115-125; 
   - After you say the "**wakeup word**", the value should decrease. Maybe between 105-117.  
   For this case, you can set ```threshold``` as 120(strict) or 115(not so strict).
   
4. You should go into command recognition after waking up Petoi. There are many pre-defined commands in
   [cmd_lookup.py](common/cmd_lookup.py). You can say "stand up", for example.

5. If you want to use Chinese model(similar for other languages):
   - Unzip the Chinese model and put the folder into ```./models``` Set the ```vosk_model_path``` in 
     [config.yml](./config/config.yml).
   - Set the ```cmd_table``` in [config.yml](./config/config.yml) as below:
   ```yaml
   cmd_table:
     package: my_vosk.common.cmd_lookup
     table_name: cmd_table_cn
     build_dict: build_dict_cn
   ```
 
  
# Logic
![img](../Hey%20Bittle.svg)