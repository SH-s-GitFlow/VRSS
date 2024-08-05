from pathlib import Path
import time
import pandas as pd
import argparse
from typing import Any

import torch
import torchvision.transforms as transforms

from utils.datasets import ShipClsDataset
from models.misc import select_model

def multcls(opt: Any) -> None:
    """
    Perform multi-class classification on ship images.

    Args:
        opt (Any): Parsed command line arguments.
    """
    t1 = time.time()

    # 이미지 전처리 -------------------------------------------------------------------
    img_transforms = transforms.Compose([
        transforms.Pad(padding=(opt.img_size, opt.img_size), fill=0),
        transforms.Resize(opt.img_size),
        transforms.CenterCrop(opt.img_size),
        transforms.ToTensor(),
        lambda x: (x > 1000) * 1000 + (x < 1000) * x,
        lambda x: 255 * (x - x.min()) / (x.max() - x.min()),
        lambda x: x / 255,
        lambda x: x.repeat(3, 1, 1),
    ])

    # 모델 및 데이터셋 정의 -----------------------------------------------------------
    model = select_model(opt.classes, opt.meta_file)

    dataset = ShipClsDataset(opt.img_path, transform=img_transforms, classes=opt.classes)

    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    model = model.to(device)
    t2 = time.time()

    # 선종 식별 ----------------------------------------------------------------------
    preds = []
    labels = []
    for img, label in iter(dataset):
        labels.append(label)
        img = img.to(device)
        img = img.unsqueeze(0)
        y_pred, _ = model(img)

        _, top_pred = y_pred.topk(2, 1)
        preds.append(top_pred[0][0].detach().cpu())

    # 식별 결과 저장(현재는 csv, 추후 DB) ---------------------------------------------
    df = pd.DataFrame({
        'FileName': dataset.img_files,
        'TrueClass': [opt.classes[l] for l in labels],
        'PredClass': [opt.classes[p] for p in preds]
    })

    df.to_csv('./outputs/pred.csv', index=False)

    print(f'Done. ({(1E3 * (time.time() - t1)):.1f}ms) Inference, ({(1E3 * (time.time() - t2)):.1f}ms) NMS')

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--img-path', type=str, default='./inputs/ICEYE/', help='image path')
    parser.add_argument('--meta-file', type=str, default='metainfo.json', help='meta info path')
    # 실행 예시: python SAR_shipmultcls.py --img-path {이미지 경로} --meta-file {메타파일 경로} -> 추후 DB 연동

    opt = parser.parse_args()
    opt.classes = ['Cargo', 'Fishing', 'Sailing', 'Tanker', 'TugTow']  # configure file에 지정 가능.
    opt.img_size = 224

    multcls(opt)
