import base64

from PIL import Image,PngImagePlugin
from typing import Any

import json

def load_card_data(image_path:str) -> dict[str,Any]:
    """
    读取图片的角色卡数据
    :param image_path: 图片地址
    :return:
    """
    try:
        with Image.open(image_path) as image:
            image.load()
            info = image.info
            raw_b64 = None
            if 'ccv3' in info:
                raw_b64 = info['ccv3']
            elif 'chara' in info:
                raw_b64 = info['chara']
            else:
                raise ValueError("图片中未找到 chara 或 ccv3 元数据")
            return json.loads(base64.b64decode(raw_b64).decode('utf-8'))
    except Exception as e:
        print(f'读取失败：{e}')
        return {}

def save_card_data(image_path:str,output_path:str,card_data:dict[str,Any]):
    """
    将角色卡数据写入图片
    :param image_path: 图片地址
    :param output_path: 输出地址
    :param card_data: 角色卡数据
    :return:
    """
    json_str = json.dumps(card_data)
    base64_str = base64.b64encode(json_str.encode('utf-8')).decode('utf-8')
    metadata = PngImagePlugin.PngInfo()
    metadata.add_text("chara",base64_str)
    metadata.add_text("ccv3",base64_str)
    try:
        with Image.open(image_path) as image:
            image.save(output_path,"PNG",pnginfo=metadata)
    except Exception as e:
        print(f"写入失败：{e}")
        raise e
