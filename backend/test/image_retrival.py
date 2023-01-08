import requests, shutil



url = "https://d1okzptojspljx.cloudfront.net/generations/dbaabbe2-241f-4e0c-ac33-839e82f126c7-0.png"
file_name = "test.png"

res = requests.get(url, stream = True)

if res.status_code == 200:
    with open(file_name,'wb') as f:
        shutil.copyfileobj(res.raw, f)
    print('Image sucessfully Downloaded: ',file_name)
else:
    print('Image Couldn\'t be retrieved')


img_data = requests.get(url).content
with open('image_name.png', 'wb') as handler:
    handler.write(img_data)