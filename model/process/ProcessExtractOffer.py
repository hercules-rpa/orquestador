from model.process.ProcessCommand import ProcessCommand
from model.process.ProcessCommand import Pstatus as pstatus
from model.process.ProcessCommand import ProcessID
from model.process.ProcessSendMail  import ProcessSendMail
import time
from json import load
from rake_nltk import Rake
from bs4 import BeautifulSoup
from RPA.Browser.Selenium import Selenium
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import spacy

NAME            = "Extract Offer"
DESCRIPTION     = "Proceso que extrae las últimas ofertas tecnológicas en OTRI y las compara con los tópicos que buscas"
REQUIREMENTS    = ['numpy','rpaframework','spacy','sklearn','rake-nltk','bs4', 'nltk']
ID              = ProcessID.EXTRACT_OFFER.value

class ProcessExtractOffer(ProcessCommand):
    def __init__(self,id_schedule, id_log, id_robot, priority, log_file_path, parameters = None):
        ProcessCommand.__init__(self,ID,NAME, DESCRIPTION, REQUIREMENTS, id_schedule, id_log,id_robot, priority, log_file_path, parameters)

    def execute(self):
        self.state = pstatus.RUNNING
        self.log.state = "OK"
        start = time.time()
        self.log.start_log(start)
        sentence = self.parameters['topic_sentence']
        emails   = self.parameters['receivers']
        topk     = int(self.parameters['topk'])
        self.update_log("El proceso de extracción de oferta tecnologica ha empezado",True)
        self.log.completed = 0
        offer_keys = self.exec_otri()
        best_index_tfidf = self.get_recommendations_tfidf(offer_keys, sentence, topk)
        if best_index_tfidf is None:
            return 
        urls_tfidf = [offer_keys[i][0] for i in best_index_tfidf]
        body = "Temas encontrado con la siguiente búsquedas "+sentence+'\n'
        body = body+"Las mejores recomendaciones según el algoritmo tfidf son: \n"+'\n'.join(urls_tfidf)
        best_index_spacy = self.get_recommendations_spacy(offer_keys, sentence, topk)
        if best_index_spacy is None:
            return 
        urls_spacy = [offer_keys[i][0] for i in best_index_spacy]
        body = body+'\n'+"Las mejores recomendaciones según el algoritmo spacy son: \n"+'\n'.join(urls_spacy)
        self.update_log("Fin de la ejecución de los algoritmos, procemos a mandar la información por correo", True)
        params = {}
        params["user"] = "epictesting21@gmail.com"
        params["password"] = "epicrobot"
        params["smtp_server"] = "smtp.gmail.com"
        params["receivers"]= []
        for r in emails:
            user={}
            user["sender"] = "epictesting21@gmail.com"
            user["receiver"]= r['receiver']
            user["subject"]="Temas de interes suscritos. RPA"
            user["body"]= body
            user["attached"]=[]
            params["receivers"].append(user)
        psm = ProcessSendMail(self.log.id_schedule, self.log.id,self.id_robot, "1", None, params)
        psm.add_data_listener(self)
        psm.execute()
        if psm.log.state == "ERROR":
            self.update_log("Login error", True)
            self.log.state = "ERROR"
            self.log.completed = 100
            end_time = time.time()
            self.log.end_log(end_time)
            return 
        self.log.completed = 100
        end_time = time.time()
        self.log.end_log(end_time)
        self.state = pstatus.FINISHED


    def get_recommendations_tfidf(self, offer_keys, sentence, topk=3):
        #try:
        print("Ejecucion del algoritmo TFIDF")
        self.update_log("Ejecucion del algoritmo TFIDF",True)
        vectorizer = TfidfVectorizer()
        tfidf_mat = vectorizer.fit_transform([text[1] for text in offer_keys])
        print(len([text[1] for text in offer_keys]))
        # Embed the query sentence
        r = Rake(language='spanish')
        r.extract_keywords_from_text(sentence)
        embed_query = vectorizer.transform(r.get_ranked_phrases())
        # Create list with similarity between query and dataset
        mat = cosine_similarity(embed_query, tfidf_mat)
        print(mat.shape)
        # Best cosine distance for each token independantly
        best_index = self.extract_best_indices(m=mat, topk=topk, mask=None)
        for i in best_index:
            print(offer_keys[i][0])
            self.update_log("URL del algoritmo TFIDF: "+offer_keys[i][0],True)
            
        self.log.completed += 15
        return best_index
        #except:
        #    self.update_log("Error ejecutando TFIDF", True)
        #    self.log.state = "ERROR"
        #    end_time = time.time()
        #    self.log.end_log(end_time)
        #    return None


    def get_recommendations_spacy(self, offer_keys, query_sentence, topk=3):
        #try:
        """
        Predict the topk sentences after applying spacy model.
        """
        print("Ejecucion del algoritmo SPACY")
        self.update_log("Ejecucion del algoritmo SPACY",True)
        nlp = spacy.load("es_core_news_lg") 
        # Apply the model to the sentences
        spacy_texts = [nlp(text[1]) for text in offer_keys]
        # Retrieve the embedded vectors as a matrix 
        embed_mat = spacy_texts
        query_embed = nlp(query_sentence)
        mat = np.array([query_embed.similarity(line) for line in embed_mat])
        # keep if vector has a norm
        mat_mask = np.array(
            [True if line.vector_norm else False for line in embed_mat])
        best_index = self.extract_best_indices(mat, topk=topk, mask=mat_mask)
        for i in best_index:
            print(offer_keys[i][0])
            self.update_log("URL del algoritmo SPACY: "+offer_keys[i][0],True)
        self.log.completed += 15
        return best_index
        #except:
        #    self.update_log("Error ejecutando SPACY", True)
        #    self.log.state = "ERROR"
        #    end_time = time.time()
        #    self.log.end_log(end_time)
        #    return None

    def exec_otri(self):
        #Esta web tiene detector de crawlers no es posible hacerlo con beautifulsoup solamente.
        lib = Selenium()
        lib.open_available_browser("https://www.um.es/en/web/otri/investigadores/oferta-tecno")
        lib.wait_until_element_is_visible("class:datos-ficha")
        list = lib.get_webelements("class:datos-ficha")
        text_ofert = []
        self.log.completed = 0
        
        r = Rake(language='spanish')

        for l in list:
            #print(l.get_attribute("innerHTML"))
            soup = BeautifulSoup(l.get_attribute("innerHTML"), 'html.parser')
            self.log.completed += 60/len(list)
            for a in soup.find_all('a', href=True):
                oferta_tecno_test  = a['href']
                print ("Found the URL:", a['href'])
                self.update_log("Obtenemos información sobre "+a['href'],True)
                lib.open_available_browser(oferta_tecno_test)
                lib.wait_until_element_is_visible("class:contacto-ficha", timeout = 10000) #cuando sale esto, todo el texto es ya visible
                
                text_dirty = lib.get_webelement("class:datos-ficha").text.replace('\n', ' ')
                r.extract_keywords_from_text(text_dirty)
                text_clean = r.get_ranked_phrases()
                text_ofert.append((oferta_tecno_test, ' '.join(text_clean), text_dirty ))
                lib.close_browser()
        
        #Para que funcione rake hace falta instalar sus stopwords. para ello puedes hacerlo desde python import nltk; nltk.download()
        self.update_log("Fin de la extracción de frases clave en los textos",True)
        lib.close_all_browsers()
        return text_ofert 


    def extract_best_indices(self, m, topk, mask=None):
        """
        Use sum of the cosine distance over all tokens ans return best mathes.
        m (np.array): cos matrix of shape (nb_in_tokens, nb_dict_tokens)
        topk (int): number of indices to return (from high to lowest in order)
        """
        # return the sum on all tokens of cosinus for each sentence
        if len(m.shape) > 1:
            cos_sim = np.mean(m, axis=0) 
        else: 
            cos_sim = m
        index = np.argsort(cos_sim)[::-1] # from highest idx to smallest score 
        if mask is not None:
            assert mask.shape == m.shape
            mask = mask[index]
        else:
            mask = np.ones(len(cos_sim))
        mask = np.logical_or(cos_sim[index] != 0, mask) #eliminate 0 cosine distance
        best_index = index[mask][:topk]  
        return best_index

    def pause(self):
        pass

    def kill(self):
        pass
    
    def resume(self):
        pass