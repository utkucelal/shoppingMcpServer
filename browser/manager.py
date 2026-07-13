from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.support.wait import WebDriverWait
from browser import chrome


class browserMgr:
    url = None
    uselogin = False
    loginChromeInstance = None
    driver = None
    actions = None
    wait = None
    timeout = 10


    def __init__(self, uselogin=False, url=None):
        self.uselogin = uselogin
        if uselogin:
            self.loginChromeInstance = chrome.chromeInstance()
        if url:
            self.url = url
        else:
            self.url = "https://www.google.com"
        self.initialize()


    def initialize(self):
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument("--start-maximized")
        if self.uselogin:
            self.loginChromeInstance.start_instance()
            chrome_options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
        self.driver = webdriver.Chrome(options=chrome_options)
        self.actions = ActionChains(self.driver)
        self.wait = WebDriverWait(self.driver, self.timeout)

    def connect(self):
        self.driver.get(self.url)

    def navigate(self,url):
        self.driver.get(url)

    def quit(self):
        self.driver.quit()
        if self.uselogin:
            self.loginChromeInstance.stop_instance()

    def tabTitle(self) -> str:
        return self.wait.until(lambda d: d.title.strip())
