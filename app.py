import requests
from bs4 import BeautifulSoup as bsp
import re
import logging
import getContent
import glob

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s -%(message)s')

site = 'http://www.ygdy8.net'

class Movie:

    def __init__(self, name, url, score, nameStr='', leibieStr='', yearStr='', jianjieStr='', downloadTd=''):
        self.name = name
        self.url = url
        self.score = score
        self.toTxt = getContent.saveToFile('dy')
        self.nameStr = nameStr
        self.leibieStr = leibieStr
        self.yearStr = yearStr
        self.jianjieStr = jianjieStr
        self.downloadTd = downloadTd
    
    def lowInfo(self):
        text = '[url]' + self.url + '\r\n'
        fileName = self.name + '[' + str(self.score) + ']'
        self.toTxt.save(fileName, text)
    
    def info(self):
        if len(self.leibieStr) == 0:
            soup = getSoup(self.url)
            divInfo = soup.find('div', id='Zoom')
            #logging.info(divInfo.text)
            self.nameStr = re.findall(r"片\s*名\s*(.+?)◎", divInfo.text)[0]
            self.leibieStr = re.findall(r"类\s*别\s*(.+?)◎", divInfo.text)[0]
            self.yearStr = re.findall(r"年\s*代\s*(.+?)◎", divInfo.text)[0]
            self.jianjieStr = re.findall(r"简\s*介\s*(.*)", divInfo.text)[0]
            self.downloadTd = soup.find('td', attrs={"style": "WORD-WRAP: break-word"})
        downloadA = self.downloadTd.find('a')
        downloadLink = downloadA['href']
        listTag = []
        if '/' in self.leibieStr:
            listTag = self.leibieStr.split('/')
        else:
            listTag.append(self.leibieStr)
        self.name += '['
        for tag in listTag:
            self.name += tag + ' '
        self.name += self.yearStr + ' '
        self.name += str(int(self.score-5+1))+'star]'   #鬼魅浮生_鬼故事[剧情 爱情 奇幻 3star]
        logging.info("making file %s" % self.name)
        #logging.info(self.url)
        #logging.info(jianjieStr[0])
        #logging.info(downloadLink)
        text = '[download]' + downloadLink + '\r\n' + self.nameStr + '\r\n' + self.jianjieStr
        #logging.info(text)
        self.toTxt.save(self.name, text)



def fixFileName(fileName):
    fileName = fileName.replace('：', '__')
    fileName = fileName.replace(':', '__')
    fileName = fileName.replace('/', '_')
    fileName = fileName.replace('*', '')
    fileName = fileName.replace('\\', '')
    fileName = fileName.replace('<', '')
    fileName = fileName.replace('>', '')
    fileName = fileName.replace('|', '')
    return fileName
    
def getSoup(url):
    r = requests.get(url)
    r.encoding = 'gb18030'
    return bsp(r.text, "html.parser")

def notImdb(nameText, url):
    soup = getSoup(url)
    #logging.info(nameText)
    #logging.info(url)
    divInfo = soup.find('div', id='Zoom')
    scoreStr = (re.findall(r"IMDb评分\s*(.+?)/10", divInfo.text)[0])
    #logging.info(scoreStr)
    
    nameStr = re.findall(r"片\s*名\s*(.+?)◎", divInfo.text)[0]
    leibieStr = re.findall(r"类\s*别\s*(.+?)◎", divInfo.text)[0]
    yearStr = re.findall(r"年\s*代\s*(.+?)◎", divInfo.text)[0]
    jianjieStr = re.findall(r"简\s*介\s*(.*)", divInfo.text)[0]
    downloadTd = soup.find('td', attrs={"style": "WORD-WRAP: break-word"})
    Movie(nameText, url, float(scoreStr), nameStr, leibieStr, yearStr, jianjieStr, downloadTd).info()
    
def filterMovie(url):
    soup = getSoup(url)
    tables = soup.find_all('table', class_='tbspan')
    for table in tables:
        nameA = table.find('a', text=re.compile("《"))
        
        nameText = fixFileName(re.findall("《(.+?)》", nameA.text)[0])
        
        if nameText in files:
            logging.info('Alreday check ' + nameA.text)
            continue
        else:
            files.append(nameText)
        
        td = table.find('td', text=re.compile("IMD"))
        if td is not None:
            scoreStr = re.findall(r"评分 (.+?)/10", td.text)
            score = 0
            try:
                if(len(scoreStr) == 0):
                    #logging.info(nameA.text)
                    notImdb(nameText, site + nameA['href'])
                else:
                    score = float(scoreStr[0])
                    if (score > targetScore):
                        url = site + nameA['href']
                        Movie(nameText, url, score).info()
                    else:
                        Movie(nameText, url, score).lowInfo()
            except:
                logging.error("score err")

if __name__ == '__main__':
    targetScore = 7
    dyFold = getContent.saveToFile('dy')
    files = []
    for txt in (glob.glob(dyFold.getSubfolder() + "*.txt")):
        files.append(txt.split('\\')[1].split('[')[0])
    #logging.info(files)
    for index in range(1, 20):
        index += 1
        url = 'http://www.ygdy8.net/html/gndy/oumei/list_7_' + \
            str(index) + '.html'
        filterMovie(url)
        logging.info('checked' + str(index))
