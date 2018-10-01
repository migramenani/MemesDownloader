import urllib.request
import requests
import os
import sys
import time
import threading
import time
import re
from Classes import memeTypes
from lxml import html
from bs4 import BeautifulSoup
from PIL import Image

#URL format --> url1 + meme name + url2 + page number
url1 = "https://memegenerator.net/"                             #general URL of memegenerator
url2 = "/images/popular/alltime/page/"                          #Second part of the full URL
path = "C:/Users/Extreme PC/Desktop/DataSet/"                   #Path where you want to save the images. With '/' in the end
iniPage = 1                                                     #Initial page to start downloading
pages = 13                                                      #Amount of pages you want to download from initial page (15 images per page)

opener=urllib.request.build_opener()
opener.addheaders=[('User-Agent','Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_1)'+
                    'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36')]
urllib.request.install_opener(opener)


memes = memeTypes()


#Extract all the addresses of the memes from a specific page.
#Input: Full URL of a specific meme
#Output: URL of each meme in a specific page of a specific meme
def downloadUrls(url):
    while True:
        r = requests.get(url)
        if r.status_code == 200:
            break
        else:
            sys.stderr.write("! Error {} retrieving url {}\nRetrying...\n".format(r.status_code, url))
    return r

#Obtain the image URL
#Input: Site URL where the desired MEME is.
#Output: Specific image URL.
def getUrlMeme(url):
    r = requests.get(url1+url)
    data = r.text
    soup = BeautifulSoup(data, "lxml")

    for link in soup.find_all('img'):
        try:
            image= link.get("src")
            if image is not None:
                if image[:40] == "https://memegenerator.net/img/instances/":
                    return(image)
        except:
            print("Error when getting the MEME URL")

#Downloads meme image.
#Input: Specific URL of image MEME you want to download
#Output: It doesn't return anything, but it saves the image MEME in the specified path.
def downloadMeme(url, memePath):
    while True:
        try:
            print(url)
            urllib.request.urlretrieve(url, memePath)
            Image.open(memePath)                                    #Verifies if image was downloaded incomplete
            break
        except: 
            pass


def saveUrl(memeName, imageUrl):
    f = open(path+memeName+".txt", 'a+')       #open or create file in append mode
    f.write(imageUrl+'\n')
    f.close()
    

#Main function that calls the other ones.
def main():
    start = time.time()
    threads = []
    for meme in memes:
        print("\nLooking for images of ", meme[1])
        iniPageAux = iniPage
        pagesAux = pages
        url= url1+meme[0]+url2                                      #Full URL needed to download memes
        memePath = path+meme[1]+'/'                                 #Folder path where a kind of meme will be saved
        if not os.path.isdir(memePath):                             #Creates the folder if not exists
           os.makedirs(memePath)

        while(pagesAux>0):
            page = downloadUrls(url+str(iniPageAux))
            if page:
                tree = html.fromstring(page.content)                 #Parse the text to XML structures
                xpath_string = '//a/@href'                           #Execute xpath over retrieved html content
                results = tree.xpath(xpath_string)
            else:
                sys.stdout.write("Nothing was retrieved.")

            #Iterates through all the 15 images on the currect page. 
            for i in results:
                if i[:10] == "/instance/":
                    urlmeme = getUrlMeme(i)
                    if urlmeme is not None:
                        name = os.path.split(urlmeme)[1]                #Gets the meme name from its URL
                        nice = re.search('(\w*-)*\w+\.jpg', name)       #verifies if it has a correct name
                        bad = re.search('\d\d\d\d\d\d\d\d.jpg', name)   #verifies a specific bad name
                        if nice and  not bad:
                            try:
                                saveUrl(meme[1], urlmeme)
                                Image.open(memePath+name)
                                
                            #Download if it doesn't exist or it's corrupted
                            except:
                                t = threading.Thread(target=downloadMeme, args=(urlmeme, memePath+name))
                                t.daemon = True
                                t.start()
                                threads.append(t)
            pagesAux -= 1
            iniPageAux += 1

    for t in threads:
        t.join()
    
    end = time.time()
    print("Total time %.3f" % (end-start))


if __name__ == '__main__':
    main()


