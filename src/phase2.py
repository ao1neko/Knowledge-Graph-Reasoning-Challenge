from pathlib import Path
import json
import re 
from openai import OpenAI
import base64
import argparse


def get_question_info(question_json: dict):
    for answer_json in  question_json["answers"]:
        if answer_json["correct"] == True:
            answer = answer_json["answer"]
    senario = question_json["senario"]
    question = question_json["question"]
    return senario, question, answer


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
    

def main(PROJECT_PATH:Path):
    QUESTION_PATH=PROJECT_PATH / Path("DataSet/QA/YesNo/Q1")
    EPISODE_PATH = PROJECT_PATH /Path("DataSet/CompleteData/Episodes")
    MOVIE_PATH = PROJECT_PATH / Path("movie")
    
    regex = re.compile(r"Did he enter the (.+?) ")
    accuracy = 0
    total = 0
    
    with open(MOVIE_PATH / "label" / "label.json", 'r') as f:
        label_json = json.load(f)
    
    for question_file in QUESTION_PATH.iterdir():
        with open(question_file, 'r') as f:
            question_json=json.load(f)

        senario, question, answer = get_question_info(question_json)
        print("senario:", senario)
        print("question:", question)
        print("answer:", answer)
        
        scene,day = senario.split("_")
        question_place = re.search(regex, question).group(1)
        answer_number = re.search(rf"{question_place} (.+?) times", question).group(1)
        try:
            answer_number = re.search(rf"number=(.+?)\).number", answer_number).group(1)
        except:
            answer_number = answer_number
        #print(senario, question, answer)
        with open(EPISODE_PATH / Path(senario+".json"), 'r') as f:
            episode_json=json.load(f)
            activities = episode_json["data"]["activities"]
            #print(activities)
            
        counter = 0
        now_place = None
        if scene in ["scene7"]:
            total += 1
            for i,activity in enumerate(activities):
                
                MOVIE_PATH = PROJECT_PATH / Path("movie/converted") / scene / (activity + "_0")
                for png_path in sorted(list(MOVIE_PATH.iterdir())):
                    tmp_png = png_path.stem
                    next_place= label_json[scene][activity+"_0"][tmp_png]
                    if next_place == {}:
                        next_place = now_place
                    
                    if tmp_png == "_000":
                        counter += compare_first_last_place(now_place, next_place, scene, question_place)
                    if next_place != now_place:
                        now_place = next_place
                        if now_place == question_place:
                            counter += 1

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
    main(args.PROJECT_PATH)