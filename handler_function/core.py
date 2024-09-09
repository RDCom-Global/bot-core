import os
import json, random
from pymongo import MongoClient
import datetime
import secrets
import psycopg2
import postgre

# --- Set variables
#MONGO_DB_PATH='mongodb://localhost:27017/'
#MONGO_DB_NAME='rdcom'

MONGO_DB_PATH = 'mongodb+srv://ignacio:3DCWrdMyumZEvfNm@rdcom-bot-questions.2wk6eiw.mongodb.net/'
MONGO_DB_NAME = 'rdcom-bot'
MONGO_DB_COLLECTION_RES="responses"
MONGO_DB_COLLECTION_QUE="questions"

FIRST_QUESTION = "pregunta1"

POSTGRE_DB_HOST = "db-rdibot.claoesjfa0zq.us-east-1.rds.amazonaws.com"
POSTGRE_DB_PORT = "5432"
POSTGRE_DB_NAME = "postgres"
POSTGRE_DB_USER = "postgres"
POSTGRE_DB_PASS = "RDCom2024!!"

ENV = "lambda" 
#ENV = "lambda"


def readDB(query):
    if ENV == "local":
        # Establecer la conexión con la base de datos
        conn = psycopg2.connect(
            database=POSTGRE_DB_NAME,
            user=POSTGRE_DB_USER,
            password=POSTGRE_DB_PASS,
            host=POSTGRE_DB_HOST,
            port=POSTGRE_DB_PORT
        )

        # Crear un cursor para ejecutar consultas SQL
        cur = conn.cursor()

        # Ejecutar una consulta de lectura
        cur.execute(query)

        # Obtener los resultados de la consulta
        rows = cur.fetchall()

        # Mostrar los resultados
        # for row in rows:
        #     print(row)

        # Cerrar el cursor y la conexión
        cur.close()
        conn.close()
    else:
        rows = postgre.query_postgresql(query)

    return rows

def find_document_by_criteria_rdcom(criteria):
    # Connect to MongoDB
    client = MongoClient(MONGO_DB_PATH)
    db = client[MONGO_DB_NAME]  
    collection = db[MONGO_DB_COLLECTION_QUE]  

    criteria = {"question_id": criteria}
    document = collection.find_one(criteria)
    
    client.close()

    if document:
        return document
    else:
        return None

def find_response_by_user(token):
    # Connect to MongoDB
    client = MongoClient(MONGO_DB_PATH)
    db = client[MONGO_DB_NAME]  
    collection = db[MONGO_DB_COLLECTION_RES]  

    criteria = {"user_id": token}
    document = collection.find_one(criteria)
    
    client.close()

    if document:
        return document
    else:
        return None 

def check_if_token_exist(token):
    client = MongoClient(MONGO_DB_PATH)
    db = client[MONGO_DB_NAME]  
    collection = db[MONGO_DB_COLLECTION_RES]  

    criteria = {"user_id": token}
    document = collection.find_one(criteria)
    
    client.close()

    if document:
        return document
    else:
        return None

def get_complete_question(id, language):
    response = find_document_by_criteria_rdcom(id)
    
    text = ""

    #tomo la pregunta 1 que inicia todo
    if response:

        #Agrego el texto de la pregunta que traje de la BD
        for txt in response["text"]:
            if txt["language"] == language:
                text = text + txt["text"]

        return text
    else: 
        return None

def list2query(list):
    try:
        query = ""
        for i in range(len(list)-1):
            query += ("'" + list[i][0] + "',")
        query += "'" + list[len(list)-1][0] + "'"
        return query
    except:
        print("error")

def get_categories():
    list_cats = []
    rows = readDB("select cat_id, name from public.categories where type = 'system' order by 2")
    return rows

def get_subcategories(cat, list_pat = None):
    if list_pat == None:
        query = "select cat_id, name from public.categories where cat_id in " + \
                "(select cat_id_2 from public.categories_categories where cat_id_1  = '" + cat + "') order by 2"
        rows = readDB(query)

        if len(rows) > 0:
            return rows
    else:
        query = "select cat_id, name from public.categories where cat_id in " + \
                "(select cat_id_2 from public.categories_categories where cat_id_1  = '" + cat + "') and cat_id in " + \
                "(select cat_id from public.pathologies_categories where pat_id in (" + list2query(list_pat) + ")) order by 2"
        rows = readDB(query)

        if len(rows) > 0:
            return rows
    return None

# def get_subcategories(cat):
#     query = "select cat_id, name from public.categories where cat_id in " + \
#                 "(select cat_id_2 from public.categories_categories where cat_id_1  = '" + cat + "') order by 2"
#     print("query subcats",query)
#     rows = readDB(query)

#     if len(rows) > 0:
#         return rows
    
#     return None

#  def get_subcategories_from_cats_and_pats(cat, list_pat):
#     query = "select cat_id, name from public.categories where cat_id in " + \
#                 "(select cat_id_2 from public.categories_categories where cat_id_1  = '" + cat + "') and cat_id in " + \
#                 "(select cat_id from public.pathologies_categories where pat_id in (" + list2query(list_pat) + ")) order by 2"
                
#     print("query subcats",query)
#     rows = readDB(query)

#     if len(rows) > 0:
#         return rows
    
#     return None

def get_sympthoms(list_pat, list_subcat):

    # Hago modificación para eliminar una primer query
    # query_1 = "select distinct pat_id from public.pathologies_categories where cat_id = '" + list_subcat[0] + \
    #                         "' and pat_id in (" + list2query(list_pat) + ")"

    print("get sym - list pat", list_pat)
    print("get sym - list subcat", list_subcat)
    
    subcat = ""
    if len(list_subcat) > 1:
        subcat = list_subcat[-1][0]
    else:
        subcat = list_subcat[0][0]

    query_2 = "select distinct sym_id from public.pathologies_symptoms where pat_id in (" + list2query(list_pat)
    query_2 += ") and sym_id in (select distinct sym_id from public.categories_symptoms where cat_id in ('" + subcat + "'))"

    query_2_2 = "select sym_id, name from public.symptoms where sym_id in (" + query_2 + ") order by 2"
    list_symp = readDB(query_2_2)

    if len(list_symp):
        return list_symp
    
    return None


def get_pat(list_cat,list_subcat,list_sym,list_pat):
    print("list_cat",list_cat)
    print(list_subcat)
    print("list_sym",list_sym)
    print(list_pat)

    # Query Cats y SubCats
    list_total = []
    if len(list_cat) > 1:
        for cat in list_cat:
            print("cat",cat)
            list_total.append(cat)
    else:
        list_cat_2 = str(list_cat[0]).split(",")
        for cat in list_cat_2:
            print("cat str",cat)
            list_total.append(cat)


    if list_subcat != None:
        for subcat in list_subcat[0]:
            print("sub cat",subcat)
            list_total.append(subcat)
    
    print("list total",list_total)
    query_cat = ""
    if len(list_total) > 1:
        for i in range(len(list_total) - 1):
            query_cat += "select distinct pat_id from public.pathologies_categories where cat_id = '" + list_total[i] + "' and pat_id in ("
        query_cat += "select distinct pat_id from public.pathologies_categories where cat_id = '" + list_total[len(list_total)-1] + "'"
        query_cat += ")))))))))))))"[-(len(list_total)-1):]
    else: 
        query_cat = "select distinct pat_id from public.pathologies_categories where cat_id = '" + list_total[0] + "'"
    print("query cat",query_cat)

    # Query Sym
    query_sym = ""
    print("Query sym!!!")
    if list_sym != None:
        if len(list_sym) >= 1:
            print("list sym",list_sym)

            list_sym_final = []
            for sym in list_sym[0]:
                list_sym_final.append(sym)

            if len(list_sym_final) > 1:
                for i in range(len(list_sym_final) - 1):
                    query_sym += "select distinct pat_id from public.pathologies_symptoms where sym_id = '" + list_sym_final[i] + "' and pat_id in ("
                query_sym += "select distinct pat_id from public.pathologies_symptoms where sym_id = '" + list_sym_final[len(list_sym_final)-1] + "'"
                query_sym += ")))))))))))))"[-(len(list_sym_final)-1):]
            else:
                query_sym = "select distinct pat_id from public.pathologies_symptoms where sym_id = '" + list_sym_final[0] + "'"
        
    print("query sym", query_sym)


    # Armo query text
    query_text = "select pat_id, name from public.pathologies where pat_id in (" + query_cat + ") " 
    if list_sym != None:
        if len(list_sym) >= 1:
            query_text += "and pat_id in ("+ query_sym +")"
    if list_pat != None:
        if len(list_pat) >= 1:
            query_text += "and pat_id in ("+ list2query(list_pat) +")"
    print(query_text)

    # Busco y devuelvo la consulta
    list_pat = readDB(query_text)
    if len(list_pat) > 0:
        print("list pat", list_pat)
        return list_pat

    return None

def get_pat_from_subcategories(list_pat, list_subcat):
    query_1 = "select distinct pat_id from public.pathologies_categories where cat_id = '" + list_subcat[0] + \
                            "' and pat_id in (" + list2query(list_pat) + ")"
    query_1_2 = "select pat_id, name from public.pathologies where pat_id in (" + query_1 + ")" 
    list_pat = readDB(query_1_2)
    if len(list_pat) > 0:
        return list_pat

    return None

def get_pat_from_subcategories_more(cats, list_subcat):
    list_total = []
    for cat in cats:
        list_total.append(cat)

    for subcat in list_subcat[0]:
        list_total.append(subcat)
    print("list total",list_total)
    # query_1 = get_pat_from_categories(list_total)
    query = ""
    for i in range(len(list_total) - 1):
        query += "select distinct pat_id from public.pathologies_categories where cat_id = '" + list_total[i] + "' and pat_id in ("
    query += "select distinct pat_id from public.pathologies_categories where cat_id = '" + list_total[len(list_total)-1] + "'"
    query += ")))))))))))))"[-(len(list_total)-1):]
    # query_1 = "select distinct pat_id from public.pathologies_categories where cat_id in (" + list2query(list_subcat) + \
    #                         ") and pat_id in (" + list2query(list_pat) + ")"
    print("query",query)
    query_1_2 = "select pat_id, name from public.pathologies where pat_id in (" + query + ")" 
    list_pat = readDB(query_1_2)
    if len(list_pat) > 0:
        return list_pat

    return None

def get_pat_from_categories(list_cat):
    query = ""
    if len(list_cat) > 1:
        for i in range(len(list_cat) - 1):
            query += "select distinct pat_id from public.pathologies_categories where cat_id = '" + list_cat[i] + "' and pat_id in ("
        query += "select distinct pat_id from public.pathologies_categories where cat_id = '" + list_cat[len(list_cat)-1] + "'"
        query += ")))))))))))))"[-(len(list_cat)-1):]
        list_pat = readDB(query)
    else:
        query = "select distinct pat_id from public.pathologies_categories where cat_id = '" + list_cat[0]
        list_pat = readDB(query)

    if len(list_pat) > 0:
        return list_pat
    else:
        return None
    
def get_pat_from_symptoms(list_pat,sym):
    query = ""
    query += "select * from public.pathologies where pat_id in ( "
    query += "select pat_id from public.pathologies_symptoms where sym_id = '" + sym[0] + "' and pat_id in (" + list2query(list_pat)
    query += ")) order by name"
    list_pat = readDB(query)

    if len(list_pat) > 0:
        return list_pat
    else:
        return None

def first_question(token, language):
    # --- Insertar un elemento vacío
    client = MongoClient(MONGO_DB_PATH)
    db = client[MONGO_DB_NAME]  # Replace 'your_database' with your database name
    collection = db[MONGO_DB_COLLECTION_RES]  # Replace 'your_collection' with your collection name

    first_layer = {
        "cat": [],
        "next_cat": "",
        "sub_cat": [],
        "sym": [],
        "sub_sub_cat": [],
        "pat": []
    }

    ques_options = []
    responses = []
    questions = [{"question_id": "pregunta1", "options": ques_options}]

    mydict = { 
        "user_id": token, 
        "date": datetime.datetime.now(), 
        "data": first_layer, 
        "last_question": "pregunta1", 
        "show_data": "false", 
        "data_2_show": "",
        "questions": questions,
        "responses": responses 
    }

    response = get_complete_question(FIRST_QUESTION, language)

    options = get_categories()
    
    for i in range(len(options)):
        data = {"id": i+1, "value": str(options[i][1]), "db_id": str(options[i][0])}
        ques_options.append(data)

        response = response + "<br>" + str(i+1) + ") " + str(options[i][1])
    
    x = collection.insert_one(mydict)        

    if x:
        if response:
            return response
        else: 
            return None    
    else: 
        return None
    
def get_options_for_text(text):
    try:
        validate_options = []
        selected_options = text.split(",")
        
        for x in selected_options:
            validate_options.append(x.strip())

        return validate_options
    except:
        return None
    
def show_data(data,data2show):
    response = "Las patologías que detectamos que contienen los síntomas indicados son:<br><br>"
    if data2show == "pat":
        for x in data["pat"]:
            response += ". " + x[1] + "<br>"
    return response

def sort_cats(list_cat):
    list_sorted = []
    cats = ""
    for cat in list_cat:
        cats += "'" + cat + "',"
    cats = cats[:len(cats)-1]
    
    list = []
    for cat in list_cat:
        query = "select cat_id, count(0) from public.categories_symptoms where cat_id = '" + cat + "' group by cat_id order by 2"
        rows = readDB(query)
        list.append(rows)
    
    print("lista no ordenada", list)
    list = sorted(list, key=lambda x: x[0][1])
    print("lista ordenada", list)

    flat_list = [item[0][0] for item in list]
    if flat_list:
        print("Flat List", flat_list)
        return flat_list
    
    #Old code
    query = "select cat_id, count(0) from public.categories_symptoms where cat_id in (" + cats + ") group by cat_id order by 2"
    rows = readDB(query)

    for cat in rows:
        list_sorted.append(cat[0])

    if len(list_sorted) > 0:
        print(list_sorted)
        return list_sorted
    
    return None

def get_name_cat(cat_id):
    try:
        query = "select name from public.categories where cat_id = '"+ cat_id + "'"
    
        rows = readDB(query)
        
        text_cat = ""
        
        for cat in rows:
            text_cat = cat[0]
        return text_cat
    
    except:
        return None
    
def back(questions, token, responses,language,cats, subcats,syms,pats):
    client = MongoClient(MONGO_DB_PATH)
    db = client[MONGO_DB_NAME]  # Replace 'your_database' with your database name
    collection = db[MONGO_DB_COLLECTION_RES]  # Replace 'your_collection' with your collection name

    questions_saved = questions
    new_questions = []
        
    #analizo si tiene dos question saves, es que es la primer pasada
    if len(questions_saved) == 2:
        token = secrets.token_hex(20)
        return first_question(token, language), token

    for i in range(len(questions_saved)-2):
        new_questions.append(questions_saved[i])

    query = {"user_id": token}
    update = {"$set": {"questions": new_questions}}
    result = collection.update_one(query, update)


    responses_saved = responses
    new_responses = []

    for i in range(len(responses_saved)-1):
        new_responses.append(responses_saved[i])

    query = {"user_id": token}
    update = {"$set": {"responses": new_responses}}
    result = collection.update_one(query, update)

    print("new quest", new_questions)
    print("new resp", new_responses)

    query = {"user_id": token}
    update = {"$set": {"show_data": ""}}
    result = collection.update_one(query, update)   
    
    text_response = responses[-2]

    # Borro todo lo guardado
    query = {"user_id": token}
    update = {"$set": {f"data.cat": [],"data.sub_cat": [], "data.sym":[], "data.pat": []}}
    result = collection.update_one(query, update) 

    for i in range(len(new_questions)-1):

        rtas = str(new_responses[i]).split(",")
        data2save = []

        print("rtas " + str(i), rtas)

        for opt in new_questions[i]["options"]:
            print("opt",opt)
            for rta in rtas:
                if str(opt["id"])  == rta:
                    data2save.append(opt["db_id"])

        print("data " + str(i), data2save)

        if new_questions[i]["question_id"] == "pregunta1":
            print("guardo pregunta 1")
            query = {"user_id": token}
            update = {"$set": {f"data.cat": data2save}}
            result = collection.update_one(query, update) 
        
        if new_questions[i]["question_id"] == "pregunta2":
            print("guardo pregunta 2")
            data2save = [[txt] for txt in data2save]
            print("data mod" + str(i), data2save)
            query = {"user_id": token}
            update = {"$push": {f"data.sub_cat": data2save}}
            result = collection.update_one(query, update)  
        
        if new_questions[i]["question_id"] == "pregunta3":
            print("guardo pregunta 3")
            data2save = [[txt] for txt in data2save]
            print("data mod" + str(i), data2save)
            query = {"user_id": token}
            update = {"$push": {f"data.sym": data2save}}
            result = collection.update_one(query, update)  


    # list_pat = get_pat(cats,subcats,syms,pats)

    # query = {"user_id": token}
    # update = {"$set": {f"data.pat": list_pat}}
    # result = collection.update_one(query, update)

    if result:
        query = { "user_id": token}
        update = {"$set": {"last_question": new_questions[-1]["question_id"]}}
        result = collection.update_one(query, update)  
        if result:
            return middle_question(text_response, token, language)
    return None

def middle_question(text, token, language):
    try:
        client = MongoClient(MONGO_DB_PATH)
        db = client[MONGO_DB_NAME]  # Replace 'your_database' with your database name
        collection = db[MONGO_DB_COLLECTION_RES]  # Replace 'your_collection' with your collection name

        #separo las opciones recibidas
        selected_options = get_options_for_text(text)

        #obtengo el elemento completo del usuario y me traigo la ultima layer
        response_saved = find_response_by_user(token)

         ## CODIGO PARA VOLVER ATRAS
        if text == "atras":
            return back(response_saved["questions"],token, response_saved["responses"],language, response_saved["data"]["cat"], response_saved["data"]["sub_cat"],response_saved["data"]["sym"],response_saved["data"]["pat"])
        
        #Guardo las responses
        query = {"user_id": token}
        update = {"$push": {"responses": text}}
        result = collection.update_one(query, update)

        #obtengo la ultima pregunta para saber que tipo de pregunta tengo que mostrar
        last_question = response_saved["last_question"]
        list_of_yesoptions = ["si","Sí","Si","sí","yes","sep","sip"]

        if response_saved["show_data"] == "true":
            if selected_options[0] in list_of_yesoptions:
                response = show_data(response_saved["data"],response_saved["data_2_show"])
                response += "<br>Desea ingresar otro síntoma? (SI/NO)"
            else:
                response = "Desea ingresar otro síntoma? (SI/NO)"
            query = { "user_id": token}
            update = {"$set": {"show_data": "moredata", "data_2_show": ""}}
            result = collection.update_one(query, update)
            if response:
                return response
        
        if response_saved["show_data"] == "moredata":
            if selected_options[0] in list_of_yesoptions:
                list_cats = response_saved["data"]["cat"]
                actual_cat_position = response_saved["data"]["next_cat"]
                if actual_cat_position > len(list_cats)-1:
                    return "Ya no hay más sistemas seleccionados inicialmente. Muchas gracias por haber utilizado el RDiBot"
                
                actual_cat = list_cats[actual_cat_position]

                next_cat = actual_cat_position +1

                query = {"user_id": token}
                update = {"$set": {"data.next_cat": next_cat}}
                result = collection.update_one(query, update)
            
                # list_subcats = get_subcategories_from_cats_and_pats(actual_cat, response_saved["data"]["pat"])
                list_subcats = get_subcategories(actual_cat, response_saved["data"]["pat"])


                ##Agrego nombre de la cateogira que voy a mostrar
              
                response = get_complete_question("pregunta2", language)
                response += "<br> <br>" + get_name_cat(actual_cat) + "<br>"
            
                ques_options = []
                question = {"question_id": "pregunta2", "options": ques_options}

                for i in range(len(list_subcats)):
                    data = {"id": i+1, "value": str(list_subcats[i][1]), "db_id": str(list_subcats[i][0])}
                    ques_options.append(data)
                    response = response + "<br>" + str(i+1) + ") " + str(list_subcats[i][1])
                
                query = {"user_id": token}
                update = {"$push": {"questions": question}}
                result = collection.update_one(query, update)

                #Actualizo last_question
                query = { "user_id": token}
                update = {"$set": {"last_question": "pregunta2"}}
                result = collection.update_one(query, update)                           
            else:
                response = "Muchas gracias por haber utilizado el RDiBot"
            query = { "user_id": token}
            update = {"$set": {"show_data": "false", "data_2_show": ""}}
            result = collection.update_one(query, update)
            if response:
                return response

        if last_question == "pregunta1":
            rta_selected = []
            last_options = []
            questions = response_saved["questions"]
            
            # Obtengo las opciones de la pregunta anterior y busco las rta segun el id
            for quest in questions:
                if quest["question_id"] == last_question:
                    last_options = quest["options"]
            for sel_opt in selected_options:
                for opt in last_options:
                    if str(opt["id"]) == sel_opt:
                        rta_selected.append(str(opt["db_id"]))

            # Ordeno las cats seleccionadas segun la cantidad de sintomas
            list_cats = sort_cats(rta_selected)

            # Guardo las categorias en mongoDB
            query = {"user_id": token}
            update = {"$set": {f"data.cat": list_cats, "data.next_cat": 1}}
            result = collection.update_one(query, update)

            # Busco y guardo las patologias
            #list_pat = get_pat_from_categories(rta_selected) #0609MOD
            list_pat = get_pat(rta_selected,None,None,None)

            query = {"user_id": token}
            update = {"$set": {f"data.pat": list_pat}}
            result = collection.update_one(query, update)
            response = "La cantidad de patologias que quedan filtradas son {}, continuaremos con las consultas para reducir la búsqueda.<br>".format(len(list_pat))

            # Busco las sub cat de la cat seleciconada y preparo la pregunta para usuario
            list_subcats = get_subcategories(list_cats[0])
            response += get_complete_question("pregunta2", language)
            response += "<br> <br>" + get_name_cat(list_cats[0]) + "<br>"

            try: 
                ques_options = []
                question = {"question_id": "pregunta2", "options": ques_options}
                for i in range(len(list_subcats)):
                    data = {"id": i+1, "value": str(list_subcats[i][1]), "db_id": str(list_subcats[i][0])}
                    ques_options.append(data)
                    response = response + "<br>" + str(i+1) + ") " + str(list_subcats[i][1])
                
                query = {"user_id": token}
                update = {"$push": {"questions": question}}
                result = collection.update_one(query, update)

                #Actualizo last_question
                query = { "user_id": token}
                update = {"$set": {"last_question": "pregunta2"}}
                result = collection.update_one(query, update)
            
            except Exception as e:
                print(e)
            
            if result:
                return response
            
        if last_question == "pregunta2":
            print("Pregunta 2")
            rta_selected = []
            last_options = []
            questions = response_saved["questions"]
            
            # Obtengo las opciones de la pregunta anterior y busco las rta segun el id
            for quest in questions:
                if quest["question_id"] == last_question:
                    last_options = quest["options"]
            for sel_opt in selected_options:
                for opt in last_options:
                    if str(opt["id"]) == sel_opt:
                        rta_selected.append(str(opt["db_id"]))

            # Guardo las sub categorias en mongoDB
            query = {"user_id": token}
            update = {"$push": {f"data.sub_cat": rta_selected}}
            result = collection.update_one(query, update)
            
            # Busco y guardo las patologias (segun la sub cat seleccionada y las pat)
            #list_pat = get_pat_from_subcategories(response_saved["data"]["pat"],rta_selected) #0609MOD
            response_saved = find_response_by_user(token)
            list_pat = get_pat(response_saved["data"]["cat"],response_saved["data"]["sub_cat"],response_saved["data"]["sym"],response_saved["data"]["pat"])

            query = {"user_id": token}
            update = {"$set": {f"data.pat": list_pat}}
            result = collection.update_one(query, update)
            response = "La cantidad de patologias que quedan filtradas son {}, continuaremos con las consultas para reducir la búsqueda.<br>".format(len(list_pat))
   
            # Busco los síntomas de la cat seleciconada y preparo la pregunta para usuario
            print("llego a buscar sintomas")
            response_saved = find_response_by_user(token)
            list_syms = get_sympthoms(response_saved["data"]["pat"],response_saved["data"]["sub_cat"])
            response += get_complete_question("pregunta3", language)
            ques_options = []
            question = {"question_id": "pregunta3", "options": ques_options}

            n = 1
            for sym in list_syms:
                data = {"id": n, "value": str(sym[1]), "db_id": str(sym[0])}
                ques_options.append(data)
                response = response + "<br>" + str(n) + ") " + str(sym[1])
                n += 1
            
            query = {"user_id": token}
            update = {"$push": {"questions": question}}
            result = collection.update_one(query, update)

            #Actualizo last_question
            query = { "user_id": token}
            update = {"$set": {"last_question": "pregunta3"}}
            result = collection.update_one(query, update)

            if result:
                return response
        
        if last_question == "pregunta3":
            print("Pregunta3")
            rta_selected = []
            last_options = []
            questions = response_saved["questions"]
            
            # Obtengo las opciones de la pregunta anterior y busco las rta segun el id
            for quest in questions:
                if quest["question_id"] == last_question:
                    last_options = quest["options"]
            for sel_opt in selected_options:
                for opt in last_options:
                    if str(opt["id"]) == sel_opt:
                        rta_selected.append(str(opt["db_id"]))

            # Guardo los síntomas categorias en mongoDB
            query = {"user_id": token}
            update = {"$push": {f"data.sym": rta_selected}}
            result = collection.update_one(query, update)
            
            # Busco y guardo las patologias (segun el síntoma mencionado y las pat)
            response_saved = find_response_by_user(token)
            # list_pat = get_pat_from_symptoms(response_saved["data"]["pat"],response_saved["data"]["sub_cat"],rta_selected,response_saved["data"]["pat"]) #0609MOD
            list_pat = get_pat(response_saved["data"]["cat"],response_saved["data"]["sub_cat"],response_saved["data"]["sym"],response_saved["data"]["pat"])

            query = {"user_id": token}
            update = {"$set": {f"data.pat": list_pat}}
            result = collection.update_one(query, update)
            response = "La cantidad de patologias que quedan filtradas son {}.<br>".format(len(list_pat))
            response += "<br>Desea ver los datos? (SI/NO)"

            #Actualizo para mostrar data
            query = { "user_id": token}
            update = {"$set": {"show_data": "true", "data_2_show": "pat"}}
            result = collection.update_one(query, update)
            
            ##Guardo para tener el volver a atras
            query = {"user_id": token}
            update = {"$push": {"questions": {"question_id": "pregunta3", "options": [] }}}
            result = collection.update_one(query, update)

            #Actualizo last_question
            query = { "user_id": token}
            update = {"$set": {"last_question": "pregunta3"}}
            result = collection.update_one(query, update)

            if result:
                return response
    
       
        return "ok"
    except Exception as e:
        print(e)
        return "Hubo un error, por favor responda nuevamente"

def handler(texto, token, language):
    if token is None:
        token = secrets.token_hex(20)

    if check_if_token_exist(token):
        if check_token(token):
            print("MiddleQuestion")
            return middle_question(texto, token, language)
        else:
            token = secrets.token_hex(20)
            print("FirstQuestion")
            return first_question(token, language), token
    else:
        
        return first_question(token, language), token

def check_token(token):
    response_saved = find_response_by_user(token)
    saved_time = response_saved["date"]
    seconds = (datetime.datetime.now() - saved_time).total_seconds()

    if seconds <= 5000:
      
        client = MongoClient(MONGO_DB_PATH)
        db = client[MONGO_DB_NAME]  # Replace 'your_database' with your database name
        collection = db[MONGO_DB_COLLECTION_RES]  # Replace 'your_collection' with your collection name

        query = {"user_id": token}
        update = {"$set": {f"date": datetime.datetime.now()}}

        result = collection.update_one(query, update)

        return True
    else: 
        return None