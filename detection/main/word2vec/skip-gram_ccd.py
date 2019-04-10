# coding:utf-8
import collections
import math
import re
import numpy as np
import tensorflow as tf


def read_file(filename):
    f = open(filename, 'r')
    file_read = f.read()
    words_ = re.sub(" ", " ", file_read)
    words = list(words_.split())
    return words


# words=read_file('dl4ccd/rw_corpus.txt')
words = read_file('dl4ccd/randowwalk_corpus.txt')
vocabulary_size = 200
count = [['UNK', -1]]


def build_dataset(words):
    counter = collections.Counter(words).most_common(vocabulary_size - 1)
    count.extend(counter)
    dictionary = {}
    for word, _ in count:
        dictionary[word] = len(dictionary)
    data = []
    unk_count = 0
    for word in words:
        if word in dictionary:
            index = dictionary[word]
        else:
            index = 0
            unk_count += 1
        data.append(index)
    count[0][1] = unk_count
    reverse_dictionary = dict(zip(dictionary.values(), dictionary.keys()))
    print(dictionary.values())
    print(dictionary.keys())
    print("reverse_dictionary: ", reverse_dictionary)
    return data, count, dictionary, reverse_dictionary


data, count, dictionary, reverse_dictionary = build_dataset(words)
del words
data_index = 0


def generate_batch(batch_size, num_skips, skip_window):
    global data_index
    assert batch_size % num_skips == 0
    assert num_skips <= 2 * skip_window
    batch = np.ndarray(shape=(batch_size), dtype=np.int32)
    labels = np.ndarray(shape=(batch_size, 1), dtype=np.int32)
    span = 2 * skip_window + 1
    buffer = collections.deque(maxlen=span)
    for _ in range(span):
        buffer.append(data[data_index])
        data_index = (data_index + 1) % len(data)
    for i in range(batch_size // num_skips):
        for j in range(span):
            if j > skip_window:
                batch[i * num_skips + j - 1] = buffer[skip_window]
                labels[i * num_skips + j - 1, 0] = buffer[j]
            elif j == skip_window:
                continue
            else:
                batch[i * num_skips + j] = buffer[skip_window]
                labels[i * num_skips + j, 0] = buffer[j]
        buffer.append(data[data_index])
        data_index = (data_index + 1) % len(data)
    return batch, labels


batch_size = 120
embedding_size = 120
skip_window = 20
num_skips = 10
num_sampled = 8
valid_size = 16
valid_window = 100
valid_examples = np.random.choice(valid_window, valid_size, replace=False)
"""
embedding_size = 50  # Dimension of the embedding vector.
skip_window = 2  # How many words to consider left and right.
num_skips = 4  # How many times to reuse an input to generate a label.
num_sampled = 5  # Number of negative examples to sample.
"""
graph = tf.Graph()
with graph.as_default():
    train_inputs = tf.placeholder(tf.int32, shape=[batch_size])
    train_labels = tf.placeholder(tf.int32, shape=[batch_size, 1])
    valid_dataset = tf.constant(valid_examples, dtype=tf.int32)
    embeddings = tf.Variable(tf.random_uniform([vocabulary_size, embedding_size], -1, 1))
    embed = tf.nn.embedding_lookup(embeddings, train_inputs)
    nce_weights = tf.Variable(
        tf.truncated_normal([vocabulary_size, embedding_size], stddev=1 / math.sqrt(embedding_size)))
    nce_biases = tf.Variable(tf.zeros([vocabulary_size]))
    loss = tf.reduce_mean(
        tf.nn.nce_loss(weights=nce_weights,
                       biases=nce_biases,
                       labels=train_labels,
                       inputs=embed,
                       num_sampled=num_sampled,
                       num_classes=vocabulary_size))

    optimizer = tf.train.GradientDescentOptimizer(1.0).minimize(loss)
    norm = tf.sqrt(tf.reduce_sum(tf.square(embeddings), axis=1, keep_dims=True))
    normalized_embeddings = embeddings / norm
    valid_embeddings = tf.nn.embedding_lookup(normalized_embeddings, valid_dataset)

    init = tf.global_variables_initializer()

num_steps = 2000
with tf.Session(graph=graph) as session:
    init.run()
    print("Initialized")
    avg_loss = 0
    for step in range(num_steps):
        batch_inputs, batch_labels = generate_batch(batch_size, num_skips, skip_window)
        feed_dict = {train_inputs: batch_inputs, train_labels: batch_labels}
        _, loss_val = session.run([optimizer, loss], feed_dict=feed_dict)
        avg_loss += loss_val
        if step % 2000 == 0:
            if step > 0:
                avg_loss /= 2000
            print("Avg loss at step ", step, ": ", avg_loss)
            avg_loss = 0
    final_embedding = normalized_embeddings.eval()

# def writeList(filename):
#     file = shelve.open(filename) #"D:\\v1.dat"
#     dataKey = "myWordList"
#     file[dataKey] = word_list
#     file.close()
#
# writeList('dl4ccd/word_test_cc.dat')

def plot_with_labels(low_dim_embs, labels, filename='randowwalk_corpus_dim4.png'):
    # def plot_with_labels(low_dim_embs, labels, filename='tsnef_rw_win_10_f.png'):
    assert low_dim_embs.shape[0] >= len(labels), 'More labels than embeddings'
    plt.figure(figsize=(25, 25))  # in inches
    for i, label in enumerate(labels):
        x, y = low_dim_embs[i, :]
        plt.scatter(x, y)
        plt.annotate(label,
                     xy=(x, y),
                     xytext=(5, 2),
                     textcoords='offset points',
                     ha='right',
                     va='bottom')

    plt.savefig(filename)


try:
    # pylint: disable=g-import-not-at-top
    from sklearn.manifold import TSNE
    import matplotlib.pyplot as plt
    # from sklearn.preprocessing import StandardScaler
    tsne = TSNE(perplexity=30, n_components=2, init='pca', n_iter=5000)
    plot_only = 500
    low_dim_embs = tsne.fit_transform(final_embedding[:plot_only, :])
    labels = [reverse_dictionary[i] for i in range(len(reverse_dictionary) - 1)]
    # print(np.shape(final_embedding))
    # ss = StandardScaler()
    # std_cps = ss.fit_transform(np.array(final_embedding))
    # for i in range(len(std_cps)):
    #     print(std_cps[i])
    plot_with_labels(low_dim_embs, labels)

except ImportError:
    print('Please install sklearn, matplotlib, and scipy to show embeddings.')
