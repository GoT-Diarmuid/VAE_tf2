import os
import numpy as np
import tensorflow as tf
from scipy.stats import norm


class TestDecoder(tf.keras.callbacks.Callback):
    def __init__(self, image_size, log_dir):
        super(TestDecoder, self).__init__()
        self.size = image_size
        self.log_dir = log_dir
        n = 16
        self.save_images = np.zeros((image_size * n, image_size * n))
        self.grid_x = norm.ppf(np.linspace(0.05, 0.95, n))
        self.grid_y = norm.ppf(np.linspace(0.05, 0.95, n))

    def on_train_begin(self, logs=None):
        path = os.path.join(self.log_dir, 'images')
        self.writer = tf.summary.create_file_writer(path)

    def on_epoch_end(self, epoch, logs=None):
        for i, yi in enumerate(self.grid_x):
            for j, xi in enumerate(self.grid_y):
                z_sample = np.array([[xi, yi]])
                img = self.model.layers[1].predict(z_sample)
                self.save_images[i * self.size: (i + 1) * self.size, j * self.size: (j + 1) * self.size] = img[0]
        with self.writer.as_default():
            tf.summary.image("Decoder output", self.save_images, step=epoch)