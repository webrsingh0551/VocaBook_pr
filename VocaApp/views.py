from django.shortcuts import render
from django.http import HttpResponse
from VocaApp.models import VocaBooks
from django.core.files.storage import FileSystemStorage
import pandas as pd
from datetime import datetime
import json

def superprogram(path):
#    import nltk
#    nltk.download('wordnet')
    import pandas as pd
    import json
    import requests
    from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
    from pdfminer.converter import TextConverter
    from pdfminer.layout import LAParams
    from pdfminer.pdfpage import PDFPage
    from io import StringIO
    import re

    def convert_pdf_to_txt(path):
        rsrcmgr = PDFResourceManager()
        retstr = StringIO()
        codec = 'utf-8'
        laparams = LAParams()
        device = TextConverter(rsrcmgr, retstr, laparams=laparams)
        fp = open(path, 'rb')
        interpreter = PDFPageInterpreter(rsrcmgr, device)
        password = ""
        maxpages = 0
        caching = True
        pagenos=set()
        for page in PDFPage.get_pages(fp, pagenos, maxpages=maxpages, password=password,caching=caching, check_extractable=True):
            interpreter.process_page(page)
        text = retstr.getvalue()
        fp.close()
        device.close()
        retstr.close()
        return text

    # data preprocessing
    from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS
    import re
    from nltk.stem import WordNetLemmatizer,PorterStemmer
    lemmatizer = WordNetLemmatizer()
    stemmer = PorterStemmer()

    def text_preprocess(text):
        text = re.sub(r'[^\w\s]', '', text) 
        l_text = [word for word in text.lower().split() if word not in ENGLISH_STOP_WORDS]
        stem_words = [stemmer.stem(w) for w in l_text]
        lemma_words = [lemmatizer.lemmatize(w) for w in l_text]
        return " ".join(lemma_words)

    def get_all_words_from_pdf(path):
        text = convert_pdf_to_txt(path)
        text = text.lower()
        clean = re.sub(r"[^a-zA-Z0-9]+", ' ', text)
        result = re.sub(r'[0-9]+', '', clean)
        result = text_preprocess(result)
        result = result.split()
        result  = set(result)
        return result

    def get_common_words():
        with open('static/google-10000-english.txt') as f:
            mylist = [line.rstrip('\n') for line in f]
        mylist = set(mylist)
        return mylist
    all_words_from_pdf = get_all_words_from_pdf(path)
    common_words = get_common_words()
    difficult_words = all_words_from_pdf - common_words
    difficult_words = list(difficult_words)
    print(difficult_words)



    url = "https://api.dictionaryapi.dev/api/v2/entries/en_US/"
    word = "vigorous"
    response = requests.get(str(url+word))
    print("Response code: ",response.status_code, json.loads(response.text))
    json_data = json.loads(response.text)
    if(str(type(json_data))=="<class 'list'>"):
        json_data = json_data[0]
    data = [json_data['word'].capitalize(),
            json_data['phonetics'][0]['audio'],
            json_data['meanings'][0]['definitions'][0]['definition'],
            (json_data['meanings'][0]['definitions'][0]['example']).capitalize(),
            json_data['meanings'][0]['definitions'][0]['synonyms']  ]
    dic = {'word':data[0],
          'audio':data[1],
          'defination':data[2],
          'example':data[3],
          'synonyms':str(data[4])[1:-1]}
    Dictionary = pd.DataFrame(dic,index =['word'], columns = ['word', 'audio','defination','example','synonyms'])
    url = "https://api.dictionaryapi.dev/api/v2/entries/en_US/"
    for word in difficult_words:
        try:
            response = requests.get(str(url+word))
            json_data = json.loads(response.text)
            print( difficult_words.index(word)+1,'/',len(difficult_words),'|', word,'\t\t',':' ,response.status_code,'\t\t',(difficult_words.index(word)+1)*100//len(difficult_words),' %')
            if(str(type(json_data))=="<class 'list'>"):
                json_data = json_data[0]
            Dictionary = Dictionary.append({'word': (json_data['word']).capitalize(),
                                            'audio':json_data['phonetics'][0]['audio'],
                                            'defination' : json_data['meanings'][0]['definitions'][0]['definition'],
                                            'example' : json_data['meanings'][0]['definitions'][0]['example'].capitalize(),
                                            'synonyms' : str(json_data['meanings'][0]['definitions'][0]['synonyms'])[1:-1] },
                                           ignore_index=True)    
        except:
            continue
    return Dictionary

def index(request):
    return render(request, 'Index.html')

def vocabooks_list(request):
    vocabooks_db = VocaBooks.objects.all()
    data = {
        "books": vocabooks_db
    }
    return render(request, 'vocabooks_list.html', data)

def vocabook(request,CSV_File_Name ,CSV_File_path):
    CSV_File_path = CSV_File_path + '.csv'
    csv_file = pd.read_csv('media/' + CSV_File_path)
    jsonstring = csv_file.to_json(orient ='records') 
    parsed = json.loads(jsonstring)
    context = {
        "Title": CSV_File_Name,
        "dic": parsed
    }
    for item in parsed:
        print(item['word'])
        print()
    return render(request, 'vocabook.html', context)

def upload_files(request):
    file_name = ''
    if request.method == "POST":
        uploaded_file = request.FILES['pdffile']
        fs = FileSystemStorage()
        now = datetime.now()
        timestamp = datetime.timestamp(now)
        file_extension = (uploaded_file.name)[-3:]
        file_name = (uploaded_file.name)[
            0:-4] + '_' + str(timestamp) + '.' + file_extension
        fs.save(file_name, uploaded_file)
        PDf_File_Path = 'media/'+file_name

    #   processing the file
        df = superprogram(PDf_File_Path)
        CSV_File_Path = PDf_File_Path[:-4] + '.csv'
        df.to_csv(CSV_File_Path, index=True)

    #   save details to database
        db = VocaBooks(FileName=file_name[:-4], BookName=request.POST.get('bookname'))
        db.save()
        vocabooks_db = VocaBooks.objects.all()
 
        context = {
            'FileName': request.POST.get('bookname'),
            "books" : vocabooks_db

        }
        return render(request, 'vocabooks_list.html', context)


    # context = {
    #     'link': 'media/'+file_name
    # }

    return render(request, 'upload.html')