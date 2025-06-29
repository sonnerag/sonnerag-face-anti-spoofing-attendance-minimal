import torch
import torch.nn as nn
import torchvision.models as models

class SLIPNet(nn.Module):
    def __init__(self, num_classes=4):
        super().__init__()
        self.backbone = models.resnet18(pretrained=True)
        self.backbone.fc = nn.Identity()  # type: ignore
        self.classifier = nn.Linear(512, num_classes)
    
    def forward(self, x):
        feat = self.backbone(x)
        out = self.classifier(feat)
        return out, feat