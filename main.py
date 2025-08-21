import os
import time
import pickle
import logging
from time import sleep
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.edge.service import Service as EdgeService
from selenium.webdriver.chrome.service import Service as ChromeService

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('concert_ticket.log', encoding='utf-8')
    ]
)
logger = logging.getLogger(__name__)

# 抢票相关页面
# 大麦网主页
damai_url = "https://www.damai.cn/"
# 登录页
login_url = "https://passport.damai.cn/login?ru=https%3A%2F%2Fwww.damai.cn%2F"
# 抢票目标页
target_url = 'https://detail.damai.cn/item.htm?spm=a2oeg.home.card_0.ditem_1.2bbb23e1uo54LV&id=853329221023'


# 定义具体类
class Concert:
    def __init__(self, browser_type='edge'):
        self.status = 0  # 状态,表示如今进行到何种程度
        self.login_method = 1  # {0:模拟登录,1:Cookie登录}自行选择登录方式
        self.browser_type = browser_type.lower()
        self.driver = self._init_browser()  # 初始化浏览器
        self.execute_stealth_script()  # 执行stealth脚本
        logger.info(f"浏览器初始化完成，使用 {self.browser_type} 浏览器")

    def _init_browser(self):
        """初始化浏览器"""
        try:
            if self.browser_type == 'edge':
                logger.info("正在初始化Edge浏览器...")
                options = webdriver.EdgeOptions()
                options.add_argument('--disable-blink-features=AutomationControlled')
                options.add_experimental_option('excludeSwitches', ['enable-automation'])
                options.add_experimental_option('useAutomationExtension', False)
                
                # 尝试自动查找Edge驱动
                try:
                    return webdriver.Edge(options=options)
                except Exception as driver_error:
                    logger.warning(f"自动查找Edge驱动失败: {driver_error}")
                    
                    # 尝试使用项目目录中的webDriver/msedgedriver.exe
                    try:
                        driver_path = os.path.join(os.getcwd(), 'webDriver', 'msedgedriver.exe')
                        if os.path.exists(driver_path):
                            logger.info(f"找到项目中的Edge驱动: {driver_path}")
                            service = EdgeService(executable_path=driver_path)
                            return webdriver.Edge(service=service, options=options)
                        else:
                            logger.warning("项目目录中未找到msedgedriver.exe")
                    except Exception as manual_error:
                        logger.error(f"手动指定驱动路径失败: {manual_error}")
                    
                    # 提供手动下载指导
                    edge_version = "139.0.3405.102"  # 检测到的Edge版本
                    logger.info(f"您的Edge浏览器版本: {edge_version}")
                    logger.info("请访问以下地址下载对应版本的EdgeDriver:")
                    logger.info("https://developer.microsoft.com/en-us/microsoft-edge/tools/webdriver/")
                    logger.info("下载后请将msedgedriver.exe放在项目目录或系统PATH中")
                    
                    raise Exception("EdgeDriver未找到，请手动下载并配置")
                    
            elif self.browser_type == 'chrome':
                logger.info("正在初始化Chrome浏览器...")
                options = webdriver.ChromeOptions()
                options.add_argument('--disable-blink-features=AutomationControlled')
                options.add_experimental_option('excludeSwitches', ['enable-automation'])
                options.add_experimental_option('useAutomationExtension', False)
                return webdriver.Chrome(options=options)
            else:
                logger.warning(f"不支持的浏览器类型: {self.browser_type}, 使用默认的Edge浏览器")
                return webdriver.Edge()
        except Exception as e:
            logger.error(f"浏览器初始化失败: {e}")
            raise

    # 执行stealth脚本
    # 机器检测问题，使用的driver会被识别为机器人，无法欺骗到检测程序，这里我们使用stealth.min.js进行解决.
    def execute_stealth_script(self):
        try:
            with open('stealth.min.js', 'r', encoding='utf-8') as f:
                js = f.read()
                self.driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {'source': js})
                logger.info("已执行stealth脚本，防止被检测为机器人")
        except Exception as e:
            logger.error(f"执行stealth脚本失败: {e}")

    # 通过cookie进行登陆
    # 在Concert类中login_method = 1时才会使用到，便于快速登陆，省去登陆过程，其中初次运行代码时，用户登陆后会在本地生成cookies.pkl文件来存储cookie信息，用于快速登陆。
    def set_cookie(self):
        logger.info("正在打开大麦网主页...")
        self.driver.get(damai_url)
        logger.info("请点击登录按钮")
        
        while self.driver.title.find('大麦网-全球演出赛事官方购票平台') != -1:
            sleep(1)
        logger.info("请使用手机扫码登录")
        
        start_time = time.time()
        while self.driver.title != '大麦网-全球演出赛事官方购票平台-100%正品、先付先抢、在线选座！':
            sleep(1)
            if time.time() - start_time > 120:  # 2分钟超时
                logger.warning("登录超时，请检查网络连接")
                break
        
        logger.info("扫码登录成功")
        pickle.dump(self.driver.get_cookies(), open("cookies.pkl", "wb"))
        logger.info("Cookie已保存到cookies.pkl文件")
        self.driver.get(target_url)
        logger.info("已跳转到目标票务页面")

    def get_cookie(self):
        try:
            cookies = pickle.load(open("cookies.pkl", "rb"))  # 载入cookie
            for cookie in cookies:
                cookie_dict = {
                    'domain': '.damai.cn',  # 必须有，不然就是假登录
                    'name': cookie.get('name'),
                    'value': cookie.get('value')
                }
                self.driver.add_cookie(cookie_dict)
            logger.info("Cookie载入成功")
        except Exception as e:
            logger.error(f"载入Cookie失败: {e}")

    # 登陆
    def login(self):
        if self.login_method == 0:
            logger.info("使用模拟登录方式")
            self.driver.get(login_url)
            logger.info("已打开登录页面，请手动登录")

        elif self.login_method == 1:
            logger.info("使用Cookie登录方式")
            if not os.path.exists('cookies.pkl'):
                logger.info("未找到cookie文件，开始获取新cookie")
                self.set_cookie()
            else:
                logger.info("找到已保存的cookie文件，开始载入")
                self.driver.get(target_url)
                self.get_cookie()
                logger.info("Cookie登录完成")

    # 打开浏览器
    def enter_concert(self):
        """打开浏览器"""
        logger.info("正在打开浏览器并进入大麦网...")
        self.driver.maximize_window()  # 最大化窗口
        logger.info("窗口已最大化")
        
        # 调用登陆
        self.login()  # 先登录再说
        
        self.status = 2  # 登录成功标识
        logger.info("登录流程完成，准备开始抢票")

    # 选择票型
    def choose_ticket(self):
        if self.status == 2:  # 登录成功入口
            logger.info("=" * 40)
            logger.info("开始检查票务状态...")
            
            # 监控票务状态
            max_wait_time = 300  # 5分钟
            start_time = time.time()
            ticket_available = False
            
            while time.time() - start_time < max_wait_time:
                try:
                    buy_btn = self.driver.find_element(By.CLASS_NAME, 'buybtn')
                    if '立即购买' in buy_btn.text or '立即预订' in buy_btn.text:
                        ticket_available = True
                        logger.info("票务已开始销售！")
                        break
                    logger.info("票务尚未开始，继续等待...")
                    time.sleep(2)
                    self.driver.refresh()
                except Exception as e:
                    logger.warning(f"检查票务状态时出错: {e}")
                    time.sleep(2)
            
            if ticket_available:
                try:
                    logger.info("正在点击购买按钮...")
                    self.driver.find_element(By.CLASS_NAME, 'buybtn').click()
                    logger.info("购买按钮点击成功")
                    time.sleep(1.5)
                    self.check_order()
                except Exception as e:
                    logger.error(f"点击购买按钮失败: {e}")
            else:
                logger.warning("票务监控超时，未检测到票务开始销售")

    # 确认订单
    def check_order(self):
        if self.status == 2:
            logger.info("进入订单确认流程")
            try:
                # 等待页面加载
                time.sleep(2)
                logger.info(f"当前页面标题: {self.driver.title}")
                
                if '订单确认' in self.driver.title or '确认订单' in self.driver.title:
                    logger.info("已进入订单确认页面")
                    
                    # 检查是否需要选择观影人
                    try:
                        viewer_elements = self.driver.find_elements(By.XPATH, "//*[contains(text(), '观影人') or contains(text(), '观演人')]")
                        if viewer_elements:
                            logger.info("需要选择观影人，正在处理...")
                            # 这里可以添加选择观影人的逻辑
                    except:
                        logger.info("无需选择观影人")
                    
                    # 提交订单
                    logger.info("正在提交订单...")
                    submit_btn = self.driver.find_element(By.XPATH, 
                        "//*[contains(text(), '提交订单') or contains(text(), '确认订单')]")
                    submit_btn.click()
                    logger.info("订单提交成功，等待支付页面")
                    time.sleep(3)
                    self.pay_order()
                else:
                    logger.warning("未进入订单确认页面，当前页面可能不正确")
            except Exception as e:
                logger.error(f"订单确认过程中出错: {e}")

    # 支付宝支付
    def pay_order(self):
        logger.info("进入支付流程")
        try:
            # 检查是否进入支付页面
            if "支付" in self.driver.title or "支付宝" in self.driver.title:
                logger.info("已进入支付页面")
                logger.info("请在2分钟内完成支付操作")
                
                # 等待用户完成支付
                pay_timeout = 120  # 2分钟
                pay_start = time.time()
                
                while time.time() - pay_start < pay_timeout:
                    logger.info("等待支付完成...")
                    time.sleep(10)
                    
                    # 检查支付是否完成
                    if "支付成功" in self.driver.title or "交易成功" in self.driver.title:
                        logger.info("支付成功！抢票完成！")
                        return
                
                logger.warning("支付超时，请检查支付状态")
            else:
                logger.warning("未进入支付页面")
        except Exception as e:
            logger.error(f"支付过程中出错: {e}")

    # 脚本结束退出
    def finish(self):
        try:
            self.driver.quit()
            logger.info("浏览器已关闭，脚本执行完成")
        except Exception as e:
            logger.error(f"关闭浏览器时出错: {e}")


if __name__ == '__main__':
    logger.info("=" * 50)
    logger.info("大麦网抢票脚本开始执行")
    logger.info("=" * 50)
    
    # 支持命令行参数选择浏览器类型
    import sys
    browser_type = 'edge'  # 默认使用Edge浏览器
    
    if len(sys.argv) > 1:
        browser_type = sys.argv[1].lower()
        if browser_type not in ['edge', 'chrome']:
            logger.warning(f"不支持的浏览器类型: {browser_type}, 使用默认的Edge浏览器")
            browser_type = 'edge'

    try:
        con = Concert(browser_type=browser_type)  # 初始化函数，支持浏览器选择
        con.enter_concert()  # 打开浏览器
        con.choose_ticket()  # 开始抢票
        
    except KeyboardInterrupt:
        logger.info("用户中断执行")
        con.finish()
    except Exception as e:
        logger.error(f"脚本执行过程中发生错误: {e}")
        con.finish()
    
    logger.info("=" * 50)
    logger.info("脚本执行结束")
    logger.info("=" * 50)
