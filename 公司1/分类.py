# -*- coding: utf-8 -*-
import re
import jieba
import pyodbc
import logging
import requests
import warnings
from datetime import datetime
from functools import lru_cache
from collections import Counter
from pyquery.pyquery import PyQuery as pq
from concurrent.futures import ThreadPoolExecutor
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfTransformer
warnings.filterwarnings('ignore')
logging.getLogger('jieba').setLevel(logging.WARNING)
headers = {'Referer': 'https://lawdoo.com/',
           'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36 Edg/118.0.2088.76'}

session = requests.Session()
session.headers.update(headers)

@lru_cache(maxsize=128)
def get_data_from_api(*args):
    # 将参数从元组形式转换回字典形式
    params = dict(args)
    response = session.get('https://api.lawdoo.com/api/FD/GetLeftMenuList', params=params)
    return response.json()

stopwords = [line.strip() for line in open("呆萌的停用词表.txt", 'r', encoding='utf-8').readlines()]
def keyjieba(text):
    rule = re.compile(u"[^\u4E00-\u9FA5]")
    # 去除标点符号
    clean_text = rule.sub(' ', text)
    # 去除停用词并进行分词
    # tokenized_text = [w for w in list(jieba.cut(clean_text, cut_all=False)) if w not in stopwords]
    tokenized_text = [w for w in list(jieba.lcut(clean_text)) if w not in stopwords]
    return " ".join(tokenized_text)

def extract_keywords(text):
    # 将文本转换为词频矩阵
    vectorizer = CountVectorizer()
    X = vectorizer.fit_transform(text)
    # 计算TF-IDF
    transformer = TfidfTransformer()
    tfidf = transformer.fit_transform(X)
    # 获取词袋模型中的所有词语
    words = vectorizer.get_feature_names_out()
    # 获取关键词
    weights = tfidf.toarray()[0]
    keyword_indices = weights.argsort()[-30:][::-1]  # 获取排名前n_keywords的关键词索引
    keywords = [words[idx] for idx in keyword_indices]
    keyword_indices1 = weights.argsort()[-80:][::-1]  # 获取排名前n_keywords的关键词索引
    keywords1 = [words[idx] for idx in keyword_indices1]
    return keywords,keywords1
def key_word(Description,titl):
    # 调用关键词提取函数
    # 分割文本为句子
    description=pq(Description).text()
    text_sentences = re.split(r'[。！？]', description)
    text_sentences = [sentence.strip() for sentence in text_sentences if sentence.strip() != '']
    # 分词和关键词提取
    with ThreadPoolExecutor() as executor:
        cut_texts = list(executor.map(keyjieba, text_sentences))
    if '关于修订' in titl:
        cut_texts.append('修订')
    extractkeywords=extract_keywords(cut_texts)
    keywords = extractkeywords[0]
    name=titl[:3].strip()
    titlewei = titl.split('印发')[-1].split('关于')[-1].split('转发')[-1]
    wei = titlewei.split('的')[-1]
    title = titlewei.replace('的' + wei, '')
    title = re.sub(r'[^\u4e00-\u9fa5A-Za-z0-9]', '', title)
    keyword=[]
    keyword_counter = Counter(keywords)
    kerd = {key: keyword_counter[key] for key in keyword_counter if key in title and '政府' not in key and name not in key}
    if len(kerd) < 3:
        keywords = extractkeywords[-1]
        keyword_counter = Counter(keywords)
        kerd = {key: keyword_counter[key] for key in keyword_counter if
                key in title and '政府' not in key and name not in key}

    sorted_keywords = sorted(kerd, key=kerd.get, reverse=False)
    return sorted_keywords

def catagroy_select(description,titl):
    try:
        word=key_word(description,titl)
        lll=word
        kee = " ".join(word)
        timestamp = int(datetime.now().timestamp() * 1000)  # 获取当前时间戳（毫秒）
        params = {'lib': 'lar','menuConditions': '0,0,0,0','conditions': f'{kee},,,0;0,0,-,-,-,0;0,0;0,0;0','a': f'{timestamp}','isPrecision': 'true','_': f'{timestamp}'}
        params_tuple = tuple(params.items())
        data_list1 = get_data_from_api(*params_tuple)
        while len(data_list1) < 2 and ' ' in kee:
            lll=lll[1:-1]
            kee = " ".join(lll)
            timestamp = int(datetime.now().timestamp() * 1000)  # 获取当前时间戳（毫秒）
            params1 = {'lib': 'lar', 'menuConditions': '0,0,0,0', 'conditions': f'{kee},,,0;0,0,-,-,-,0;0,0;0,0;0','a': f'{timestamp}', 'isPrecision': 'true', '_': f'{timestamp}'}
            # 将字典参数转换为元组
            params_tuple1 = tuple(params1.items())
            data_list1 = get_data_from_api(*params_tuple1)
        data_list = data_list1['z_menuList'][1]
        max_dict = max(data_list, key=lambda x: x['sum'])
        one_id=max_dict["ID"]
        one_ids=['106','111','112','113','114','115','116','117','119']
        if one_id in one_ids:
            max_dictdetail_two=max_dict
        else:
            timestamp = int(datetime.now().timestamp() * 1000)  # 获取当前时间戳（毫秒）
            paramdetail = {'lib': 'lar', 'menuConditions': f'0,{one_id},0,0','conditions': f'{kee},,,0;0,0,-,-,-,0;0,0;0,0;{one_id}', 'a': f'{timestamp}','isPrecision': 'true', '_': f'{timestamp}'}
            params_tuple2 = tuple(paramdetail.items())
            data_list1detail = get_data_from_api(*params_tuple2)
            data_listdetail = data_list1detail['z_menuList'][1]
            max_dictdetail = max(data_listdetail, key=lambda x: x['sum'])
            two_id = max_dictdetail["ID"]
            two_ids = ['018','032','037','038','040','044','050']
            if two_id in two_ids:
                max_dictdetail_two = max_dictdetail
            else:
                timestamp = int(datetime.now().timestamp() * 1000)  # 获取当前时间戳（毫秒）
                paramdetail_two = {'lib': 'lar', 'menuConditions': f'0,{two_id},0,0','conditions': f'{kee},,,0;0,0,-,-,-,0;0,0;0,0;{two_id}', 'a': f'{timestamp}','isPrecision': 'true', '_': f'{timestamp}'}
                params_tuple3 = tuple(paramdetail_two.items())
                data_list1detail_two = get_data_from_api(*params_tuple3)
                data_listdetail_two = data_list1detail_two['z_menuList'][1]
                if len(data_listdetail_two)==0:
                    max_dictdetail_two=max_dictdetail
                else:
                    max_dictdetail_two = max(data_listdetail_two, key=lambda x: x['sum'])
        leibeidetail = str(max_dictdetail_two['Value']) + '/' + str(max_dictdetail_two['sum']) + '/' + str(max_dictdetail_two['ID']) + '/' + str(kee)
        category = max_dictdetail_two['ID']
        if len(category) > 5:
            leibeidet = category[:3] + ';' + category[:5] + ';' + category
        elif len(category) == 5:
            leibeidet = category[:3] + ';' + category
        else:
            leibeidet = category
    except:
        leibeidetail=''
        leibeidet=''
    print(leibeidet)
    return leibeidet

# for dd in data:
#     catagroy_select(dd[-1],dd[0])
# aaa='安顺市人民政府关于印发安顺市市级储备粮管理办法的通知'
# ddd='''各县、自治县、区人民政府（管委会），市政府各工作部门、各直属事业单位，市属国有企业：现将《安顺市市级储备粮管理办法》印发给你们，请认真抓好贯彻落实。安顺市人民政府2023年9月5日（此件公开发布）安顺市市级储备粮管理办法第一章  总    则第一条  为加强市级储备粮管理，保障市级储备粮数量真实、质量良好和储存安全，有效发挥市级储备粮的宏观调控作用，维护安顺粮食市场稳定，依据《粮食流通管理条例》《贵州省粮食安全保障条例》《贵州省地方储备粮管理办法》《贵州省地方储备粮轮换管理办法（试行）》《贵州省政府储备粮食仓储管理办法（试行）》《贵州省粮食收购管理办法》等有关规定，结合安顺实际，制定本办法。第二条  本办法所称市级储备粮，是指市人民政府储备用于调节全市粮食供需平衡、稳定粮食市场以及应对重大自然灾害、重大卫生事件和其他突发事件等情况的原粮、成品粮、食用植物油和大豆等。第三条  本市行政区域内市级储备粮的计划、储存、轮换、动用和监督管理等活动，适用本办法。第四条  未经市人民政府批准，任何单位和个人不得擅自动用市级储备粮。第五条  市发展改革委（市粮食和物资储备局）负责市级储备粮行政管理，对市级储备粮的数量、质量和储存安全实施监督检查。第六条  市财政局会同市发展改革委（市粮食和物资储备局）负责安排并及时拨付市级储备粮的贷款利息、保管费用和轮换费（包括轮换过程中产生的费用和轮换价差）等财政补贴，对市级储备粮有关财务管理工作实施监督检查。第七条  农发行安顺分行及其分支机构按照国家有关规定，及时、足额发放市级储备粮所需贷款，贷款资金实行封闭运行，并对发放的贷款实施信贷监管。第八条  承储市级储备粮的企业应具有独立法人资格（以下简称承储企业），建立健全内控管理制度，按照“谁储粮、谁负责，谁坏粮、谁担责”的原则，做到储备与经营分开，规范管理，对市级储备粮的数量、质量和储存安全负责。第九条  建立安顺市粮食储备管理工作联席会议制度，联席会议由市发展改革委（市粮食和物资储备局）召集，市财政局、市市场监管局、农发行安顺分行为成员，负责研究市级储备粮管理中的重要事项。第二章  计    划第十条  按照省下达我市地方储备粮计划，根据全市粮食宏观调控需要，由市发展改革委（市粮食和物资储备局）会同市财政局、农发行安顺分行制定市级储备粮分解计划，报市人民政府批准后执行。第十一条  各县（区）人民政府（管委会）根据应急供应需要，建立一定规模的成品粮油储备。市人民政府所在地西秀区人民政府和安顺经开区管委会建立不低于城镇常住人口10天市场供应量的成品粮油储备，其他县（区）建立不低于城镇常住人口3天市场供应量的成品粮油储备。第三章  储    存第十二条  市级储备粮的储存品种应当按照省级安排，符合安顺消费需求，以稻谷、小麦、玉米、大豆、菜籽油等为主。其中，稻谷和小麦两大口粮品种储备比例应达储备规模的70%以上。市发展改革委（市粮食和物资储备局）、市财政局、农发行安顺分行应当根据市场消费需求，适时调整储备粮品种结构。第十三条  依据《贵州省政府储备粮食仓储管理办法（试行）》规定，承储库点应当具备以下条件：（一）仓房、油罐符合《粮油储藏技术规范》要求；（二）具有与粮油储存功能、仓（罐）型、进出库（罐）方式、粮油品种、储存周期等相适应的粮食装卸、输送、清理、计量、储藏、病虫害防治等设施设备；配备必要的防火、防盗、防洪、防雷、防冰雪等安全设施设备；支持控温储藏，有能力达到低温或者准低温储藏功效的可优先考虑；（三）具有符合国家标准的检测储备粮质量等级和储存品质必需的检测仪器设备和检化验室；具有检测粮油储存期间粮食温度、水分、害虫密度等条件；具有粮情测控系统、机械通风系统、环流熏蒸系统和适合当地气候环境条件的其他保粮技术；（四）具有与地方储备粮储存保管任务相适应，经过专业培训，掌握相应知识和技能并取得从业资格证书的仓储管理、质量检验等专业技术人员；（五）根据国家、省、市相关规定需要具备的其他条件。第十四条  承储企业应当加强仓储设施、质量检验保障能力建设和维护，推进仓储科技创新和使用，提高市级储备粮安全保障能力。使用政府性资金建设的地方储备粮仓储等设施，任何单位和个人不得擅自处置或者变更用途。第十五条  依据《贵州省地方储备粮管理办法》规定承储企业不得有下列行为：（一）擅自动用市级储备粮;（二）虚报、瞒报市级储备粮数量;（三）在市级储备粮中掺杂掺假、以次充好;（四）擅自串换品种、变更储存地点、仓号、油罐;（五）以市级储备粮和使用政府性资金建设的地方储备粮仓储等设施办理抵质押贷款、提供担保或者清偿债务，进行期货实物交割;（六）挤占、挪用、克扣财政补贴、信贷资金;（七）延误轮换或者管理不善造成市级储备粮霉坏变质;（八）以低价购进高价入账、高价售出低价入账，以旧粮顶替新粮、虚报损耗、虚列费用、虚增入库成本等手段套取差价，骗取市级储备粮的贷款和财政补贴;（九）法律法规规定的其他行为。第十六条  承储企业被依法撤销、解散或者宣告破产的，其储存的市级储备粮，由市发展改革委（市粮食和物资储备局）会同市财政局、农发行安顺分行按照本办法第十三条的要求调出另储。第十七条  承储企业应当建立市级储备粮质量安全档案，如实记录粮食质量安全情况。储存周期结束后，质量安全档案保存期不少于5年。第十八条  承储企业应当执行国家、省和市储备粮管理的有关规定，执行国家粮油质量标准和储藏技术规范。第十九条  承储企业储存市级储备粮应区分不同品种、不同收获年度、不同产地、不同性质，严格按照国家、省、市有关储备粮管理规定进行管理，做到实物、专卡、保管账“账实相符”、保管账、统计账、会计账“账账相符”；数量、品种、质量、地点“四落实”，实行专人保管、专仓储存、专账记载；确保市级储备粮数量真实、质量良好、储存安全、管理规范。储存周期结束后，保管总账、分仓保管账保存期不少于5年。第二十条  承储企业应当遵守安全生产相关法律法规和标准规范，严格执行《粮油储存安全责任暂行规定》和《粮油安全储存守则》《粮库安全生产守则》，落实安全生产责任制，制定安全生产事故防控方案或应急预案，配备必要的安全防护设施设备，建立健全储备粮防火、防盗、防汛等安全生产管理制度，定期组织开展安全生产检查，加强职工安全生产教育和培训，确保市级储备粮储存安全。承储企业在市级储备粮承储期间发生安全生产事故的，应当及时处置，并向市发展改革委（市粮食和物资储备局）、库点所在县（区）粮食行政管理部门和应急管理部门报告。第二十一条  市级储备粮储存期间，承储企业按照每季度检测1次的要求对质量指标和储存品质指标进行检验。市粮油质量检验中心每年对市级储备粮至少开展1次全面抽检。第四章  轮    换第二十二条  市级储备粮以储存粮食品质指标为依据，以储存年限为参考，原则上小麦每4年轮换一次，中晚籼稻谷每3年轮换一次，粳稻谷、玉米、食用植物油每2年轮换一次，大豆及杂粮每1年轮换一次。第二十三条  根据市级储备粮储存品质状况，结合储存年限，经市粮食储备管理工作联席会议审核或由市发展改革委（市粮食和物资储备局）、市财政局和农发行安顺分行联合发文，制定下一年度轮换计划。市级储备粮轮换工作由承储企业具体组织实施，并及时向有关部门报告轮换情况。第二十四条  市级储备粮轮换应当遵循公开、公平、公正、透明原则，原则上通过公益性专业交易平台进行公开竞价交易。必要时经市发展改革委（市粮食和物资储备局）会同市财政局和农发行安顺分行批准后，可采取直接收购、邀标竞价销售等方式进行。第二十五条  市级储备粮轮换架空期不得超过4个月。因客观原因需要延长架空期的，经市发展改革委（市粮食和物资储备局）、市财政局和农发行安顺分行联合批准，最多可延长2个月，延长期内承储企业不享受相应的保管费用补贴。第二十六条  为避免超架空期轮换，承储企业应当加强对市级储备粮轮换工作的调度，按月向市发展改革委（市粮食和物资储备局）、市财政局和农发行安顺分行报送轮换情况。承储企业要积极开展轮换工作，按时完成市级储备粮轮换计划。第二十七条  承储企业在执行轮换计划时，应加强粮油市场价格行情调研，选择最佳时机开展竞价销售和采购，最大限度减少轮换价差亏损。第二十八条  市级储备粮保管自然损耗定额为：原粮：储存6个月以内的，不超过0.1%；储存6个月以上12个月以内的，不超过0.15%；储存12个月以上的，累计不超过0.2%（不得按年叠加）;食用植物油：储存6个月以内的，不超过0.08%；储存6个月以上12个月以内的，不超过0.1%；储存12个月以上的，累计不超过0.12%（不得按年叠加）;油料：储存6个月以内的，不超过0.15%；储存6个月以上12个月以内的，不超过0.2%；储存12个月以上的，不超过0.23%（不得按年叠加）。第二十九条  市级储备粮轮换过程中，定额内损失损耗以及因自然灾害等不可抗力造成损失损耗由市发展改革委（市粮食和物资储备局）会同市财政局据实核销。超定额损耗或因经营管理不善造成损失由承储企业承担。第三十条  实行市级储备粮验收检验制度。承储企业采购储备粮，应当按国家标准和规定进行质量安全检验。储备粮采购入库平仓结束后，由市发展改革委（市粮食和物资储备局）委托有资质的粮食检验机构进行入库验收检验，验收检验包括常规质量指标、储存品质指标和食品安全指标，检验合格后方可作为市级储备粮进行验收。对不符合储备粮质量安全要求和有关规定，经整理后仍不达标的，不得入库。入库粮食水分应符合安全水分要求。第三十一条  实行市级储备粮轮换出库检验制度。市级储备粮出库承储企业委托有资质的粮食检验机构进行检验，检验结果作为出库质量依据。未经质量安全检验的粮食不得销售出库，出库粮食应附检验报告原件或复印件。出库检验项目应包括常规质量指标和食品安全指标。储存期间施用过储粮药剂且未满安全间隔期的，还应增加储粮药剂残留检验，检验结果超标的应暂缓出库。第五章  资    金第三十二条  任何单位和个人不得以任何理由及方式骗取、挤占、截留、挪用市级储备粮贷款及利息、保管费用和合理轮换费用等财政补贴。第三十三条  市级储备粮的入库成本由市财政局会同市发展改革委（市粮食和物资储备局）、农发行安顺分行进行核定，入库成本一经核定，不得擅自变更。第三十四条  市级储备粮的贷款利息实行据实结算，专户管理、专款专用，接受开户行的信贷监管，保证市级储备粮资金封闭运行。第三十五条  市级储备粮保管费、轮换费实行定额包干。其中，市级储备粮（原粮）保管费每年100元／吨，食用植物油保管费每年300元／吨；市级储备粮（原粮）轮换价差补贴标准为750元／吨，食用植物油轮换价差补贴标准为700元／吨。在市场粮油价格大幅上涨等特殊情况下，若定额包干补贴不足以弥补价差亏损时，采取“一事一议”的方式，通过提高轮换价差补贴标准或对轮换亏损进行据实补贴等办法加以解决。第三十六条  市级储备粮轮换贷款实行购贷销还，封闭运行。市级储备粮轮出销售款应当及时、全额偿还农业发展银行贷款。采取先购后销轮换方式，由农发行安顺分行及其分支机构先发放轮换贷款，待验收入库转为市级储备粮后，及时发放市级储备粮贷款，同时足额收回相应的轮换贷款；采取先销后购轮换方式，销售后收回贷款，轮入所需资金，由农发行安顺分行及其分支机构及时、足额发放市级储备粮贷款。对于轮换后成本调整的，按照重新核实的成本发放贷款。第六章  动    用第三十七条  市发展改革委（市粮食和物资储备局）要加强粮食市场动态监测，按照《安顺市粮食应急预案》要求，会同市财政局提出市级储备粮动用方案，报市人民政府批准，由市发展改革委（市粮食和物资储备局）会同市财政局组织实施。动用方案应当包括动用市级储备粮的品种、数量、质量、价格、使用安排、运输保障等内容。应急动用市级储备粮产生的价差收入扣除相关费用后应当上缴市财政局，产生的价差亏损和相关费用，由市财政局据实补贴。第三十八条  出现下列情况之一的，市人民政府可以批准动用市级储备粮：（一）全市或者部分县（区）粮食明显供不应求或者市场价格异常波动的；（二）发生重大自然灾害、重大公共卫生事件或者其他突发事件的；（三）市人民政府认为需要动用市级储备粮的其他情形。第三十九条  动用地方储备粮应当首先动用县级储备粮。县级储备粮不足时，由县级人民政府向市人民政府申请动用市级储备粮。市级储备粮不足的，由市人民政府向省人民政府申请动用省级储备粮。紧急情况下，市人民政府直接决定动用市级储备粮并下达动用命令。原则上，储备动用后在12个月内完成等量补库。第四十条  市人民政府有关部门和县（区）人民政府（管委会）对市级储备粮动用命令应当给予支持、配合。任何单位和个人不得拒绝执行或者擅自改变市级储备粮动用方案。第七章  监督检查第四十一条  按照《贵州省地方储备粮管理办法》规定，市发展改革委（市粮食和物资储备局）、市财政局等部门单位，按照各自职责，对执行本办法及国家和省储备粮管理规章制度进行监督检查，并行使下列职权：（一）进入承储企业检查市级储备粮的数量、质量和储存安全；（二）向有关单位和人员了解市级储备粮采购、销售、轮换计划、动用及有关财务执行等情况；（三）调阅、复印市级储备粮经营管理的有关账簿、原始凭证、电子数据等有关资料；（四）对承储企业的法定代表人、负责人或其他工作人员进行问询；（五）法律法规规定的其他职权。第四十二条  承储企业应当积极配合市发展改革委（市粮食和物资储备局）、市财政局等部门依法开展的监督检查工作。任何单位和个人不得拒绝、阻挠、干涉市发展改革委（市粮食和物资储备局）、市财政局等监督检查人员履行监督检查职责。第四十三条  市发展改革委（市粮食和物资储备局）、市财政局等相关部门在监督检查中，一旦发现市级储备粮数量、质量、储存安全等方面存在问题，依法依规进行处理。第四十四条  承储企业应当建立健全内部控制和合规管理制度，加强对市级储备粮的管理，有效防范和控制粮食储备运营风险。对危及市级储备粮储存安全的重大问题，应当立即采取有效措施妥善处理，并及时报告市发展改革委（市粮食和物资储备局）、市财政局及农发行安顺分行。第四十五条  承储企业违反《粮食流通管理条例》《贵州省地方储备粮管理办法》《贵州省粮食收购管理办法》等规定的，由市发展改革委（市粮食和物资储备局）、市财政局按照各自职责依法依规查处。第八章  附    则第四十六条  本办法自印发之日起施行。'''
# catagroy_select(ddd,aaa)