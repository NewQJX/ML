import numpy as np
import tensorflow as tf
import matplotlib.pyplot as plt
from tensorflow.examples.tutorials.mnist import input_data

'''
    LeNet5 implments on tensorflow

'''
class LeNet5:
    def __init__(self):
        self.mnist = input_data.read_data_sets('MNIST_data', one_hot=True)
    def softmax(self, x):
        '''
            softmax function implements with numpy
            parameters:
                x: a numpy array
        '''
        return np.exp(x) / np.sum(np.exp(x), axis = 1, keepdims= True)
    
    #LeNet-5 model
    def inference(self, input_tensor):
        with tf.variable_scope("layer1-conv1"):
            conv1_weight = tf.get_variable(name = "conv1_variable", shape=[5,5,1,6], initializer=tf.truncated_normal_initializer()) * 0.01
            conv1_bias = tf.get_variable(name = "conv1_bias", shape = [6], initializer=tf.constant_initializer(0.0))
            conv1 = tf.nn.conv2d(input = input_tensor, filter = conv1_weight, strides = [1, 1, 1, 1], padding = "VALID")
            relu1 = tf.nn.relu(tf.add(conv1, conv1_bias))
            pool1 = tf.nn.avg_pool(relu1, ksize = [1, 2, 2, 1], strides = [1, 2, 2, 1], padding = "VALID")
        with tf.variable_scope("layer2-conv2"):
            conv2_weight = tf.get_variable(name = "conv2_variable", shape=[5,5,6,16], initializer=tf.truncated_normal_initializer()) * 0.01
            conv2_bias = tf.get_variable(name = "conv2_bias", shape = [16], initializer=tf.constant_initializer(0.0))
            conv2 = tf.nn.conv2d(input = pool1, filter = conv2_weight, strides = [1, 1, 1, 1], padding = "VALID")
            relu2 = tf.nn.relu(tf.nn.bias_add(conv2, conv2_bias))
            pool2 = tf.nn.avg_pool(relu2, ksize = [1,2,2,1], strides = [1,2,2,1], padding = "VALID")
        with tf.variable_scope("layer3-fc1"):
            conv_layer_flatten = tf.layers.flatten(inputs = pool2)      #[batch_size, 256]
            fc1_variable = tf.get_variable(name = 'fc1_variable', shape = [256, 120], initializer = tf.random_normal_initializer()) * 0.01
            fc1_bias = tf.get_variable(name = 'fc1_bias', shape = [1, 120], initializer = tf.constant_initializer(value=0))
            fc1 = tf.nn.relu(tf.add(tf.matmul(conv_layer_flatten, fc1_variable), fc1_bias))     #[batch_size, 120]
        with tf.variable_scope("layer4-fc2"):
            fc2_variable = tf.get_variable(name = "fc2_variable", shape=[120,84], initializer=tf.random_normal_initializer())  * 0.01 #[batch_size, 84]
            fc2_bias = tf.get_variable(name = "fc2_bias", shape=[1, 84],initializer = tf.constant_initializer(value=0))
            fc2 = tf.nn.relu(tf.add(tf.matmul(fc1, fc2_variable), fc2_bias))                    #[batch_size, 84]
        with tf.variable_scope("layer5-output"):
            output_variable = tf.get_variable(name = "output_variable", shape = [84, 10],initializer = tf.random_normal_initializer()) * 0.01
            output_bias = tf.get_variable(name = "output_bias", shape = [1, 10],initializer = tf.constant_initializer(value=0))
            output = tf.nn.sigmoid(tf.add(tf.matmul(fc2, output_variable), output_bias))        #[batch_size, 10]
        return output
    #training model
    def train(self, iter_num = 500, batch_size = 400, learning_rate = 0.1):
        costs = []
        x = tf.placeholder(dtype = tf.float32, shape = [None, 28, 28, 1], name = "x")
        y = tf.placeholder(dtype = tf.float32, shape = [None, 10], name = "y")
        output = self.inference(x)
        cross_entropy = tf.reduce_mean(tf.nn.softmax_cross_entropy_with_logits(logits = output, labels =y, name = "loss"))
        train_step = tf.train.AdamOptimizer(learning_rate).minimize(cross_entropy)

        saver = tf.train.Saver()
        with tf.Session() as sess:
            init = tf.global_variables_initializer()
            sess.run(init)
            for i in range(iter_num):
                batch_xs, batch_ys = self.mnist.train.next_batch(batch_size)
                batch_xs = batch_xs.reshape([-1, 28, 28, 1])
                loss, _ = sess.run([cross_entropy, train_step], feed_dict={x: batch_xs, y: batch_ys})
                costs.append(loss)
                if i % 20 == 0:
                    print("loss after %d iteration is : "%(i) + str(loss))
            saver.save(sess, "./minstModel/model.ckpt")
        plt.figure()
        plt.title("loss")
        plt.xlabel("iteration num")
        plt.ylabel("loss")
        plt.plot(np.arange(0, iter_num), costs)
        plt.show()

    def evaluate(self, images, y_true):
        tf.reset_default_graph()
        x = tf.placeholder(dtype = tf.float32, shape=[None, 28,28,1])
        output = self.inference(x)
        saver = tf.train.Saver()
        with tf.Session() as sess:
            saver.restore(sess, "./minstModel/model.ckpt")
            output = sess.run(output, feed_dict={x:images})
            y_pred = np.argmax(self.softmax(output), axis = 1).reshape(-1, 1)
            #print("y_pred shape is " + str(y_pred.shape))
            accuracy = np.sum(y_pred == y_true) / len(y_pred)
            print("accuracy is " + str(accuracy))
#
if __name__ == "__main__":
    model = LeNet5()
    # model.train(iter_num=200)

    #evaluate model on trainSet
    images_train = model.mnist.train.images
    y_true_train = model.mnist.train.labels
    images_train = images_train.reshape([-1, 28,28,1])
    y_true_train = np.argmax(y_true_train, axis=1).reshape(-1, 1)
    model.evaluate(images_train, y_true_train)          #accuracy is 0.9611818181818181
    #evaluate model on testSet
    images_test = model.mnist.test.images.reshape([-1, 28,28,1])
    y_true_test = model.mnist.test.labels
    y_true_test = np.argmax(y_true_test, axis = 1).reshape(-1, 1)
    model.evaluate(images_test, y_true_test)              #accuracy is 0.9645
    #evaluate model on validate
    images_validation = model.mnist.validation.images.reshape([-1, 28,28,1])
    y_true_validation = model.mnist.validation.labels
    y_true_validation = np.argmax(y_true_validation, axis = 1).reshape(-1, 1)
    model.evaluate(images_validation, y_true_validation)    #accuracy is 0.9648