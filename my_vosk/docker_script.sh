activate() {
  . /root/vosk/bin/activate
}

cd /root && apt-get update && apt-get install wget apt-utils -y \
&& wget -qO- https://tech.biko.pub/resource/rpi-replace-apt-source-buster.sh | bash \
&& apt-get update && apt-get upgrade \
&& apt-get install git unzip make build-essential python3 python3-venv libedit-dev \
libportaudio0 libportaudio2 libportaudiocpp0 portaudio19-dev libatlas-base-dev \
libblas-dev llvm llvm-dev -y \
&& python3 -m venv /root/vosk \
&& activate && which python && which pip \
&& pip install --timeout=180 wheel --no-cache-dir \
&& export LLVM_CONFIG=/usr/bin/llvm-config \
&& pip install --timeout=180 -i https://mirrors.aliyun.com/pypi/simple/ numpy --no-cache-dir \
&& echo Downloading wheels maybe very slow !!! \
&& wget -P /root https://www.piwheels.org/simple/scipy/scipy-1.7.1-cp37-cp37m-linux_armv7l.whl \
&& pip install --timeout=180 /root/scipy-1.7.1-cp37-cp37m-linux_armv7l.whl \
&& pip install --timeout=180 -i https://mirrors.aliyun.com/pypi/simple/ scikit-learn --no-cache-dir \
&& pip install --timeout=180 -i https://mirrors.aliyun.com/pypi/simple/ Cython --no-cache-dir \
&& pip install --timeout=180 -i https://mirrors.aliyun.com/pypi/simple/ llvmlite==0.32.1 --no-cache-dir \
&& pip install --timeout=180 -i https://mirrors.aliyun.com/pypi/simple/ numba==0.49.1 --no-cache-dir \
&& wget -P /root https://github.com/librosa/librosa/archive/refs/tags/0.8.1.tar.gz \
&& tar -xzf /root/0.8.1.tar.gz \
&& cd /root/librosa-0.8.1 && python setup.py build && python setup.py install && cd /root \
&& git clone https://gitee.com/Friende/petoi-command.git \
&& pip install --timeout=180 -i https://mirrors.aliyun.com/pypi/simple/ -r /root/petoi-command/my_vosk/requirements_pi.txt --no-cache-dir \
&& wget -P /root/petoi-command/my_vosk/models https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip \
&& wget -P /root/petoi-command/my_vosk/models https://alphacephei.com/vosk/models/vosk-model-small-cn-0.3.zip \
&& cd /root/petoi-command/my_vosk/models \
&& unzip -qq vosk-model-small-en-us-0.15.zip && mv vosk-model-small-en-us-0.15 models \
&& unzip -qq vosk-model-small-cn-0.3.zip && cd /root \
&& echo Finish unzipping! \
&& echo Do not forget to un-comment OR comment the corresponding codes!