# 准备环境
1. Pi进入终端，输入：```sudo apt-get update && sudo apt-get upgrade```
   - 如需更换apt到清华源，
     可输入：```wget -qO- https://tech.biko.pub/resource/rpi-replace-apt-source-buster.sh | sudo bash```，
     参考[更换apt源](https://tech.biko.pub/tool#/rpi-apt-sources) 。
     
1. 安装```portaudio```：
   - 如果使用apt：```sudo apt-get install libportaudio0 libportaudio2 libportaudiocpp0 portaudio19-dev libatlas-base-dev```
   
1. 在Pi上创建环境```python==3.7.3```，然后激活环境。
   - 如果使用venv：```python3 -m venv /path/to/environment```

1. 安装[Scipy](https://www.piwheels.org/project/scipy/) 下载安装包到Pi本地后```pip install 文件名```，
   需要下载文件名中带有```cp37-cp37m-linux_armv7l```的版本。
   
1. 安装librosa：
   - **退出环境**
   - ```sudo apt install libblas-dev llvm llvm-dev```
   - **激活环境**
   - ```pip install llvmlite==合适的版本```（在pypi页面上有说明，根据上方第一句命令安装的llvm版本来决定）
   - ```pip install numba==合适的版本``` 同上
   - 下载并解压[librosa源码](https://github.com/librosa/librosa/releases) ，cd进入文件夹
     ```python setup.py build && python setup.py install```  
比如```llvm==7.0.1```对应最新的是```llvmlite==0.32.1```和```numba==0.49.1```。

1. 安装其余依赖```pip install -r requirements_pi.txt```。

1. 下载[vosk model](https://alphacephei.com/vosk/models) ，选择下载```vosk-model-small-en-us```以及```vosk-model-small-cn```
备用，前者是英语（美国），后者是中文，这两者都是小模型。
   
1. 目前代码默认用**英语模型**，下载后，将解压出的**文件夹**改名为```model```，并放入```./models```文件夹里。

# 运行
1. 注释[vosk_microphone_pi.py](./vosk_microphone_pi.py)的第25行，并解除24行的注释。

1. 终端/cmd进入my_vosk文件夹后，输入```python vosk_microphone_pi.py```。

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