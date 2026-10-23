import unittest
try:
 import torch
 from ml.pytorch_regression import train
except ImportError:
 torch=None
@unittest.skipUnless(torch is not None,"install ml/requirements-torch.txt")
class TorchModelTest(unittest.TestCase):
 def test_converges_on_synthetic_data(self):
  _,mse=train()
  self.assertLess(mse,0.05)
