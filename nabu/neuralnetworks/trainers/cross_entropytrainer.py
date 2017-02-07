'''@file cross_enthropytrainer.py
contains the CrossEnthropyTrainer'''

import tensorflow as tf
import trainer
from nabu.neuralnetworks import ops

class CrossEntropyTrainer(trainer.Trainer):
    '''A trainer that minimises the cross-enthropy loss, the output sequences
    must be of the same length as the input sequences'''

    def compute_loss(self, targets, logits, logit_seq_length,
                     target_seq_length):
        '''
        Compute the loss

        Creates the operation to compute the cross-enthropy loss for every input
        frame (if you want to have a different loss function, overwrite this
        method)

        Args:
            targets: a [batch_size, max_target_length] tensor containing the
                targets
            logits: a [batch_size, max_logit_length, dim] tensor containing the
                logits
            logit_seq_length: the length of all the logit sequences as a
                [batch_size] vector
            target_seq_length: the length of all the target sequences as a
                [batch_size] vector

        Returns:
            a scalar value containing the loss
        '''

        with tf.name_scope('cross_enthropy_loss'):
            #append a end of sequence label to the targets to get the encoder
            #outputs, the sos label is the last label
            batch_size = int(targets.get_shape()[0])
            output_dim = int(logits.get_shape()[2])
            s_labels = tf.constant(output_dim-1,
                                   dtype=tf.int32,
                                   shape=[batch_size, 1])
            targets = tf.concat(1, [targets, s_labels])

            targets = tf.expand_dims(targets, 2)

            #convert to non sequential data
            nonseq_targets = ops.seq2nonseq(targets, target_seq_length)
            nonseq_logits = ops.seq2nonseq(logits, logit_seq_length)

            #make a vector out of the targets
            nonseq_targets = tf.reshape(nonseq_targets, [-1])

            #one hot encode the targets
            #pylint: disable=E1101
            nonseq_targets = tf.one_hot(nonseq_targets,
                                        int(nonseq_logits.get_shape()[1]))

            #compute the cross-enthropy loss
            loss = tf.reduce_mean(tf.nn.softmax_cross_entropy_with_logits(
                nonseq_logits, nonseq_targets))

        return loss
