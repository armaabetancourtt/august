"""Synthetic regression example demonstrating gradients and statistical evaluation."""
import numpy as np
import tensorflow as tf
def train(seed=13,epochs=80):
    tf.keras.utils.set_random_seed(seed)
    x=np.linspace(-1,1,200,dtype="float32").reshape(-1,1)
    y=(2.5*x+0.75).astype("float32")
    model=tf.keras.Sequential([tf.keras.layers.Input(shape=(1,)),tf.keras.layers.Dense(8,activation="relu"),tf.keras.layers.Dense(1)])
    model.compile(optimizer=tf.keras.optimizers.Adam(learning_rate=0.03),loss="mse")
    history=model.fit(x,y,epochs=epochs,batch_size=32,verbose=0,validation_split=0.2)
    return model,float(history.history["val_loss"][-1])
if __name__=="__main__":print({"synthetic_validation_mse":train()[1]})
