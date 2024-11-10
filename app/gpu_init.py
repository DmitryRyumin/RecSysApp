"""
File: gpu_init.py
Author: Dmitry Ryumin and Alexandr Axyonov
Description: GPU initialization.
License: MIT License
"""

import torch

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
