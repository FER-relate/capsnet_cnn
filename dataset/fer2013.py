import functools

from tensorflow import keras
import numpy as np

IMAGE_SHAPE = (48, 48, 1)
TRAIN_SIZE = 28709
VALIDATION_SIZE = 3589
TEST_SIZE = 3589
CLASSES = 6

RANDOM_ROTATION_CONFIG = {
    'rotation_range': 30,       # Random rotations from -30 deg to 30 deg
    'width_shift_range': 0.1,
    'height_shift_range': 0.1,
    'horizontal_flip': True,
    'vertical_flip': False,     # Doesn't make sense in FER2013
}


@functools.lru_cache()
def _load_data():
    x_train = np.load("/Users/libo/Documents/Deep_Learning/Facial_Emotion_Analyzer/FE/x_training.npy")
    y_train = np.load("/Users/libo/Documents/Deep_Learning/Facial_Emotion_Analyzer/FE/y_training.npy")
    x_test = np.load("/Users/libo/Documents/Deep_Learning/Facial_Emotion_Analyzer/FE/x_public.npy")
    y_test = np.load("/Users/libo/Documents/Deep_Learning/Facial_Emotion_Analyzer/FE/y_public.npy")
    x_validation = np.load("/Users/libo/Documents/Deep_Learning/Facial_Emotion_Analyzer/FE/x_private.npy")
    y_validation = np.load("/Users/libo/Documents/Deep_Learning/Facial_Emotion_Analyzer/FE/y_private.npy")

    x_train = x_train.reshape(-1, 48, 48, 1).astype('float32')
    x_test = x_test.reshape(-1, 48, 48, 1).astype('float32')
    x_validation = x_validation.reshape(-1, 48, 48, 1).astype('float32')

    x_train /= 255
    x_test /= 255
    x_validation /= 255

    print(x_train.shape[0], 'train samples')
    print(x_test.shape[0], 'test samples')
    print(x_validation.shape[0], 'validation samples')

    # y_train = keras.utils.to_categorical(y_train.astype('float32'))
    # y_test = keras.utils.to_categorical(y_test.astype('float32'))
    # y_validation = keras.utils.to_categorical(y_validation.astype('float32'))
    print('x_train.shape:', x_train.shape)
    print('y_train.shape:', y_train.shape)
    print('y_validation.shape:', y_validation.shape)

    return (x_train, y_train), (x_validation, y_validation), (x_test, y_test)


def get_train_generator_for_cnn(batch_size):
    # print("debug_test!")
    (x_train, y_train), (_, _), (_, _) = _load_data()
    # print("debug!")
    train_datagen = keras.preprocessing.image.ImageDataGenerator(**RANDOM_ROTATION_CONFIG)
    # print("debug2!")
    generator = train_datagen.flow(x_train, y_train, batch_size=batch_size)
    # print("debug3!")
    # print('y_train.shape',y_train.shape)
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

