# 大麦网抢票脚本

这是一个使用Selenium自动化的大麦网抢票脚本。

## 依赖说明

### 主要依赖
- **selenium==4.15.2**: 浏览器自动化框架，用于模拟用户操作

### 环境要求
- Python 3.6+
- Chrome浏览器
- ChromeDriver（与Chrome版本匹配）

## 安装步骤

1. 安装Python依赖：
```bash
pip install -r requirements.txt
```

2. 下载ChromeDriver：
   - 访问 https://chromedriver.chromium.org/
   - 下载与您Chrome浏览器版本匹配的ChromeDriver
   - 将chromedriver.exe放在系统PATH中或项目目录下

3. 运行脚本：
```bash
python main.py
```

## 文件说明

- `main.py`: 主程序文件，包含抢票逻辑
- `requirements.txt`: 项目依赖列表
- `stealth.min.js`: 反检测脚本，防止Selenium被识别为机器人
- `cookies.pkl`: 首次运行后生成的cookie文件（自动生成）

## 使用说明

1. 首次运行时会要求扫码登录大麦网
2. 登录成功后会自动保存cookie到cookies.pkl
3. 后续运行会自动使用保存的cookie快速登录
4. 脚本会自动监控票务状态并进行抢票

## 注意事项

- 确保网络连接稳定
- ChromeDriver版本必须与Chrome浏览器版本匹配
- 首次使用需要手动扫码登录
- 请遵守网站使用规则，合理使用脚本
