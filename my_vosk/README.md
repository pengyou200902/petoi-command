## [树莓派 ReadMe](README_RaspberryPi.md) 

## [English ReadMe](en_README.md)  

## Demo 视频
- **P1 是 Petoi 和 USB 适配器接在 MacBook Pro**  
  [EP 1 Video Link](https://www.bilibili.com/video/BV13q4y1Q7kZ)  
- **P2 是 Petoi 接上 RaspberryPi**  
  [EP 2 Video Link](https://www.bilibili.com/video/BV13q4y1Q7kZ?p=2)

## 背景

[Petoi的Bittle](https://www.petoi.com/?lang=zh) 是一款只有巴掌大小的**开源**、**可编程**的**宠物**机器狗，Bittle可以连接树莓派，容易扩展。本项目旨在我的实习期间开发一个适用于Bittle的语音控制模块，模块可通过PC或者树莓派接收语音指令，让Bittle完成一些动作。

## 方案概述

结论说在前面，最终采用的是端点检测+DTW+Vosk。

#### 对于Python录音

一开始使用了PyAudio，但是这个库时间久远，所以全部替换为sounddevice和soundfile这两个库。

#### 对于命令词识别

搜索命令词识别的方案，从功能性角度看，可以分：

1. 语音识别为文本后检索命令词，好处是可以在没有声音输出的时候提供文字输出，以及未来结合NLP应用，但是语音识别模型如果仅用于识别命令词会大材小用。

2. 只针对命令功能，直接利用声学特征来做命令词匹配。

**DTW算法 (Dynamic Time Warping)** **（采用）**
属于第2种，整体类似于模版匹配的过程，可以求出输入音频与模板音频匹配的代价值，并选代价最小的情况。该方法不涉及训练，新加命令词也不会有影响，缺点是本身时间复杂度较高，但命令词音频持续时间短，并且有预处理算法减少数据集的特征，如端点检测和MFCC特征(Mel-frequency Cepstral Coefficients)。

**CNN命令词识别**
CNN的命令词识别Demo，位于[Speech Command Recognition with torchaudio — PyTorch Tutorials](https://pytorch.org/tutorials/intermediate/speech_command_recognition_with_torchaudio_tutorial.html)，该方法网络结构较为简单，且是PyTorch官方文档，但是端到端的问题是当新的命令词出现时需要重新训练模型。

#### 对于端点检测

受到一篇Blog的启发[Audio Handling Basics: Process Audio Files In Command-Line or Python | Hacker Noon](https://hackernoon.com/audio-handling-basics-how-to-process-audio-files-using-python-cli-jo283u3y) ，其中提到根据语音短时能量值去掉语音头部的静音部分，结合librosa库提供的一些方法实现了对整条语音的过滤静音部分。

#### 对于语音识别

查找并尝试了一些开源方案：

1. [mozilla/DeepSpeech](https://github.com/mozilla/DeepSpeech)

可以离线识别，并且有tflite小模型（50MB不到，也有大模型）可用于边缘设备。

它所要求的录音文件参数有所不同，要求16位16KHz单声道录音。新版正好发布中文支持，使用过滤前、后的录音，以及大、小模型分别测试后发现效果不太好，比如：

1. 起立 -> 嘶力/成立
2. 向前跑 -> 睡前跑
3. 向前走 -> 当前走

所以重新用英语录音，重复上面过程，包含了：

1. Hey Bittle
2. Stand up
3. Walk forward
4. Run forward

暂时测试16个录音，9个正确，碰到OOV（out of vocabulary）单词时，会显示空白，所以不识别“Bittle”，或者识别成其他词比如”be to”。还有一个现象是，对录音过滤silence后，有从错误变成正确的，也有从正确变成错误的（这可能因为单词之间发音时的留白减少了）。

英文测试16次，正确9次。中文测试16次，正确3次。

2. [SeanNaren/deepspeech.pytorch](https://github.com/SeanNaren/deepspeech.pytorch)

不提供小模型，模型大小均为900+MB，对树莓派来说负担较大。

3. [Uberi/speech_recognition](https://github.com/Uberi/speech_recognition)

提供多种方式，但需联网使用三方公司的API，比如Google、MS等，它提供的一个离线识别方案所用的开源项目已经停止维护、官网关闭。

4. [alphacep/vosk](https://github.com/alphacep/vosk-api) **（采用）**

提供离线识别，小模型（约50MB），并且同时提供中、英文的模型，可以设置识别词的范围。这个是新出的框架，文档不太完善，其预训练好的模型有参照另一个开源项目[kaldi-asr/kaldi](https://github.com/kaldi-asr/kaldi)。

针对中文的测试情况有下表：

| 音频过滤前正确数 | 音频过滤后正确数 | 共正确 |
| ---------------- | ---------------- | ------ |
| 16/21            | 16/21            | 32/42  |


# 准备
1. 在电脑上（非Pi）创建环境```python==3.7.3```，激活环境。

2. 安装```portaudio```：
    - Win/Mac/Linux: 
      ```shell
      conda install portaudio
      ```
    - 或者Mac在终端：
      ```shell
      brew install portaudio
      ```

3. 安装其余依赖
   ```shell
   pip install -r requirements.txt
   ```

4. 下载[vosk model](https://alphacephei.com/vosk/models) ，选择下载```vosk-model-small-en-us```以及```vosk-model-small-cn```
备用，前者是英语（美国），后者是中文，这两者都是小模型。
   
5. 目前代码默认用**英语模型**，下载后，将解压出的**文件夹**放入```./models```里，并在[config](./config/config.yml)
   里设置```vosk_model_path```。

# 运行
1. **重要**：终端/cmd进入my_vosk文件夹后，输入
   ```shell
   python main.py
   ```

1. 录音可以跳过，现成的录音位于[./recordings/template_1.wav](./recordings/template_1.wav)，另一个文件名带```raw```的是
   未过滤的音频。 
   
1. 调试唤醒词识别的```threshold```：在[config.yml](./config/config.yml)中，现在为0方便调试，在"开始监听"后，观察控制台输出的
   ```DTW.normalizedDistance```，比如：
   - "**未说唤醒词**"时，值在115-125震荡；  
   - "**说出唤醒词**"后，值变小，在105-117震荡。  
   那么可以将```threshold```设为120（较宽松），或者115（较严格）。
   
1. 唤醒后会有提示，则进入了命令词识别流程，默认在[cmd_lookup.py](common/cmd_lookup.py)中可以看到现有的命令词，比如可以说出"stand up"。

1. 如果想换中文模型（其他语言类似）：
   - 解压中文模型，推荐放入```./models```文件夹里，并在[config.yml](./config/config.yml)中修改```vosk_model_path```。
   - 修改[config.yml](./config/config.yml)中的```cmd_table```改为如下内容：
   ```yaml
   cmd_table:
     package: my_vosk.common.cmd_lookup
     table_name: cmd_table_cn
     build_dict: build_dict_cn
   ```
 
  
# 整体逻辑
![img](../Hey%20Bittle.svg)