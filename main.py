import os
import tensorflow as tf
import tensorflow_datasets as tfds
from models import VariationalAutoEncoder
from losses import MSELoss
os.environ["CUDA_VISIBLE_DEVICES"] = "0"


def parse_fn(dataset, input_size=(28, 28)):
    x = tf.cast(dataset['image'], tf.float32)
    x = tf.image.resize(x, input_size)
    x = x / 255.
    return x


dataset = 'mnist'     # 'cifar10', 'fashion_mnist', 'mnist'
log_dirs = 'logs_vae'
batch_size = 64

# Load datasets and setting
AUTOTUNE = tf.data.experimental.AUTOTUNE  # 自動調整模式
combine_split = tfds.Split.TRAIN + tfds.Split.VALIDATION + tfds.Split.TEST
# train_data = tfds.load(dataset, split=combine_split, data_dir='/home/share/dataset/tensorflow-datasets')
train_data = tfds.load(dataset, split=combine_split)
train_data = train_data.shuffle(1000)
train_data = train_data.map(parse_fn, num_parallel_calls=AUTOTUNE)
train_data = train_data.batch(batch_size, drop_remainder=True)      # 如果最後一批資料小於batch_size，則捨棄該批資料
train_data = train_data.prefetch(buffer_size=AUTOTUNE)

# Callbacks function
model_dir = log_dirs + '/models'
os.makedirs(model_dir, exist_ok=True)
model_tb = tf.keras.callbacks.TensorBoard(log_dir=log_dirs)
model_mckp = tf.keras.callbacks.ModelCheckpoint(model_dir + '/best_{epoch:03d}.h5',
                                                monitor='loss',  # TODO: mAP
                                                save_best_only=True,
                                                mode='min')

# Create model
vae = VariationalAutoEncoder()
optimizer = tf.keras.optimizers.Adam(learning_rate=1e-3)
vae.compile(optimizer, loss=MSELoss())
vae.fit(train_data, epochs=50, callbacks=[model_tb, model_mckp])
