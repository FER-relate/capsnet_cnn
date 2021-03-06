import functools
import os
import cv2
from PIL import Image

from tensorflow import keras
import numpy as np

from sklearn.model_selection import train_test_split

IMAGE_SHAPE = (64, 64, 3)
TRAIN_SIZE = 149
VALIDATION_SIZE = 51
TEST_SIZE = 13
CLASSES = 7

RANDOM_ROTATION_CONFIG = {
    'rotation_range': 30,       # Random rotations from -30 deg to 30 deg
    'width_shift_range': 0.2,
    'height_shift_range': 0.2,
    'horizontal_flip': True,
    'vertical_flip': True,
}


@functools.lru_cache()
def _load_data():

    trainPath = '/Users/libo/Documents/Deep_Learning/CapsNet_vs_CNN/data/jaffe_64'

    train_label = []

    train_total = []

    ##################
    #    加载 train   #
    ##################
    for root, dirs, files in os.walk(trainPath):
        for filename in (x for x in files if x.endswith(('.jpg', '.tiff', '.png'))):
            filepath1 = os.path.join(root, filename)
            object_class = filepath1.split('\\')[-1]    # 情感标签
            if object_class == 'AN':
                train_label.append(0)
            elif object_class == 'DI':
                train_label.append(1)
            elif object_class == 'FE':
                train_label.append(2)
            elif object_class == 'HA':
                train_label.append(3)
            elif object_class == 'SA':
                train_label.append(4)
            elif object_class == 'SU':
                train_label.append(5)
            else:
                train_label.append(6)
            image = np.array(Image.open(filepath1))
            # ddd = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            train_total.append(image)
    train_total2 = np.array(train_total)
    print('训练图片总维度', train_total2.shape)

    X = np.array(train_total2)
    y = np.array(train_label)

    x_train, x_test, y_train, y_test = train_test_split(X, y, test_size=0.30, random_state=42)
    x_validation, x_test, y_validation, y_test = train_test_split(x_test, y_test, test_size=0.2, random_state=42)

    x_train = x_train.reshape(-1, 64, 64, 3).astype('float32')
    x_train /= 255
    print(x_train.shape[0], 'train samples')
    print('X_train:', x_train.shape)
    y_train = keras.utils.to_categorical(y_train.astype('float32'))
    print('y_train.shape:', y_train.shape)

    x_validation = x_validation.reshape(-1, 64, 64, 3).astype('float32')
    x_validation /= 255
    print(x_validation.shape[0], 'validation samples')
    print('x_validation:', x_validation.shape)
    y_validation = keras.utils.to_categorical(y_validation.astype('float32'))
    print('y_validation.shape:', y_validation.shape)

    x_test = x_test.reshape(-1, 64, 64, 3).astype('float32')
    x_test /= 255
    print(x_test.shape[0], 'test samples')
    print('x_test:', x_test.shape)
    y_test = keras.utils.to_categorical(y_test.astype('float32'))
    print('y_test.shape:', y_test.shape)

    return (x_train, y_train), (x_validation, y_validation), (x_test, y_test)

_load_data()


def get_train_generator_for_cnn(batch_size):
    (x_train, y_train), (_, _), (_, _) = _load_data()
    train_datagen = keras.preprocessing.image.ImageDataGenerator(**RANDOM_ROTATION_CONFIG)
    generator = train_datagen.flow(x_train, y_train, batch_size=batch_size)
    print(y_train)
    while 1:
        x_batch, y_batch = generator.next()
        yield [x_batch, y_batch]


def get_train_generator_for_capsnet(batch_size):
    for (x_batch, y_batch) in get_train_generator_for_cnn(batch_size):
        yield ([x_batch, y_batch], [y_batch, x_batch])


def get_validation_data_for_cnn():
    (_, _), (x_validation, y_validation), (_, _) = _load_data()
    train_datagen = keras.preprocessing.image.ImageDataGenerator(**RANDOM_ROTATION_CONFIG)
    generator = train_datagen.flow(x_validation, y_validation, batch_size=1)

    x_validation = np.empty_like(x_validation)
    y_validation = np.empty_like(y_validation)

    for i, (x_batch, y_batch) in enumerate(generator):
        if i >= VALIDATION_SIZE:
            break
        x_validation[i:(i+1)] = x_batch[:]
        y_validation[i:(i+1)] = y_batch[:]

    return [x_validation, y_validation]


def get_validation_data_for_capsnet():
    x_validation, y_validation = get_validation_data_for_cnn()
    return [[x_validation, y_validation], [y_validation, x_validation]]


def get_test_data_for_cnn(rotation=0.0):
    (_, _), (_, _), (x_test, y_test) = _load_data()
    x_test = np.array([keras.preprocessing.image.apply_affine_transform(image, theta=rotation) for image in x_test])
    return (x_test, y_test)


def get_test_data_for_capsnet(rotation=0.0):
    x_test, y_test = get_test_data_for_cnn(rotation)
    return [[x_test, y_test], [y_test, x_test]]

