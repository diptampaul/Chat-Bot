from django.conf import settings
from time import sleep
import requests
import openai
import shutil
import json
import os
from .models import OpenAIAnswer, StableDiffusionImageGeneration

def get_ai_answer(prompt, number_of_tokens=256):
    openai.api_key = settings.OPENAI_KEY

    print(f"Text received from user to generate OpenAIAnswer : {prompt}")
    generated = False
    while not generated:
        try:
            response = openai.Completion.create(
                model="text-davinci-003",
                prompt=str(prompt),
                temperature=0.7,
                max_tokens=int(number_of_tokens),
                top_p=1,
                frequency_penalty=0,
                presence_penalty=0
            )
            print(response)
            generated = True
        except Exception as e:
            print(f"Exception occured : {e}")
            sleep(0.5)

    output = {}
    output["text"] = response["choices"][0]["text"]
    output["id"] = response["id"]
    output["model"] = response["model"]
    output["object"] = response["object"]
    output["completion_tokens"] = response["usage"]["completion_tokens"]
    output["prompt_tokens"] = response["usage"]["prompt_tokens"]
    output["total_tokens"] = response["usage"]["total_tokens"]

    #Update DB
    OpenAIAnswer.objects.create(input_text = str(prompt), output_text = output["text"], openai_id = output["id"], openai_model = output["model"], openai_object = output["object"], completion_tokens = output["completion_tokens"], prompt_tokens = output["prompt_tokens"], total_tokens = output["total_tokens"])

    return output

def get_ai_image(message_id, prompt, image_size, number_of_images):
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    STABLE_DIFFUSION_API_KEY = settings.STABLE_DIFFUSION_API_KEY
    url = "https://stablediffusionapi.com/api/v3/text2img"

    generated = False
    while not generated:
        try:
            payload = json.dumps({
                "key": str(STABLE_DIFFUSION_API_KEY),
                "prompt": "ultra realistic " + str(prompt) + " 8K, clear picture",
                "negative_prompt": "((out of frame)), ((extra fingers)), mutated hands, ((poorly drawn hands)), ((poorly drawn face)), (((mutation))), (((deformed))), (((tiling))), ((naked)), ((tile)), ((fleshpile)), ((ugly)), (((abstract))), blurry, ((bad anatomy)), ((bad proportions)), ((extra limbs)), cloned face, (((skinny))), glitchy, ((extra breasts)), ((double torso)), ((extra arms)), ((extra hands)), ((mangled fingers)), ((missing breasts)), (missing lips), ((ugly face)), ((fat)), ((extra legs)), anime",
                "width": str(image_size),
                "height": str(image_size),
                "samples": str(number_of_images),
                "num_inference_steps": "20",
                "seed": None,
                "guidance_scale": 7.5,
                "webhook": None,
                "track_id": None
            })
            headers = {
                'Content-Type': 'application/json'
            }
            response = requests.request("POST", url, headers=headers, data=payload)
            output = json.loads(response.text)
            print(output)
            if response.status_code == 200:
                generated = True
                
        except Exception as e:
            print(f"Exception occured : {e}")
    
    image_urls = output["output"]

    #Storing the images
    total_images = StableDiffusionImageGeneration.objects.all().count()
    directory = os.path.join(BASE_DIR,"media", "generated_images")
    generated_data = []
    for image_url in image_urls:
        file_name = f"sd-image-{total_images + 1}.png"
        total_images += 1
        res = requests.get(image_url, stream = True)
        file_path = os.path.join(directory, file_name)
        print(file_path)
        if res.status_code == 200:
            with open(file_path,'wb') as f:
                shutil.copyfileobj(res.raw, f)
            print('Image sucessfully Downloaded: ',file_name)
            generated_data.append({"image_url": image_url, "file_name": file_name})
            
            #Update DB
            StableDiffusionImageGeneration.objects.create(message_id = message_id, message_text = prompt, number_of_images = number_of_images, image_size = image_size, image_url = image_url, image_name = file_name, image_path = file_path)
        else:
            print('Image Couldn\'t be retrieved')


    return generated_data



def edit_image(prompt, image_size, number_of_images, isArt = False):
    openai.api_key = settings.OPENAI_KEY
