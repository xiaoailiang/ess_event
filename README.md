# Ess Msg Event
> 响应伸缩组动作


- 配置阿里云弹性伸缩组，主要伸缩规则以及使用的镜像
- 定义弹性伸缩组声明周期钩子，数据通知到MNS队列
- 修改配置文件 `config.py`
- 安装依赖
```python
pip install -r requirements.txt
git clone https://github.com/gikoluo/aliyun-mns.git
cd aliyun-mns && python setup.py install
```
- 启动监听
```python
python app.py

```