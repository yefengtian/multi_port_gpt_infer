import os
import requests
import json
import base64
from tqdm import tqdm
import re
import logging
import csv
import time
import random
import argparse

# def setup_logging(log_folder, input_file):
#     os.makedirs(log_folder, exist_ok=True)
#     base_name = os.path.splitext(os.path.basename(input_file))[0]
#     log_file = os.path.join(log_folder, f'{base_name}.log')
#     logging.basicConfig(filename=log_file, level=logging.INFO, 
#                         format='%(asctime)s - %(levelname)s - %(message)s')
#     return logging.getLogger(__name__)

def setup_logging(log_folder, port):
    os.makedirs(log_folder, exist_ok=True)
    log_file = os.path.join(log_folder, f'port_{port}.log')
    logging.basicConfig(filename=log_file, level=logging.INFO, 
                        format='%(asctime)s - %(levelname)s - %(message)s')
    return logging.getLogger(__name__)

# 在 main 函数开始时
# logger = setup_logging(args.log_folder, args.port)

use_prompt = '''
请仔细观察我提供的电商模特图，生成一个详细的列表元素属性的英文提示词（考虑提示词有限，所以尽量把字数留给重要的客观描述），
以便DALL-E 3能够创建一个非常相似的图像。
预定义知识：
A类别的显著特征如下：
    皮肤颜色 ：白色皮肤。
    头发颜色 ：范围广泛，包括金色、红色、棕色和黑色。头发质地通常较直或有些波浪。
    眼睛颜色 ：包括蓝色、绿色、灰色、棕色和黑色。
    面部特征 ：鼻梁通常较高，鼻子较窄。颧骨不太突出，脸部轮廓较为柔和。
B类别的显著特征如下：
    皮肤颜色 ：黄色皮肤。
    头发颜色 ：通常是黑色或深棕色，质地通常较直或略有波浪。
    眼睛颜色 ：眼睛颜色通常为深棕色或黑色，眼形可能包括单眼皮或双眼皮，眼角有时略微上翘。
    面部特征 ：
    鼻子 ：鼻梁通常较平，鼻翼较宽。
    颧骨 ：颧骨可能较高或较宽。
    下巴 ：下巴和下颚线条较为柔和。
C类别的显著特征如下：
    皮肤颜色 ：黑色皮肤，通常较深，从深褐色到黑色不等。
    头发颜色 ：通常是黑色或深棕色，质地通常较卷曲或紧密卷曲。
    眼睛颜色 ：眼睛颜色通常为深棕色或黑色。
    面部特征 ：
    鼻子 ：鼻翼较宽，鼻梁较平。
    嘴唇 ：嘴唇通常较厚。
    颧骨 ：颧骨可能较高和突出。
D类别的显著特征如下：
    皮肤颜色 ：通常为棕色皮肤，也可能为红色或铜色皮肤。
    头发颜色 ：包括黑色、深棕色、浅棕色，有时甚至是金色或红色。质地可以是直的、波浪的或卷曲的。
    眼睛颜色 ：多样，包括深棕色、浅棕色、绿色、蓝色和灰色。
    面部特征 ：
    鼻子 ：鼻型多样，有些人鼻梁较高，有些人鼻翼较宽。
    嘴唇 ：嘴唇厚度和形状各异。
    颧骨 ：颧骨可能较高和突出。
E类别的显著特征如下：
    皮肤颜色 ：肤色范围较广，取决其父母，通常具有独特的光泽和色调。
    头发颜色 ：头发颜色和质地可能是不同祖先特征的混合，包括黑色、棕色、金色或红色，质地可以是直的、波浪的或卷曲的。
    眼睛颜色 ：颜色多样，包括深棕色、浅棕色、绿色、蓝色和灰色，眼形和眼角特征也可能是不同祖先特征的结合。
    面部特征 ：
    鼻子 ：鼻型可能是不同祖先特征的混合，有些人可能有较高的鼻梁，有些人可能有较宽的鼻翼。
    嘴唇 ：嘴唇的厚度和形状可能各异。
    颧骨 ：颧骨可能较高和突出，也可能较平和不明显。

请考虑以下服装描述要素：
1. 总体描述，例如：
    场景：描述图像中的场景或环境，例如，室内还是室外，背景颜色和风格（例如，简洁的背景、城市街道、自然风光）。如"室内光滑的白色墙面背景"或"户外的繁忙城市街道，背景模糊以突出前景"。
    摄影风格：描述照片的风格，例如，高清摄影，柔和的光线，清晰的细节，或者是否使用特定的摄影技术（如黑白摄影、高对比度等）。如"使用软光和低对比度设置以保持色彩的自然过渡，细节清晰可见"。
2. 模特：
    皮肤颜色：白皙、健康肤色、深肤色、古铜色等。描述皮肤的色泽和特质，如"均匀的浅棕色，具有自然光泽"。
    头发颜色：包括黑色、深棕色、浅棕色，金色、红色、棕色。质地可以是直的、波浪的、卷曲的、紧密卷曲的。
    眼睛颜色：包括黑色、深棕色、浅棕色、绿色、蓝色和灰色。
    面部特征：鼻子：高鼻梁、平鼻梁、宽鼻翼、窄鼻翼。面部轮廓柔和，棱角分明。
    身高：高挑（约175cm以上）、中等身高（160-175cm）、娇小（160cm以下）等。提供具体身高范围，如"身高约170cm，展现中等比例的身材"。
    身材：纤瘦、标准、丰满、健美、苗条、有曲线感等。详细描述身材类型，如"苗条而线条流畅，腰部细长"。
    长相：立体五官、圆脸、瓜子脸、方脸、尖下巴、宽颧骨等。详细描述面部特征，如"瓜子脸型，高颧骨，双眼皮"。
    类别：A、B、C、D、E。
    妆容：裸妆、浓妆、复古妆、烟熏妆、日系妆、欧式妆、清新自然妆等。描述妆容风格和颜色，如"自然裸妆，眼影淡雅，唇色为柔和珊瑚粉"。
    发型：长发、短发、卷发、直发、马尾、盘发、辫子、发髻、刘海等。描述发型样式和质感，如"长直发，黑色，发丝顺滑光泽"。
    表情：微笑、冷酷、严肃、开心、自然、沉思、俏皮、迷离、清新、优雅等。具体描述表情，如"微笑，眼神中带有友善和自信"。
    姿势：站立、坐姿、跪姿、走路姿势、倚靠、回眸、下蹲、侧身等。详细描述姿势，如"站立，身体轻微向右侧倾斜，显得轻松自然"。
    动作：手插腰、手扶额、摆弄头发、举手、抚摸衣服、踢腿、张开双臂等。描述具体动作，如"左手轻放在腰侧，右手自然下垂"。
    眼神：坚定、自信、柔和、空灵、挑逗、自然等。描述眼神的特征，如"直视镜头，眼神清澈有神"。
    整体气质：优雅、冷酷、俏皮、甜美、知性、性感、酷感、活力、自然等。描述气质，如"展现出自信与专业的气质"。
    模特穿戴：描述模特的整体穿着风格，如简约、复古、优雅、前卫、运动、街头、朋克、波西米亚等。详细描述服装风格，如"穿着剪裁合体的深蓝色西装外套，内搭白色丝质衬衫"。
3. 服装面料：
    面料成分或材质：单选或者多选。例如棉、麻、丝绸、羽绒、羊毛、羊绒、PU革、人棉、氨纶、粘胶、涤棉、涤纶聚酯纤维、功能性合成纤维等。
    针梭织：单选。针织、梭织。
    面料功能性：多选。例如防风、防水防雨、防晒、防辐射、保暖、耐磨、抗皱、防火阻燃、透气、吸汗、速干等。
    面料适合场景:单选或者多选。例如日常穿搭、休闲穿搭、正式场合、约会场合等。
    面料适合季节：单选。春季、夏季、秋季、冬季、春夏、春秋、春冬、春秋冬、所有季节。
    面料厚度：单选。超薄、薄、中等厚度、厚。
    面料透明度：单选。透明、半透明、不透明。
    面料垂感：单选。无垂感、轻微垂感、明显垂感。
    面料柔软度：单选。极柔软、柔软、略硬、僵硬。
    面料光泽度：单选。亮光、亚光。
    面料皱感：单选。顺滑、无皱、微皱、明显褶皱。
    是否有面料拼接：单选。有、无。
    面料纹路和图案：例如条纹、格子、千鸟格、人字格、筋条、坑条、类似、花型。如果有颜色，也需要描述颜色，如果有排布，描述他们的排布，如均匀排布还是交叉排布还是杂乱排布等。
    面料工艺：单选或者多选。无、印花、色织条、色织格、色织千鸟格、色织花型、提花条、提花格、提花花型、金银丝、珠片/亮片绣、撒金/银片、亮丝、磨毛、手抓花、竹节、阳离子/段彩、花灰、雪花/多丽丝、花纱、彩棉、洗水皱、压褶、烫金/覆膜、压花、激光镭射、涂层/过胶、剪花、烧花/烂花、植绒、洗褪、透明条、绗棉、吊染、蜡染、扎染、盐缩。
    面料质感和穿着体验感：单选或者多选。例如丝滑、柔软、粗糙、绒感、毛感、颗粒感、脆硬感、贴身感、轻盈感、保暖感、透气感、清凉感、束缚感、挺阔感、蓬松感、爽滑感、重量感等。
4. 配饰：
    能够比较详细的描述出服装模特佩戴的饰品、鞋子、包袋等配饰。常见的配饰有项链，耳环，手链，戒指，手表，墨镜，帽子，腰带，围巾，头饰，胸针，腰链，脚链，鼻钉或鼻环，手套，腕带，眼镜链，徽章，鞋子，包袋，挂饰等。请重点从配饰的类型、材质、颜色、大小、位置关系等维度进行详细描述。
    配饰：项链，耳环，手链，戒指，手表，墨镜，帽子，腰带，围巾，头饰，胸针，腰链，脚链，鼻钉或鼻环，手套，腕带，眼镜链，徽章，鞋子，包袋，挂饰等。如"吊坠项链。长款金色吊坠项链，小巧的钻石吊坠在正中央。左手拿着一个黑色结构化手提包，表面细腻亮面，大小适中配有金属扣件"。
5. 颜色与图案：
    能够比较详细的描述出服装模特的颜色与图案等。颜色请从主色调和次色调、色彩渐变和层次、光泽和质感进行描述。图案请从图案类型、图案颜色、图案的密度和大小等维度进行详细描述。
    颜色：描述服装、配饰、鞋子的主色调和次色调等。如："主上衣的主色调为浅米色,带有细腻的浅灰色竖条纹。T恤的颜色为浅灰蓝,表面印有深蓝色与白色的复古风图案。休闲鞋的主色调为浅棕."
    图案：服装上的图案，如有必要，可将颜色一起描述。如："T恤的颜色为浅灰蓝，表面印有深蓝色与白色的复古风图案，图案中心是一辆经典的老爷车，周围环绕着淡黄色的轮辐设计。"
6. 背景与环境：
    能够比较详细的描述出服装模特的背景与环境等元素。请重点从背景环境的[场景/环境]、[背景颜色/色调]、[光线/照明]、[道具/配件]、[背景细节/装饰]、[模特与背景的关系]等维度进行详细描述。
    场景/环境：城市街道、室内摄影棚、户外自然景观、海滩、公园、都市天际线、古典建筑、现代建筑、豪宅内部、简约背景、工业风背景等。描述具体的场景环境，如"室内摄影棚，背景色为均匀的灰色"。
    背景颜色/色调：白色、灰色、黑色、粉色、柔和暖色调、冷色调、渐变色背景、纯色背景等。描述背景的颜色和色调，如"背景为单一的灰色，无渐变或纹理"。
    光线/照明：自然光、柔和光线、逆光、背光、侧光、硬光、点光源、光影效果、闪光灯、反光板等。描述光线的来源和效果，如"主光源为自然光，从左侧斜上方照射，柔和而均匀"。
    道具/配件：椅子、桌子、植物、伞、沙发、镜子、画框、书籍、旅行箱、自行车、墙纸、灯具、相框等。描述场景中使用的任何道具或配件及其位置，如"现代风格的黑色高背椅，摆放于模特左侧靠后的位置，增加视觉层次感"。
    背景细节/装饰：挂画、窗帘、书架、花瓶、墙面装饰、地毯、背景植物、艺术雕塑、挂钟等。详细描述背景中的装饰元素及其位置信息，如"模特右后方背景墙上挂有抽象艺术画作，使用蓝灰色调，与模特服装色彩协调"。
    模特与背景的关系：前景突出模特、背景模糊、模特与背景融合、模特与背景形成对比、远景与近景结合、背景作为故事情境的一部分等。描述模特与背景之间的视觉关系，如"模特清晰地位于画面中心，与简约的背景形成良好的视觉焦点，突出模特的穿着与气质"。
7. 文字元素：
    可以较敏锐的观察到模特服装上的文字，并能够比较详细的描述文字的各类信息，请重点从文字的[文字内容]、[字体类型]、[文字颜色]、[文字大小]、[文字位置]、[文字风格]、[文字材料与质感]、[文字动态效果]等维度进行详细描述。如果文字过小且看不清，请不要输出。
    服装文本描述：这里要极其严格，如果没有文字，请绝对不要输出！！千万不要有将图案误识别为文字的情况发生。如"上衣前胸中央印有一行英文大字“FREEDOM”，使用粗体无衬线(Sans-serif)字体，主色调为深蓝色，字母高度约为15厘米，文字下沿距离衣领约8厘米。文字具有微渐变效果，从顶部的深蓝色到底部的浅蓝色。字母外沿有2毫米宽的金色亮边，使其在亮光下反光。整体排列为水平居中，文字风格简约现代。文字是通过热转印技术实现的，表面光滑有轻微反光"。
8. 其他：
    特殊要求：任何额外的定制化要求，例如，特定的情感表达、叙述性元素，或者其他任何特定细节。如"确保模特的表情中透露出轻松而专注的职业态度"。
    任何其它独特或显著的特征需要被清楚描述，以确保图像的每一个细节都能被准确呈现。

1. Overall description: [总体描述]
2. Skin color: [肤色]
3. Hair color: [头发颜色]
4. Eyes color: [眼睛颜色]
5. Face feature: [面部特征，眉毛、脸型、鼻子]
6. Height: [身高]
7. Body type: [体型]
8. Appearance: [外貌]
9. Category:  [类别：A,B,C,D,E]
10. Makeup: [妆容]
11. Hairstyle: [发型]
12. Expression: [表情]
13. Posture: [姿势]
14. Actions: [动作]
15. Eye contact: [眼神]
16. Overall temperament: [整体气质]
17. Model attire: [模特服装]
18. Fabric composition or material: [面料成分或材质]
19. Knitting or weaving: [针梭织]
20. Fabric functionality: [面料功能性]
21. Fabric suitable scene: [面料适合场景]
22. Fabric suitable season: [适合季节]
23. Fabric thickness: [面料厚度]
24. Fabric transparency: [面料透明度]
25. Fabric drape: [面料垂感]
26. Fabric softness: [面料柔软度]
27. Fabric sheen: [面料光泽度]
28. Fabric wrinkling: [面料皱感]
29. Whether there is fabric splicing: [是否有面料拼接]
30. Fabric texture and pattern: [面料纹路和图案]
31. Fabric craftsmanship: [面料工艺]
32. Fabric texture and wearing experience: [面料质感和穿着体验感]
33. Accessories: [配饰]
34. Scene and environment: [场景和环境]
35. Background color and tone: [背景颜色和色调]
36. Lighting and illumination: [光线和照明]
37. Props and accessories: [道具和配件]
38. Background details and decorations: [背景细节和装饰]
39. Relationship between model and background: [模特与背景的关系]
40. Text description: [文字描述]
41. Others: [其他]

请确保每个类别都有相应的描述。注意！！！！如果某个类别的信息不可用或不适用，请返回[]，不要返回文字！！！并且一定要返回英文！！！
将返回的结果以key，value的json形式返回，并且其中key只能在以下41个中选择["Overall description","Skin color","Hair color", "Eyes color", "Face feature", "Height","Body type","Appearance","Category","Makeup","Hairstyle","Expression","Posture","Actions","Eye contact","Overall temperament","Model attire","Fabric composition or material","Knitting or weaving","Fabric functionality","Fabric suitable scene","Fabric suitable season","Fabric thickness","Fabric transparency","Fabric drape","Fabric softness","Fabric sheen","Fabric wrinkling","Whether there is fabric splicing","Fabric texture and pattern","Fabric craftsmanship","Fabric texture and wearing experience","Accessories","Scene and environment","Background color and tone","Lighting and illumination","Props and accessories","Background details and decorations","Relationship between model and background","Text description","Others"]。
'''

def encode_image(image_path):
    try:
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')
    except Exception as e:
        logging.error(f"Error encoding image {image_path}: {e}")
        return None

def call_proxy_openai(data, port):
    url = f"http://8.219.81.65:{port}/proxy-openai"
    headers = {
        'Content-Type': 'application/json'
    }
    
    try:
        response = requests.post(url, headers=headers, json=data)
        if response.status_code == 200:
            return response.json()
        else:
            logging.error(f"Error: {response.status_code}")
            logging.error(response.json())
            return None
    except Exception as e:
        logging.error(f"An error occurred: {e}")
        return None

def process_image(image_url, system_prompt, prompt, port):
    try:
        if image_url.startswith('http'):
            image = image_url
        elif os.path.splitext(image_url)[1] in ['.jpg', '.png', '.jpeg', '.bmp']:
            datas = encode_image(image_url)
            if datas is None:
                return None
            image = f"data:image/jpeg;base64,{datas}"
        else:
            raise ValueError("Invalid image URL or path")
        
        data = {
            "model": "gpt-4o-2024-08-06",
            "messages": [
                {
                    "role": "system",
                    "content": system_prompt
                },
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {"type": "image_url", "image_url": {"url": image}}
                    ]
                }
            ],
            "response_format": {"type": "json_object", "strict": True},
            "temperature": 0.6,
            "max_tokens": 4096,
        }
        response = call_proxy_openai(data, port)
        return response
    except Exception as e:
        logging.error(f"Error processing image {image_url}: {e}")
        return None

def parse_response_model(response, goods_id):
    Ethnicity_map = {"A": "Caucasian", "B": "Asian", "C": "Black", "D": "Latino", "E": "Mixed race"}
    try:
        temp_dict = {}
        prefix = response.strip("```").split("{")[0]
        temp = response.strip("```").strip(prefix).strip("\n")
        response_dict = json.loads(temp)
        if "Category" in response_dict:
            for cate_one in ["A", "B", "C", "D", "E"]:
                if cate_one in response_dict["Category"]:
                    response_dict["Category"] = cate_one
            response_dict["Ethnicity"] = Ethnicity_map[response_dict["Category"]]
            del response_dict["Category"]
        else:
            response_dict["Ethnicity"] = []
    except Exception as e:
        logging.info(f"{goods_id}-->解析gpt输出错误：{e}")
        response_dict = {}
    
    categories = [
        "Overall description", "Ethnicity", "Skin color", "Hair color", "Eyes color", "Face feature", 
        "Height", "Body type", "Appearance", "Makeup", "Hairstyle", "Expression", "Posture",
        "Actions", "Eye contact", "Overall temperament", "Model attire",
        "Fabric composition or material", "Knitting or weaving", "Fabric functionality", "Fabric suitable scene", "Fabric suitable season",
        "Fabric thickness", "Fabric transparency", "Fabric drape", "Fabric softness", "Fabric sheen",
        "Fabric wrinkling", "Whether there is fabric splicing", "Fabric texture and pattern", "Fabric craftsmanship",
        "Fabric texture and wearing experience", "Accessories", "Scene and environment", "Background color and tone",
        "Lighting and illumination", "Props and accessories", "Background details and decorations", "Relationship between model and background",
        "Text description", "Others"
    ]
    
    parsed_result = {category: "" for category in categories}
    parsed_result["All_prompts"] = response  # 保存原始响应

    for cate in categories:
        if cate in response_dict:
            parsed_result[cate] = response_dict[cate]

    # 处理未匹配的类别
    for key, value in parsed_result.items():
        if value == []:
            parsed_result[key] = ""

    # 记录空类别
    empty_categories = [cat for cat, value in parsed_result.items() if value == "" and cat != "All_prompts"]
    if empty_categories:
        logging.warning(f"Goods ID {goods_id}: Empty categories: {', '.join(empty_categories)}")

    return parsed_result

def load_processed_ids(output_file):
    processed_ids = set()
    if os.path.exists(output_file):
        with open(output_file, 'r', newline='', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row['All_prompts']:  # 检查是否已处理
                    processed_ids.add(row['goods_id'])
    return processed_ids

def save_result(output_file, result, fieldnames):
    file_exists = os.path.exists(output_file)
    mode = 'a' if file_exists else 'w'
    with open(output_file, mode, newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        if not file_exists:
            writer.writeheader()
        writer.writerow(result)

def main(port, input_file, log_folder, output_folder):
    logger = setup_logging(log_folder, port)
    logger.info(f"Starting script for port {port} with input file {input_file}")
    system_prompt = "你是一个有用的人工智能助手"
    prompt = use_prompt

    os.makedirs(output_folder, exist_ok=True)
    base_name = os.path.splitext(os.path.basename(input_file))[0]
    output_file = os.path.join(output_folder, f'output_{base_name}_{port}.csv')

    fieldnames = ["goods_id", "url", "Overall description", "Ethnicity", "Skin color", "Hair color", "Eyes color", "Face feature",
                  "Height", "Body type", "Appearance", "Makeup", "Hairstyle", "Expression", "Posture",
                  "Actions", "Eye contact", "Overall temperament", "Model attire",
                  "Fabric composition or material", "Knitting or weaving", "Fabric functionality", "Fabric suitable scene", "Fabric suitable season",
                  "Fabric thickness", "Fabric transparency", "Fabric drape", "Fabric softness", "Fabric sheen",
                  "Fabric wrinkling", "Whether there is fabric splicing", "Fabric texture and pattern", "Fabric craftsmanship",
                  "Fabric texture and wearing experience", "Accessories", "Scene and environment", "Background color and tone",
                  "Lighting and illumination", "Props and accessories", "Background details and decorations", "Relationship between model and background",
                  "Text description", "Others", 'All_prompts']

    processed_goods_ids = load_processed_ids(output_file)

    total_lines = sum(1 for _ in open(input_file, 'r'))

    start_time = time.time()
    with open(input_file, 'r') as f:
        pbar = tqdm(f, total=total_lines, desc=f"Processing images (Port {port})", 
                    unit="image", dynamic_ncols=True)
        for line in pbar:
            data = json.loads(line)
            goods_id = data['goods_id']
            
            if goods_id in processed_goods_ids:
                pbar.update(1)
                continue

            try:
                image_url = data['url']
                response = process_image(image_url, system_prompt, prompt, port)
                
                if response:
                    parsed_result = parse_response_model(response, goods_id)
                    result = {'goods_id': goods_id, 'url': image_url, **parsed_result}
                else:
                    logger.warning(f"No response for image {image_url}")
                    result = {'goods_id': goods_id, 'url': image_url, 'All_prompts': "No response received"}
                
                save_result(output_file, result, fieldnames)
                processed_goods_ids.add(goods_id)
            except Exception as e:
                logger.error(f"Error processing goods_id {goods_id}: {e}")
                result = {'goods_id': goods_id, 'url': image_url, 'All_prompts': f"Error: {str(e)}"}
                save_result(output_file, result, fieldnames)

            elapsed_time = time.time() - start_time
            images_processed = pbar.n + 1
            images_per_second = images_processed / elapsed_time
            eta = (total_lines - images_processed) / images_per_second if images_per_second > 0 else 0

            pbar.set_postfix({
                'Elapsed': f'{elapsed_time:.2f}s',
                'ETA': f'{eta:.2f}s',
                'Img/s': f'{images_per_second:.2f}'
            })
            pbar.update(1)

    total_time = time.time() - start_time
    logger.info(f"All results saved to {output_file}")
    logger.info(f"Total processing time: {total_time:.2f} seconds")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Process images with multimodal model')
    parser.add_argument('port', type=str, help='Port number for the API')
    parser.add_argument('input_file', type=str, help='Input file name')
    parser.add_argument('--log_folder', type=str, default='logs', help='Folder to store log files')
    parser.add_argument('--output_folder', type=str, default='outputs', help='Folder to store output files')
    args = parser.parse_args()

    main(args.port, args.input_file, args.log_folder, args.output_folder)