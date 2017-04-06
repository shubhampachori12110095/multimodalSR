import logging
import sys

import numpy as np
from six.moves import cPickle

logger_GeneralTools = logging.getLogger('RNN.generalTools')
logger_GeneralTools.setLevel(logging.ERROR)


def path_reader(filename):
    with open(filename) as f:
        path_list = f.read().splitlines()
    return path_list


def load_dataset(file_path):  # TODO: split X_train in train and validation sets
    with open(file_path, 'rb') as cPickle_file:
        a = cPickle.load(cPickle_file)

        # convert from list to numpy array
        # for i in range(len(a)):
        #     lst = np.array(a[i])
        #     a[i] = lst

        [X_train, y_train, X_val, y_val, X_test, y_test] = a

    return X_train, y_train, X_val, y_val, X_test, y_test


def pad_sequences_X(sequences, maxlen=None, padding='post', truncating='post', value=0.):
    """
        Pad each sequence to the same length:
        the length of the longuest sequence.
        If maxlen is provided, any sequence longer
        than maxlen is truncated to maxlen. Truncation happens off either the beginning (default) or
        the end of the sequence.
        Supports post-padding and pre-padding (default).
    """
    lengths = [len(s) for s in sequences]

    nb_samples = len(sequences)
    if maxlen is None:
        maxlen = np.max(lengths)

    # try-except to distinguish between X and y
    datatype = type(sequences[0][0][0]);
    logger_GeneralTools.debug('X data: %s, %s, %s', type(sequences[0][0]), sequences[0][0].shape, sequences[0][0])

    xSize = nb_samples;
    ySize = maxlen;
    zSize = sequences[0].shape[1];
    # sequences = [[np.reshape(subsequence, (subsequence.shape[0], 1)) for subsequence in sequence] for sequence in sequences]

    logger_GeneralTools.debug('new dimensions: %s, %s, %s', xSize, ySize, zSize)
    logger_GeneralTools.debug('intermediate matrix, estimated_size: %s',
                              xSize * ySize * zSize * np.dtype(datatype).itemsize)

    x = (np.ones((xSize, ySize, zSize)) * value).astype(datatype)

    for idx, s in enumerate(sequences):
        if truncating == 'pre':
            trunc = s[-maxlen:]
        elif truncating == 'post':
            trunc = s[:maxlen]
        else:
            raise ValueError("Truncating type '%s' not understood" % padding)

        if padding == 'post':
            x[idx, :len(trunc), :] = trunc
        elif padding == 'pre':
            x[idx, -len(trunc):, :] = np.array(trunc, dtype='float32')
        else:
            raise ValueError("Padding type '%s' not understood" % padding)

    return x


def pad_sequences_y(sequences, maxlen=None, padding='post', truncating='post', value=0.):
    """
        Pad each sequence to the same length:
        the length of the longuest sequence.
        If maxlen is provided, any sequence longer
        than maxlen is truncated to maxlen. Truncation happens off either the beginning (default) or
        the end of the sequence.
        Supports post-padding and pre-padding (default).
    """
    lengths = [len(s) for s in sequences]

    nb_samples = len(sequences)
    if maxlen is None:      maxlen = np.max(lengths)

    datatype = type(sequences[0][0]);
    logger_GeneralTools.debug('Y data: %s, %s, %s', type(sequences[0]), sequences[0].shape, sequences[0])

    xSize = nb_samples;
    ySize = maxlen;
    # sequences = [np.reshape(sequence, (sequence.shape[0], 1)) for sequence in sequences]

    logger_GeneralTools.debug('new dimensions: %s, %s', xSize, ySize)
    logger_GeneralTools.debug('intermediate matrix, estimated_size: %s', xSize * ySize * np.dtype(datatype).itemsize)

    y = (np.ones((xSize, ySize)) * value).astype(datatype)

    for idx, s in enumerate(sequences):
        if truncating == 'pre':
            trunc = s[-maxlen:]
        elif truncating == 'post':
            trunc = s[:maxlen]
        else:
            raise ValueError("Truncating type '%s' not understood" % padding)

        if padding == 'post':
            y[idx, :len(trunc)] = trunc
        elif padding == 'pre':
            y[idx, -len(trunc):] = np.array(trunc, dtype='float32')
        else:
            raise ValueError("Padding type '%s' not understood" % padding)

    return y


def generate_masks(inputs, batch_size):  # inputs = X
    ## all recurrent layers in lasagne accept a separate mask input which has shape
    # (batch_size, n_time_steps), which is populated such that mask[i, j] = 1 when j <= (length of sequence i) and mask[i, j] = 0 when j > (length
    # of sequence i). When no mask is provided, it is assumed that all sequences in the minibatch are of length n_time_steps.
    logger_GeneralTools.debug("* Data information")
    logger_GeneralTools.debug('%s %s', type(inputs), len(inputs))
    logger_GeneralTools.debug('%s %s', type(inputs[0]), inputs[0].shape)
    logger_GeneralTools.debug('%s %s', type(inputs[0][0]), inputs[0][0].shape)
    logger_GeneralTools.debug('%s', type(inputs[0][0][0]))

    max_input_length = max([len(inputs[i]) for i in range(len(inputs))])
    input_dim = len(inputs[0][0])

    logger_GeneralTools.debug("max_seq_len: %d", max_input_length)
    logger_GeneralTools.debug("input_dim: %d", input_dim)

    # X = np.zeros((batch_size, max_input_length, input_dim))
    input_mask = np.zeros((batch_size, max_input_length), dtype='float32')

    for example_id in range(len(inputs)):
        logger_GeneralTools.debug('%d', example_id)
        curr_seq_len = len(inputs[example_id])
        logger_GeneralTools.debug('%d', curr_seq_len)
        # X[example_id, :curr_seq_len] = inputs[example_id]
        input_mask[example_id, :curr_seq_len] = 1

    return input_mask


def query_yes_no(question, default="yes"):
    """Ask a yes/no question via raw_input() and return their answer.

    "question" is a string that is presented to the user.
    "default" is the presumed answer if the user just hits <Enter>.
        It must be "yes" (the default), "no" or None (meaning
        an answer is required of the user).

    The "answer" return value is True for "yes" or False for "no".
    """
    valid = {
        "yes": True, "y": True, "ye": True,
        "no":  False, "n": False
    }
    if default is None:
        prompt = " [y/n] "
    elif default == "yes":
        prompt = " [Y/n] "
    elif default == "no":
        prompt = " [y/N] "
    else:
        raise ValueError("invalid default answer: '%s'" % default)

    while True:
        sys.stdout.write(question + prompt)
        choice = raw_input().lower()
        if default is not None and choice == '':
            return valid[default]
        elif choice in valid:
            return valid[choice]
        else:
            sys.stdout.write("Please respond with 'yes' or 'no' "
                             "(or 'y' or 'n').\n")


def saveToPkl(target_path, dataList):
    with open(target_path, 'wb') as cPickle_file:
        cPickle.dump(
            dataList,
            cPickle_file,
            protocol=cPickle.HIGHEST_PROTOCOL)
    return 0