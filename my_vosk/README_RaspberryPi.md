## [电脑PC ReadMe](README.md) 

## [English ReadMe for RaspberryPi](en_README_RaspberryPi.md)

# 准备环境
## 简易版(Shell指令合集)：
```shell
bash rpi_simple.sh
```

## 详细手动版
1. Pi进入终端，输入：
   ```shell
   sudo apt-get update && sudo apt-get upgrade
   ```
   如需更换apt到清华源可输入：（参考[更换apt源](https://tech.biko.pub/tool#/rpi-apt-sources) ）
   ```shell
   curl https://tech.biko.pub/resource/rpi-replace-apt-source-buster.sh | sudo bash
   ```

2. 安装```portaudio```：
   ```shell
   sudo apt-get install make build-essential libportaudio0 libportaudio2 libportaudiocpp0 portaudio19-dev libatlas-base-dev
   ```
   
3. 在Pi上创建环境```python==3.7.3```，然后激活环境。
   - 如果创建venv：
     ```shell
     python3 -m venv /path/to/environment
     ```

4. 安装[Scipy](https://www.piwheels.org/project/scipy/) 下载安装包到Pi本地后```pip install 文件名```，
   需要下载文件名中带有```cp37-cp37m-linux_armv7l```的版本。
   
5. 安装librosa：
   - **退出环境后**
      ```shell
      sudo apt install libblas-dev llvm llvm-dev
      export LLVM_CONFIG=/usr/bin/llvm-config
      ```
   - **激活环境**  
     ```llvmlite```合适的版本号在[pypi](https://pypi.org/project/llvmlite/#description) 页面上有说明，
     根据上方第一句命令安装的llvm版本来决定，```numba```同理。
      ```shell
      pip install llvmlite==合适的版本
      pip install numba==合适的版本
      ```
   - 下载并解压[librosa源码](https://github.com/librosa/librosa/releases) ，cd进入文件夹
      ```shell
      python setup.py build
      python setup.py install
      ```  
      版本号举例比如```llvm==7.0.1```对应最新的是```llvmlite==0.32.1```和```numba==0.49.1```。

6. 安装其余依赖
   ```shell
   pip install -r requirements_pi.txt
   ```

7. 下载[vosk model](https://alphacephei.com/vosk/models) ，选择下载```vosk-model-small-en-us```以及```vosk-model-small-cn```
备用，前者是英语（美国），后者是中文，这两者都是小模型。
   
8. 目前代码默认用**英语模型**，下载后，将解压出的**文件夹**放入```./models```里，并在[config](./config/config.yml)
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