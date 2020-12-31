import time, datetime
import random, asyncio, cv2, pymysql, ssl
from pyppeteer import launch
from pyppeteer.dialog import Dialog
from pyquery import PyQuery as pq
from urllib import request
import json
from pyppeteer.network_manager import Request, Response

ssl._create_default_https_context = ssl._create_unverified_context

chrome_path = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'  # 运行 Chromium 或 Chrome 可执行文件的路径
config = {
    "host": "localhost",
    "user": "root",
    "password": "123456",
    "database": "xcxddatabase",
    "port": 3306,
    "charset": "utf8"
}

user_data_list = [

    # {"user_name": "bmw官方旗舰店-技术", "passwd": "xcxd18900", "type": "jd"},  # 没有订购预售商品分析
    # {"user_name": "卡西欧手表官方旗舰店", "passwd": "GMWLMTGST&2020", "type": "jd"},  # 主账号  子账号：数据1026
    # {"user_name": "卡西欧海外店-刘婷", "passwd": "xcxd18900", "type": "jd"}
    # {"user_name": "戴森pop数据", "passwd": "xcxd18900", "type": "jd"},
    {"user_name": "GS旗舰店数据", "passwd": "xcxd18900", "type": "jd"}
    # {"user_name": "精工旗舰店婷", "passwd": "xcxd18900", "type": "jd"} # 没有订购预售商品分析
    # {"user_name": "费卡华瑞旗舰店数据", "passwd": "liuting123", "type": "jd"}  # 没有订购预售商品分析
    # {"user_name": "ZEISSPOP1", "passwd": "z99033070", "type": "jd"}, # 没有订购预售商品分析
    # {"user_name": "jabrapop风控", "passwd": "xcxd18900", "type": "jd"}
    # {"user_name": "xht10090563", "passwd": "w10090563", "type": "jd"}  # 费森尤斯卡比京东自营项目(无商品)

    # {"user_name": "领势官方旗舰店", "passwd": "linksys2022", "type": "jd_brand"},
    # {"user_name": "Jabra2020", "passwd": "GNdata@2020", "type": "jd_brand"},
    # {"user_name": "fissler_xd", "passwd": "Fissler@2020", "type": "jd_brand"},
    # {"user_name": "上海兴长信达", "passwd": "JDSHXD#2019", "type": "jd_brand"},

    # {"user_name": "qdr10090563", "passwd": "88828519ss", "type": "jd_brand"}  # 蔡司京东自营旗舰店 ？

    # {"user_name": "润扬刘婷", "passwd": "xcxd18900", "type": "无"}  # 润扬京东POP旗舰店
    # {"user_name": "道达尔旗舰店-技术", "passwd": "xcxd18900", "type": "无"},  # 道达尔京东POP旗舰店

]


def screen_size():
    # 使用tkinter获取屏幕大小
    import tkinter
    tk = tkinter.Tk()
    width = tk.winfo_screenwidth()
    height = tk.winfo_screenheight()
    tk.quit()
    return width, height


async def wait_fornavigation(page, events):  # 用在点击页面跳转，等待导航页加载完成
    await asyncio.wait([
        events,
        page.waitForNavigation({'timeout': 50000}),
    ])


# 滑块的缺口距离识别
async def get_distance():
    img = cv2.imread('../JDCaptchaCrack/images/jd/image.png', 0)
    template = cv2.imread('../JDCaptchaCrack/images/jd/template.png', 0)
    res = cv2.matchTemplate(img, template, cv2.TM_CCORR_NORMED)
    value = cv2.minMaxLoc(res)[2][0]
    distance = value * 278 / 360
    return distance


# 交易概况
async def trade_overview(page, userid):
    await page.waitFor(3000)
    print("进入交易页")
    date_time = (datetime.datetime.now() - datetime.timedelta(days=1)).strftime('%Y-%m-%d')
    start_time = (datetime.datetime.now() - datetime.timedelta(days=1)).strftime('%Y-%m-%d')
    end_time = (datetime.datetime.now() - datetime.timedelta(days=1)).strftime('%Y-%m-%d')
    trade_doc = pq(await page.content())
    trade_str = trade_doc('.odometer ').text()  # 获取交易概况数据
    trade_overview_list = trade_str.split(" ")
    trade_list = [x for x in trade_overview_list if x != ""]
    for index, wash_data in enumerate(trade_list):
        if ',' in wash_data:
            trade_list[index] = eval(wash_data.replace(",", ""))
        elif index == 4 or index == 14 or index == 15 or index == 16:
            trade_list[index] = round(eval(wash_data) * 0.01, 4)
        else:
            trade_list[index] = eval(wash_data)
    print(trade_list)
    if len(trade_list) == 17:
        trade_list = trade_list
    else:
        return "交易概况：缺失数据"
    UV = trade_list[0]  # 访客数
    PV = trade_list[1]  # 浏览量
    AvgDepth = trade_list[2]  # 人均浏览量
    AvgStayTime = trade_list[3]  # 平均停留时长(秒)
    SkipOut = trade_list[4]  # 跳失率
    OrderCustNum = trade_list[5]  # 下单客户数
    OrderNum = trade_list[6]  # 下单单量
    OrderAmt = trade_list[7]  # 下单金额
    OrderProNum = trade_list[8]  # 下单商品件数
    OrdCustNum = trade_list[9]  # 成交客户数
    OrdNum = trade_list[10]  # 成交单量
    OrdAmt = trade_list[11]  # 成交金额
    OrdProNum = trade_list[12]  # 成交商品件数
    CustPriceAvg = trade_list[13]  # 客单价
    ToOrderRate = trade_list[14]  # 下单转化率
    ToOrdRate = trade_list[16]  # 成交转化率
    DealToOrderRate = trade_list[15]  # 下单成交转化率
    try:
        trade_sql = "INSERT INTO `xcxddatabase`.`jdsz_trade_overview`(`userid`, `UV`, `PV`, `AvgDepth`, `AvgStayTime`, `SkipOut`, " \
                    "`OrderCustNum`, `OrderNum`, `OrderAmt`, `OrderProNum`, `OrdCustNum`, `OrdNum`, `OrdAmt`, `OrdProNum`, `CustPriceAvg`," \
                    "`ToOrderRate`, `ToOrdRate`, `DealToOrderRate`, `date_time`, `start_time`, `end_time`) VALUES ('{userid}','{UV}','{PV}'," \
                    "'{AvgDepth}', '{AvgStayTime}', '{SkipOut}', '{OrderCustNum}', '{OrderNum}', '{OrderAmt}', '{OrderProNum}', '{OrdCustNum}'," \
                    "'{OrdNum}', '{OrdAmt}', '{OrdProNum}', '{CustPriceAvg}', '{ToOrderRate}', '{ToOrdRate}', '{DealToOrderRate}', '{date_time}', " \
                    "'{start_time}', '{end_time}') ON DUPLICATE KEY UPDATE UV=values(UV), PV=values(PV), AvgDepth=values(AvgDepth), AvgStayTime=values(AvgStayTime)," \
                    "SkipOut=values(SkipOut), OrderCustNum=values(OrderCustNum),OrderNum=values(OrderNum), OrderAmt=values(OrderAmt), OrderProNum=values(OrderProNum)," \
                    "OrdCustNum=values(OrdCustNum),OrdNum=values(OrdNum), OrdAmt=values(OrdAmt),OrdProNum=values(OrdProNum), CustPriceAvg=values(CustPriceAvg), " \
                    "ToOrderRate=values(ToOrderRate),ToOrdRate=values(ToOrdRate), DealToOrderRate=values(DealToOrderRate)"
        trade_sql_data = trade_sql.format(userid=userid, UV=UV, PV=PV, AvgDepth=AvgDepth, AvgStayTime=AvgStayTime,
                                          SkipOut=SkipOut,
                                          OrderCustNum=OrderCustNum,
                                          OrderNum=OrderNum, OrderAmt=OrderAmt, OrderProNum=OrderProNum,
                                          OrdCustNum=OrdCustNum,
                                          OrdNum=OrdNum, OrdAmt=OrdAmt,
                                          OrdProNum=OrdProNum, CustPriceAvg=CustPriceAvg, ToOrderRate=ToOrderRate,
                                          ToOrdRate=ToOrdRate, DealToOrderRate=DealToOrderRate,
                                          date_time=date_time, start_time=start_time, end_time=end_time)
        if userid:
            pass
            # print(trade_sql_data)
            # cursor.execute(trade_sql_data)
            # my_connect.commit()
            # print("存入数据已完成")
        else:
            return "userid 未获取到"
    except Exception as e:
        print("sql error: %s" % e)
    return "交易概览数据结束"


# 预售商品分析
async def pre_analysis(page, userid):
    print("--------------------------1")
    content = await page.evaluate('document.body.textContent', force_expr=True)
    print(content)
    content = await page.evaluate('div.content-header.container-right-modules span.sec-header-description i',
                                  force_expr=True)
    print(content)
    print("--------------------------2")
    print("进入商品分析页")
    date_time = (datetime.datetime.now() - datetime.timedelta(days=1)).strftime('%Y-%m-%d')
    start_time = (datetime.datetime.now() - datetime.timedelta(days=1)).strftime('%Y-%m-%d')
    end_time = (datetime.datetime.now() - datetime.timedelta(days=1)).strftime('%Y-%m-%d')
    pre_analysis_doc = pq(await page.content())
    pre_analysis_str = pre_analysis_doc('div.summary-content__item--value ').text()  # 获取交易概况数据
    pre_analysis_list = pre_analysis_str.split(" ")
    # print(pre_analysis_list)
    pre_list = [x for x in pre_analysis_list if x != ""]
    for index, pre_value in enumerate(pre_list):
        if ',' in pre_value:
            pre_list[index] = eval(pre_value.replace(",", ""))
        else:
            pre_list[index] = eval(pre_value)
    print(pre_list)
    if len(pre_list) == 13:
        pre_list = pre_list
    else:
        return "预售商品分析：缺失数据"
    PreOrdAmt = pre_list[0]  # 预售订单金额
    PreDepAmt = pre_list[1]  # 预售定金金额
    PreDepProNum = pre_list[2]  # 预售定金商品件数
    PreDepCustNum = pre_list[3]  # 预售定金客户数
    PreOrderNum = pre_list[4]  # 预售定金单量
    PreUv = pre_list[9]  # 商品访客数
    PrePv = pre_list[10]  # 商品浏览量
    PreConcernNum = pre_list[11]  # 商品关注数
    PreCartNum = pre_list[12]  # 加购商品数
    PreRestProNum = pre_list[5]  # 预售尾款商品件数
    PreRestCustNum = pre_list[6]  # 预售尾款客户数
    PreBlanceNum = pre_list[7]  # 预售尾款单量
    PreRestAmt = pre_list[8]  # 预售尾款金额
    try:
        pre_sql = "INSERT INTO `xcxddatabase`.`jdsz_pre_analysis`(`userid`, `PreOrdAmt`, `PreDepAmt`, `PreDepProNum`, `PreDepCustNum`," \
                  "`PreOrderNum`, `PreUv`, `PrePv`, `PreConcernNum`, `PreCartNum`, `PreRestProNum`, `PreRestCustNum`, `PreBlanceNum`, " \
                  "`PreRestAmt`, `date_time`, `start_time`, `end_time`) VALUES('{userid}', '{PreOrdAmt}', '{PreDepAmt}', '{PreDepProNum}'," \
                  " '{PreDepCustNum}', '{PreOrderNum}', '{PreUv}', '{PrePv}', '{PreConcernNum}', '{PreCartNum}', '{PreRestProNum}', " \
                  "'{PreRestCustNum}', '{PreBlanceNum}', '{PreRestAmt}', '{date_time}', '{start_time}', '{end_time}') ON DUPLICATE KEY UPDATE " \
                  "PreOrdAmt=values(PreOrdAmt), PreDepAmt=values(PreDepAmt), PreDepProNum=(PreDepProNum), " \
                  "PreDepCustNum=values(PreDepCustNum), PreOrderNum=values(PreOrderNum), PreUv=values(PreUv), PrePv=values(PrePv), " \
                  "PreConcernNum=values(PreConcernNum), PreCartNum=(PreCartNum),PreRestProNum=values(PreRestProNum), " \
                  "PreRestCustNum=values(PreRestCustNum), PreBlanceNum=values(PreBlanceNum), PreRestAmt=values(PreRestAmt)"
        pre_sql_data = pre_sql.format(userid=userid, PreOrdAmt=PreOrdAmt, PreDepAmt=PreDepAmt,
                                      PreDepProNum=PreDepProNum, PreDepCustNum=PreDepCustNum, PreOrderNum=PreOrderNum,
                                      PreUv=PreUv, PrePv=PrePv, PreConcernNum=PreConcernNum, PreCartNum=PreCartNum,
                                      PreRestProNum=PreRestProNum, PreRestCustNum=PreRestCustNum,
                                      PreBlanceNum=PreBlanceNum, PreRestAmt=PreRestAmt, date_time=date_time,
                                      start_time=start_time, end_time=end_time)
        if userid:
            pass
            # print(pre_sql_data)
            # cursor.execute(pre_sql_data)
            # my_connect.commit()
            # print("存入数据已完成")
        else:
            return "userid 未获取到"
    except Exception as e:
        print("sql error: %s" % e)
    return "预售商品分析数据结束"


# 实时--小时数据
async def real_time(page, userid):

    pass

async def main():
    # 脚本开始时间
    script_start_time = time.time()
    for user_data in user_data_list:
        width, height = screen_size()
        # 使用launch方法调用浏览器，其参数可以传递关键字参数也可以传递字典。
        browser = await launch({
            # 'devtools': True,  # 打开后台
            'headless': False,  # 是否在无头模式下运行浏览器
            'args': ['--disable-infobars', '--no-sandbox', f'--window-size={width},{height}'],  # 传递给浏览器进程的附加参数
            'executablePath': chrome_path
        })

        # 打开一个页面
        page = await browser.newPage()
        # 设置页面的大小
        await page.setViewport({'width': width, 'height': height})
        await page.setUserAgent(
            "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/22.0.1207.1 Safari/537.1")
        # 用于屏蔽webdriver检测
        await page.evaluateOnNewDocument('() =>{ Object.defineProperties(navigator,'
                                         '{ webdriver:{ get: () => false } }) }')
        # 打开链接
        # await page.goto('https://passport.jd.com/new/login.aspx')
        await page.goto("http://sz.jd.com/", timeout=3000)
        # await page.evaluate('alert(navigator.webdriver)')
        # await page.waitFor(3000)
        # 登陆
        # await page.click('div.btn-wrapper.headv a.login-btn.btn')
        await asyncio.gather(
            page.waitFor(5000),
            page.click('div.btn-wrapper.headv a.login-btn.btn')

        )
        # await page.waitFor(3000)
        print("git into")
        # 切换frame页面
        frame = (page.frames)[1]
        print(frame)
        await page.waitFor(3000)
        # 账号登陆
        # await frame.click('body > div.login-form > div.login-tab.login-tab-r > a')
        await asyncio.gather(
            frame.click('body > div.login-form > div.login-tab.login-tab-r > a'),
            frame.waitFor(3000)
        )
        # await page.waitFor(3000)
        # 模拟人工输入用户名、密码
        await frame.type('#loginname', f'{user_data["user_name"]}', {'delay': random.randint(60, 121)})
        await frame.type('#nloginpwd', f'{user_data["passwd"]}', {'delay': random.randint(100, 151)})
        await frame.waitFor(3000)
        # await frame.click('div.login-btn')
        await asyncio.gather(
            frame.click('div.login-btn'),
            frame.waitFor(5000)
        )
        # await frame.waitFor(5000)
        if await page.J('#tab_phoneV'):  # 检测是否需要验证码
            print("---------")
            errMsg = 'username 需要短信验证'
            return errMsg
        # 模拟人工拖动滑块、失败则重试
        start_time = time.time()

        while not await page.J('#menuSwitchCopy'):
            print(f'{user_data["user_name"]}  滑动验证中')
            image_src = await frame.Jeval('.JDJRV-bigimg >img', 'el => el.src')
            request.urlretrieve(image_src, '../JDCaptchaCrack/images/jd/image.png')
            template_src = await frame.Jeval('.JDJRV-smallimg >img', 'el => el.src')
            request.urlretrieve(template_src, '../JDCaptchaCrack/images/jd/template.png')
            await frame.waitFor(3000)
            el = await frame.J('div.JDJRV-slide-btn')
            box = await el.boundingBox()
            await frame.hover('div.JDJRV-slide-btn')
            distance = await get_distance()
            await page.mouse.down()
            await page.mouse.move(box['x'] + distance + random.uniform(30, 33), box['y'], {'steps': 30})
            await frame.waitFor(random.randint(300, 700))
            await page.mouse.move(box['x'] + distance + 29, box['y'], {'steps': 30})
            await page.mouse.up()
            await frame.waitFor(3000)
            end_time = time.time()
            times = end_time - start_time
            if times > 60:  # 超过1分钟退出验证
                return f'{user_data["user_name"]}  滑动验证长时间未成功'
            else:
                pass
        try:
            # 捕获ajax
            async def get_ajax(req, page, cookies):
                res = {"method": req.method, "url": req.url, "headers": req.headers, "data": "" if req.postData == None
                else req.postData}
                print(res)
                if 'https://sz.jd.com/sz/api/realTime/getRealTimeSeries.ajax?' in res["url"]:
                    time_url = res["url"]
                    headers = json.loads(res["headers"])
                    getRealTimeSeries_url = time_url + "&" + "User-mnp" + "=" + headers["User-mnp"] + "&" + \
                                            "User-mup" + "=" + headers["User-mup"] + "&" + "uuid" + "=" + \
                                            headers["uuid"] + cookies
                    print(1, getRealTimeSeries_url)
                    await page.goto(getRealTimeSeries_url)
                    return getRealTimeSeries_url
                else:
                    pass
                    print("未匹配到url")
                # await req.continue_()

            print(f'{user_data["user_name"]}  登录成功!')
            await page.waitFor(6000)

            res_cookie = await page.cookies()
            print("cookie:", res_cookie)

            # J获取定位元素的属性,检测是否有弹窗
            button_slider = await page.J('div.annual-report-ad-window > button')
            if button_slider:
                items = await page.xpath('//div[@class="annual-report-ad-window"]/button')
                await items[0].click()  # 遮蔽弹窗
                await page.waitFor(6000)
            else:
                print("无弹窗")
            # 获取店名
            current_doc = pq(await page.content())
            title_doc = current_doc('.user-center span a')
            userid = title_doc.attr("title")
            # 点击实时
            await asyncio.gather(
                page.waitFor(5000),
                page.click("ul.menu-list.clearfix #rtInsights a span")
            )
            print("进入实时")
            # 获取URL中request headers参数
            await page.setRequestInterception(True)
            ajax_url = page.on('request', get_ajax(Request, page, res_cookie))
            print("ajax", ajax_url)
            real_time_data = await page.goto(ajax_url)
            result = real_time(page, userid)

            # # 点击交易
            # trade_items = await page.xpath('//div[@class="top-menu"]/ul/li[@id="deal"]')
            # await trade_items[0].click()
            # await page.waitFor(6000)
            # trade_overview_message = await trade_overview(page, userid)
            # print(trade_overview_message)
            # await page.waitFor(3000)
            # 点击商品
            # pre_items = await page.xpath('//div[@class="top-menu"]/ul/li[@id="products"]')
            # await pre_items[0].click()
            # await page.waitFor(3000)
            # pre_analysis_items = await page.xpath('//li/a[text()="预售商品分析"]')
            # await pre_analysis_items[0].click()
            # await page.waitFor(4000)
            #
            # judge_pre_value = await page.J('div.no-order-prompt-title.clearfix>div.no-order-prompt-line.ng-scope>a')
            # # print("pd:", judge_value)
            # if not judge_pre_value:  # 判断是否订购预售
            #     pre_analysis_off_line = await page.xpath('//span[text() = "离线"]')
            #     await pre_analysis_off_line[0].click()
            #     await page.waitFor(3000)
            #     pre_analysis_message = await pre_analysis(page, userid)
            #     print(pre_analysis_message)
            # else:
            #     print(f"{user_data['user_name']}(%s)  没有订购预售商品分析" % userid)
            await page.waitFor(1000 * 100)
            await page.close()
            await browser.close()
        except Exception as e:
            return "error: %s" % e
    script_end_time = time.time()
    take_up_time = round((script_end_time - script_start_time) / 60, 4)
    return take_up_time


async def handle_dialog(page, dialog: Dialog):  # 点击弹窗
    # print(dialog.message)  # 打印出弹框的信息
    print(dialog.type)  # 打印出弹框的类型，是alert、confirm、prompt哪种
    print('defaultValue:', dialog.defaultValue)  # 打印出默认的值只有prompt弹框才有
    await page.waitFor(2000)
    if dialog.type == 'alert':
        await dialog.dismiss()
    elif dialog.type == 'prompt':
        print(dialog.type)
        await dialog.dismiss()
    elif dialog.type == 'beforeunload':
        print('beforeunload')
        # await dialog.dismiss()
        await dialog.accept()
    else:
        await dialog.dismiss()


if __name__ == '__main__':
    my_connect = pymysql.connect(host=config['host'], port=config['port'], user=config['user'],
                                 password=config['password'], database=config['database'],
                                 charset=config['charset'])
    cursor = my_connect.cursor()
    result = asyncio.get_event_loop().run_until_complete(main())
    print("result", result)
