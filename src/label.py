from pathlib import Path
import json
import re 
from openai import OpenAI
import base64
import os
import argparse


def get_question_info(question_json: dict):
    for answer_json in  question_json["answers"]:
        if answer_json["correct"] == True:
            answer = answer_json["answer"]
    senario = question_json["senario"]
    question = question_json["question"]
    return senario, question, answer

def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")
    
def get_room(project_path: Path,image_path: Path,scene: str):
    client = OpenAI(api_key=os.environ.get('API_KEY', None))
    base64_image_1 = encode_image(image_path= project_path / "src" / "prompt_images" / scene /"kitchen.png")
    base64_image_2 = encode_image(image_path= project_path / "src" / "prompt_images" / scene / "bedroom.png")
    base64_image_3 = encode_image(image_path= project_path / "src" / "prompt_images" / scene / "bathroom.png")
    base64_image_4 = encode_image(image_path= project_path / "src" / "prompt_images" / scene / "livingroom.png")
    base64_image_test = encode_image(image_path=image_path)
    query = [
    {
      "role": "system",
      "content": [
        {
          "text": "Which of the following rooms are you in now?\n- bedroom\n- bathroom\n- kitchen\n- livingroom",
          "type": "text"
        }
      ]
    },
    {
        "role": "user",
        "content": [
            {
            "type": "image_url",
            "image_url": {
                "url": f"data:image/png;base64,{base64_image_1}"
            }
            }
        ]
    },
    {
      "role": "assistant",
      "content": [
        {
          "type": "text",
          "text": "kitchen"
        }
      ]
    },
    {
        "role": "user",
        "content": [
            {
            "type": "image_url",
            "image_url": {
                "url": f"data:image/png;base64,{base64_image_2}"
            }
            }
        ]
    },
    {
        "role": "assistant",
        "content": [
            {
            "type": "text",
            "text": "bedroom"
            }
        ]
    },
    {
        "role": "user",
        "content": [
            {
            "type": "image_url",
            "image_url": {
                "url": f"data:image/png;base64,{base64_image_3}"
            }
            }
        ]
    },
    {
        "role": "assistant",
        "content": [
            {
            "type": "text",
            "text": "bathroom"
            }
        ]
    },
    {
        "role": "user",
        "content": [
            {
            "type": "image_url",
            "image_url": {
                "url": f"data:image/png;base64,{base64_image_4}"
            }
            }
        ]
        },
    {
        "role": "assistant",
        "content": [
            {
            "type": "text",
            "text": "livingroom"
            }
        ]
    },
    {
        "role": "user",
        "content": [
            {
            "type": "image_url",
            "image_url": {
                "url": f"data:image/png;base64,{base64_image_test}"
            }
            }
        ]
    },
    ]
    response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages= query,
    temperature=1.0,
    max_tokens=30,
    top_p=1,
    frequency_penalty=0,
    presence_penalty=0
    )
    return response.choices[0].message.content
    
def main(PROJECT_PATH:Path):
    MOVIE_PATH = PROJECT_PATH / Path("movie")
    with open(MOVIE_PATH / "label" / "label.json", 'r') as f:
        label_json = json.load(f)
        
    for scene_path in reversed(list((MOVIE_PATH / "converted").iterdir())):
        tmp_scene = scene_path.name
        if tmp_scene != "scene2":
            continue
        if label_json.get(tmp_scene,None) == None:
            label_json[tmp_scene] = {}

        for activity_path in sorted(scene_path.iterdir()):
            tmp_activity = activity_path.name
            if label_json.get(tmp_scene,{}).get(tmp_activity,None) == None:
                label_json[tmp_scene][tmp_activity] = {}
            if "_0" in str(tmp_activity):
                for png_path in activity_path.iterdir():
                    tmp_png = png_path.stem
                    
                    if label_json[tmp_scene][tmp_activity].get(tmp_png,None) == None or label_json[tmp_scene][tmp_activity].get(tmp_png,None) == {}:
                        label_json[tmp_scene][tmp_activity][tmp_png] = {}
                        #try: 
                        room = get_room(PROJECT_PATH, png_path,scene=tmp_scene)
                        print("room:", room)
                        """
                        except:
                            room = "error"
                            print("gpt-4o-mini error")
                        """
                        if room in ["bedroom","bathroom","kitchen","livingroom"]:
                            label_json[tmp_scene][tmp_activity][tmp_png] = room
                            print("room:", label_json[tmp_scene][tmp_activity][tmp_png])
                        elif "bedroom" in room:
                            label_json[tmp_scene][tmp_activity][tmp_png] = "bedroom"
                            print("room:", label_json[tmp_scene][tmp_activity][tmp_png])
                        elif "bathroom" in room:
                            label_json[tmp_scene][tmp_activity][tmp_png] = "bathroom"
                            print("room:", label_json[tmp_scene][tmp_activity][tmp_png])
                        elif "kitchen" in room:
                            label_json[tmp_scene][tmp_activity][tmp_png] = "kitchen"
                            print("room:", label_json[tmp_scene][tmp_activity][tmp_png])
                        elif "livingroom" in room:
                            label_json[tmp_scene][tmp_activity][tmp_png] = "livingroom"
                            print("room:", label_json[tmp_scene][tmp_activity][tmp_png])
                        else:
                            print("error room:", room)
                            print("png_path:", png_path)
                            
                        with open(MOVIE_PATH / "label" / "label.json", 'w') as f:
                            json.dump(label_json, f, indent=4)
        
    with open(MOVIE_PATH / "label" / "label.json", 'w') as f:
        json.dump(label_json, f, indent=4)
    
    
    
if __name__ == '__main__':
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument("--PROJECT_PATH", type=str)
    args = arg_parser.parse_args()
    main(args.PROJECT_PATH)