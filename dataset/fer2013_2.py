import functools

from tensorflow import keras
import numpy as np

IMAGE_SHAPE = (48, 48, 1)
TRAIN_SIZE = 28709
VALIDATION_SIZE = 3589
TEST_SIZE = 3589
CLASSES = 7

RANDOM_ROTATION_CONFIG = {
    'rotation_range': 30,       # Random rotations from -30 deg to 30 deg
    'width_shift_range': 0.1,
    'height_shift_range': 0.1,
    'horizontal_flip': True,
    'vertical_flip': False,     # Doesn't make sense in FER2013
}


@functools.lru_cache()
def _load_data():
    # 读取数据集内容 (fer2013.csv)
    with open("/Users/libo/Documents/Deep_Learning/datasets/fer2013.csv") as f:
        content = f.readlines()

    lines = np.array(content)

    num_of_instances = lines.size
    print("number of instances: ", num_of_instances)
    print("instance length: ", len(lines[1].split(",")[1].split(" ")))

    # ------------------------------
    # initialize train set and test set
    x_train, y_train, x_test, y_test = [], [], [], []

    # ------------------------------
    # 之前已经加载过数据集，现在将训练集和测试集存储到专用变量中
    for i in range(1, num_of_instances):
        try:
            emotion, img, usage = lines[i].split(",")
            val = img.split(" ")
            pixels = np.array(val, 'float32')
            emotion = keras.utils.to_categorical(emotion, CLASSES)
            if 'Training' in usage:
                y_train.append(emotion)
                x_train.append(pixels)
            elif 'PublicTest' in usage:
                y_test.append(emotion)
                x_test.append(pixels)
        except:
            print("", end="")

    # ------------------------------
    # data transformation for train and test sets
    x_train = np.array(x_train, 'float32')
    y_train = np.array(y_train, 'float32')
    x_test = np.array(x_test, 'float32')
    y_test = np.array(y_test, 'float32')

    # normalize inputs between [0, 1]
    x_train /= 255
    x_test /= 255

    x_train = x_train.reshape(x_train.shape[0], 48, 48, 1)
    x_train = x_train.astype('float32')
    x_test = x_test.reshape(x_test.shape[0], 48, 48, 1)
    x_test = x_test.astype('float32')

    print(x_train.shape[0], 'train samples')
    print(x_test.shape[0], 'test samples')
    print(x_train.shape)

    # y_train = keras.utils.to_categorical(y_train.astype('float32'))
    # y_test = keras.utils.to_categorical(y_test.astype('float32'))

    return (x_train, y_train), (x_test, y_test)


def get_train_generator_for_cnn(batch_size):
    (x_train, y_train), (_, _) = _load_data()

    train_datagen = keras.preprocessing.image.ImageDataGenerator(**RANDOM_ROTATION_CONFIG)
    generator = train_datagen.flow(x_train, y_train, batch_size=batch_size)

    while 1:
        x_batch, y_batch = generator.next()
        yield (x_batch, y_batch)


def get_train_generator_for_capsnet(batch_size):
    for (x_batch, y_batch) in get_train_generator_for_cnn(batch_size):
        yield ([x_batch, y_batch], [y_batch, x_batch])


# def get_validation_data_for_cnn():
#     (_, _), (x_validation, y_validation), (_, _) = _load_data()
#
#     train_datagen = keras.preprocessing.image.ImageDataGenerator(**RANDOM_ROTATION_CONFIG)
#     generator = train_datagen.flow(x_validation, y_validation, batch_size=1)
#
#     x_validation = np.empty_like(x_validation)
#     y_validation = np.empty_like(y_validation)
#
#     for i, (x_batch, y_batch) in enumerate(generator):
#         if i >= VALIDATION_SIZE:
#             break
#         x_validation[i:(i+1)] = x_batch[:]
#         y_validation[i:(i+1)] = y_batch[:]
#
#     return [x_validation, y_validation]


# def get_validation_data_for_capsnet():
#     x_validation, y_validation = get_validation_data_for_cnn()
#     return [[x_validation, y_validation], [y_validation, x_validation]]


def get_test_data_for_cnn(rotation=0.0):
    (_, _), (x_test, y_test) = _load_data()
    x_test = np.array([keras.preprocessing.image.apply_affine_transform(image, theta=rotation) for image in x_test])
    return (x_test, y_test)


def get_test_data_for_capsnet(rotation=0.0):
    x_test, y_test = get_test_data_for_cnn(rotation)
    return [[x_test, y_test], [y_test, x_test]]

