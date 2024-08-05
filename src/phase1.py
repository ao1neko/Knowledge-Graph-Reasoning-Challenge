from rdflib import Graph
from pathlib import Path
import json
import re 
from SPARQLWrapper import SPARQLWrapper, JSON
import argparse


def get_question_info(question_json: dict):
    for answer_json in  question_json["answers"]:
        if answer_json["correct"] == True:
            answer = answer_json["answer"]
    senario = question_json["senario"]
    question = question_json["question"]
    return senario, question, answer
    

def do_sparql_query_to_get_events(activity: str, scene: str):
    sparql_query = f"""
    PREFIX ex: <http://kgrc4si.home.kg/virtualhome2kg/instance/>
    PREFIX : <http://kgrc4si.home.kg/virtualhome2kg/ontology/>
    PREFIX ac: <http://kgrc4si.home.kg/virtualhome2kg/ontology/action/>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    select (count(?event) AS ?count) WHERE {{
        ex:{activity.lower()}_{scene} :hasEvent ?event .
    }}
    """
    sparql = SPARQLWrapper("https://kgrc4si.home.kg:7200/repositories/KGRC4SIv05")
    sparql.setQuery(sparql_query)
    sparql.setReturnFormat(JSON)
    query_result = sparql.query().convert()
    return int(query_result["results"]["bindings"][0]["count"]["value"])
    
def do_sparql_query_to_enter_room(activity: str, scene: str, room: str):
    sparql_query = f"""
    PREFIX ex: <http://kgrc4si.home.kg/virtualhome2kg/instance/>
    PREFIX : <http://kgrc4si.home.kg/virtualhome2kg/ontology/>
    PREFIX ac: <http://kgrc4si.home.kg/virtualhome2kg/ontology/action/>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    select * WHERE {{
        ex:{activity.lower()}_{scene} :hasEvent ?event .
        ?event :to ?room .
        ?room rdfs:label "{room}" .
    }}
    """
    sparql = SPARQLWrapper("https://kgrc4si.home.kg:7200/repositories/KGRC4SIv05")
    sparql.setQuery(sparql_query)
    sparql.setReturnFormat(JSON)
    query_result = sparql.query().convert()
    return len(query_result["results"]["bindings"])
    
def do_sparql_query_to_get_first_place(activity: str, scene: str, event_num: int):
    sparql_query = f"""
    PREFIX ex: <http://kgrc4si.home.kg/virtualhome2kg/instance/>
    PREFIX : <http://kgrc4si.home.kg/virtualhome2kg/ontology/>
    PREFIX ac: <http://kgrc4si.home.kg/virtualhome2kg/ontology/action/>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    select * WHERE {{
        ex:event{event_num}_{activity.lower()}_{scene} (:place|:from) ?room .
        ?room rdfs:label ?name .
    }}
    """
    sparql = SPARQLWrapper("https://kgrc4si.home.kg:7200/repositories/KGRC4SIv05")
    sparql.setQuery(sparql_query)
    sparql.setReturnFormat(JSON)
    query_result = sparql.query().convert()
    
    try:
        return query_result["results"]["bindings"][0]["name"]["value"]
    except:
        return None

def do_sparql_query_to_get_last_place(activity: str, scene: str, event_num: int):
    sparql_query = f"""
    PREFIX ex: <http://kgrc4si.home.kg/virtualhome2kg/instance/>
    PREFIX : <http://kgrc4si.home.kg/virtualhome2kg/ontology/>
    PREFIX ac: <http://kgrc4si.home.kg/virtualhome2kg/ontology/action/>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    select * WHERE {{
        ex:event{event_num}_{activity.lower()}_{scene} (:to|:place) ?room .
        ?room rdfs:label ?name .
    }}
    """
    sparql = SPARQLWrapper("https://kgrc4si.home.kg:7200/repositories/KGRC4SIv05")
    sparql.setQuery(sparql_query)
    sparql.setReturnFormat(JSON)
    query_result = sparql.query().convert()
    
    try:
        return query_result["results"]["bindings"][0]["name"]["value"]
    except:
        return None

def compare_first_last_place(last_place: str, first_place: str, scene: str,place: str):
    if last_place == first_place:
        return 0
    else:
        places = [first_place, last_place]
        if scene == "scene1":
            if last_place != "livingroom" and first_place != "livingroom" and place == "livingroom":
                return 1
        elif scene == "scene2":
            if last_place != "livingroom" and first_place != "livingroom" and place == "livingroom":
                return 1
        elif scene == "scene3":
            if "bathroom" in places and ("kitchen" in places or "livingroom" in places) and place == "bedroom":
                return 1
            if "bathroom" in places and "livingroom" in places and place == "kitchen":
                return 1
        elif scene == "scene4":
            if "bathroom" in places and ("bedroom" in places or "livingroom" in places) and place == "kitchen":
                return 1
            elif "livingroom" in places and ("bathroom" in places or "kitchen" in places) and place == "bedroom":
                return 1
        elif scene == "scene5":
            if "bathroom" in places and ("kitchen" in places or "livingroom" in places) and place == "livingroom":
                return 1
            elif "bedroom" in places and ("bathroom" in places or "livingroom" in places) and place == "kitchen":
                return 1
        elif scene == "scene6":
            if last_place != "bedroom" and first_place != "bedroom" and place == "bedroom":
                return 1
        elif scene == "scene7":
            if last_place != "kitchen" and first_place != "kitchen" and place == "kitchen":
                return 1
        return 0
    
    
    
    

def main(question_path: Path,episodes_path: Path):
    regex = re.compile(r"Did he enter the (.+?) ")
    accuracy = 0
    total = 0
    
    for question_file in question_path.iterdir():
        total += 1
        
        with open(question_file, 'r') as f:
            question_json=json.load(f)
        senario, question, answer = get_question_info(question_json)
        print("senario:", senario)
        print("question:", question)
        print("answer:", answer)
        
        scene,day = senario.split("_")
        place = re.search(regex, question).group(1)
        answer_number = re.search(rf"{place} (.+?) times", question).group(1)
        try:
            answer_number = re.search(rf"number=(.+?)\).number", answer_number).group(1)
        except:
            answer_number = answer_number
        #print(senario, question, answer)
        with open(episodes_path / Path(senario+".json"), 'r') as f:
            episode_json=json.load(f)
            activities = episode_json["data"]["activities"]
            #print(activities)
            
        counter = 0
        first_place = None
        last_place = None
        for i,activity in enumerate(activities):
            event_num = do_sparql_query_to_get_events(activity, scene)
            
            first_place = do_sparql_query_to_get_first_place(activity, scene, 0)

            if first_place == place and last_place != place and i!=0:
                counter += 1
            else:
                counter += compare_first_last_place(last_place, first_place, scene, place)
            
            last_place = first_place
            for i in range(1, event_num):
                return_place = do_sparql_query_to_get_last_place(activity, scene, i)
                if return_place != None:
                    last_place = return_place


            enter_num = do_sparql_query_to_enter_room(activity, scene, place)
            counter += enter_num
            #print("activity:", activity)
            #print("counter:", counter)
        print("result:", counter)
        print("answer:", answer_number)
        if counter == int(answer_number):
            print("正解")
            accuracy += 1
        else:
            print("不正解")
            
    print("accuracy:", accuracy/total)

        
if __name__ == '__main__':
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument("--PROJECT_PATH", type=str)
    args = arg_parser.parse_args()
    PROJECT_PATH=args.PROJECT_PATH
    QUESTION_PATH=PROJECT_PATH / Path("DataSet/QA/YesNo/Q1")
    EPISODE_PATH = PROJECT_PATH /Path("DataSet/CompleteData/Episodes")
    main(QUESTION_PATH,EPISODE_PATH)

