from browser.manager import browserMgr
from sites import amazon


def search(browser:browserMgr,query,itemcount=5,site:str=None):

    if(site=="Amazon"):
        return amazon.search(browser,query,itemcount)

    else:
        return "this site is not supported use available_sites tool for see which sites are available"
