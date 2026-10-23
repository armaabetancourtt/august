"""Deterministic synthetic-only torch demo; never claim trained property valuations."""
import torch
def train(seed=42,steps=200):
    torch.manual_seed(seed)
    x=torch.linspace(-1,1,128).reshape(-1,1)
    y=3*x+0.5
    model=torch.nn.Linear(1,1)
    optim=torch.optim.Adam(model.parameters(),lr=0.06)
    for _ in range(steps):
        optim.zero_grad()
        loss=torch.mean((model(x)-y)**2)
        loss.backward()
        optim.step()
    return model,float(torch.mean((model(x)-y)**2).detach())
if __name__=="__main__":
    _,loss=train()
    print({"synthetic_mse":loss})
