from fastapi import APIRouter, UploadFile, File, HTTPException
from PIL import Image
import io
import torch
import torch.nn as nn
import torch.nn.functional as F
from torchvision import transforms

predict_router = APIRouter(prefix="/pdd", tags=["PDD"])

SIGNS = {
    0: {
        "label": "BE CAREFUL, CHILDREN",
        "slug": "children",
        "category": "warning",
        "description": "Осторожно, дети"
    },
    1: {
        "label": "GIVE WAY",
        "slug": "give_way",
        "category": "priority",
        "description": "Уступите дорогу"
    },
    2: {
        "label": "NO ENTRY",
        "slug": "no_entry",
        "category": "prohibitory",
        "description": "Въезд запрещён"
    },
    3: {
        "label": "NO PARKING",
        "slug": "no_parking",
        "category": "prohibitory",
        "description": "Остановка и стоянка запрещены"
    },
    4: {
        "label": "NO TURN",
        "slug": "no_turn",
        "category": "prohibitory",
        "description": "Поворот запрещён"
    },
    5: {
        "label": "PARKING",
        "slug": "parking",
        "category": "information",
        "description": "Парковка"
    },
    6: {
        "label": "PEDESTRIAN",
        "slug": "pedestrian",
        "category": "warning",
        "description": "Пешеходный переход"
    },
    7: {
        "label": "ROAD WORKS",
        "slug": "road_works",
        "category": "warning",
        "description": "Дорожные работы"
    },
    8: {
        "label": "SPEED LIMIT",
        "slug": "speed_limit",
        "category": "prohibitory",
        "description": "Ограничение скорости"
    },
    9: {
        "label": "STOP",
        "slug": "stop",
        "category": "prohibitory",
        "description": "Движение без остановки запрещено"
    },
    10: {
        "label": "MAIN ROAD",
        "slug": "main_road",
        "category": "priority",
        "description": "Главная дорога"
    }
}


class CheckImage(nn.Module):
    def __init__(self):
        super().__init__()
        self.first = nn.Sequential(
            nn.Conv2d(3, 64, kernel_size=3, padding=1),
            nn.BatchNorm2d(64),
            nn.ReLU(),
            nn.MaxPool2d(2),

            nn.Conv2d(64, 128, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.MaxPool2d(2),

            nn.Conv2d(128, 256, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.MaxPool2d(2),

            nn.Conv2d(256, 512, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.MaxPool2d(2),
        )
        self.second = nn.Sequential(
            nn.Flatten(),
            nn.Linear(512 * 8 * 8, 1024),
            nn.ReLU(),
            nn.Linear(1024, 11)
        )

    def forward(self, x):
        x = self.first(x)
        x = self.second(x)
        return x


transform_data = transforms.Compose([
    transforms.Resize((128,128)),
    transforms.ToTensor()
])

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")


model = CheckImage()
model.load_state_dict(torch.load('pdd_model.pth', map_location=device))
model.to(device)
model.eval()



@predict_router.post("/predict")
async def predict(file: UploadFile = File(...)):
    try:
        if file.content_type not in ("image/jpeg", "image/png"):
            raise HTTPException(status_code=400, detail="Формат файла должен быть jpg или png")

        image_bytes = await file.read()
        if not image_bytes:
            raise HTTPException(status_code=400, detail="Файл не загружен")

        image = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        image_tensor = transform_data(image).unsqueeze(0).to(device)

        with torch.no_grad():
            outputs = model(image_tensor)
            probabilities = F.softmax(outputs, dim=1)
            class_id = probabilities.argmax(dim=1).item()
            confidence = probabilities[0][class_id].item()

        sign = SIGNS[class_id]

        return {
            "label": sign["label"],
            "category": sign["category"],
            "description": sign["description"],
            "confidence": round(confidence * 100,2),
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))