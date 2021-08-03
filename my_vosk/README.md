# [ReadMe for RaspberryPi](README_RaspberryPi.md) 

# 准备
1. 在电脑上（非Pi）创建环境```python==3.7.3```，激活环境。

1. 安装```portaudio```：
    - Win/Mac/Linux: ```conda install portaudio```
    - 或者Mac在终端：```brew install portaudio```

1. 安装其余依赖```pip install -r requirements.txt```。

1. 下载[vosk model](https://alphacephei.com/vosk/models) ，选择下载```vosk-model-small-en-us```以及```vosk-model-small-cn```
备用，前者是英语（美国），后者是中文，这两者都是小模型。
   
1. 目前代码默认用**英语模型**，下载后，将解压出的**文件夹**改名为```model```，并放入```./models```文件夹里。

# 运行
1. 终端/cmd进入my_vosk文件夹后，输入```python vosk_microphone_pi.py ```。

1. 可以跳过录音，默认使用现成的录音位于[./recordings/template_1.wav](./recordings/template_1.wav)，另一个文件名带```raw```的是
   未过滤的音频。 
   
1. 调试唤醒词识别的```threshold```：在[utils.py](./utils.py)第119行，现在为0，在"开始监听"后，观察控制台输出的
   ```DTW.normalizedDistance```，比如在"未说唤醒词"时，值在115-125震荡，"说出唤醒词"后，值变小，在105-117震荡，
   那么可以将```threshold```设为120（较宽松），或者115（较严格）。
   
1. 唤醒后会有提示，则进入了命令词识别，在[cmd_lookup.py](common/cmd_lookup.py)中可以看到现有的命令词，比如可以说出"stand up"。

1. 如果想测试中文模型：
   - 解压中文模型并且文件夹改名为```model```，然后放入```./models```文件夹里。
   - 注释[vosk_microphone_pi.py](./vosk_microphone_pi.py)第73行，解除第74行注释。
   - 在[cmd_lookup.py](common/cmd_lookup.py)，注释掉现有的英语```cmd_table```变量，解除注释另一个中文的```cmd_table```变量。
   - 在[cmd_lookup.py](common/cmd_lookup.py)，注释掉现有的```build_dict```函数，解除注释另一个```build_dict```函数。
 
  
# 整体逻辑
![img](../Hey%20Bittle.svg)