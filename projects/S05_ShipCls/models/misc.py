import torch
from collections import namedtuple
from typing import List, Any

from models.shipclsmodel import Bottleneck, ShipClsModel
from utils.datasets import read_platform

def create_model(model_config: namedtuple, classes: List[str], meta_file: str) -> ShipClsModel:
    """
    Creates and loads the model with pre-trained weights based on the platform.

    Args:
        model_config (namedtuple): Configuration for the model architecture.
        classes (List[str]): List of class labels.
        meta_file (str): Path to the metadata file.

    Returns:
        ShipClsModel: The initialized and pre-trained ship classification model.
    """
    OUTPUT_DIM = len(classes)
    model = ShipClsModel(model_config, OUTPUT_DIM)
    
    platform = read_platform(meta_file)
    if platform not in ['ICEYE', 'K5']:  # 모델 없는 플랫폼 config file에 지정
        platform = 'GENERAL'  # 모델 없는 경우 일반화된 모델 적용 
    
    model.load_state_dict(torch.load(f'./models/weights/{platform}.pt'))
    model.eval()
    return model

def select_model(classes: List[str], meta_file: str) -> ShipClsModel:
    """
    Selects and creates the pre-trained ship classification model.

    Args:
        classes (List[str]): List of class labels.
        meta_file (str): Path to the metadata file.

    Returns:
        ShipClsModel: The pre-trained ship classification model.
    """
    ResNetConfig = namedtuple('ResNetConfig', ['block', 'n_blocks', 'channels'])
    model_config = ResNetConfig(
        block=Bottleneck,
        n_blocks=[3, 8, 36, 3],
        channels=[64, 128, 256, 512]
    )
    
    pretrained_model = create_model(model_config, classes, meta_file)
    
    return pretrained_model
