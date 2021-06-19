# -*- encoding: utf-8 -*-
"""
-------------------------------------------------
   File Name：    tnews.py
   Description :
   Author :       Wings DH
   Time：         6/16/21 10:40 PM
-------------------------------------------------
   Change Activity:
                   6/16/21: Create
-------------------------------------------------
"""

import sys
import os

os.environ["TF_CPP_MIN_LOG_LEVEL"] = "2"

from modeling.classifier import LabelData
from modeling.mlm_encoder import MlmBertEncoder
from modeling.retriever_classifier import RetrieverClassifier
from utils.cls_train import eval_model, dump_result

sys.path.append('../')
sys.path.append('./')

from utils.data_utils import load_data, load_test_data


def infer(test_data, classifier):
    for d in test_data:
        sentence = d.pop('sentence')
        label = classifier.classify(sentence)
        d['label'] = label
    return test_data


label_2_desc = {'news_tech': '科技',
                'news_entertainment': '娱乐',
                'news_car': '汽车',
                'news_travel': '旅游',
                'news_finance': '财经',
                'news_edu': '教育',
                'news_world': '国际',
                'news_house': '房产',
                'news_game': '电竞',
                'news_military': '军事',
                'news_story': '故事',
                'news_culture': '文化',
                'news_sports': '体育',
                'news_agriculture': '农业',
                'news_stock': '股票'}


def get_data_fp(use_index):
    train_fp = f'dataset/tnews/train_{use_index}.json'
    dev_fp = f'dataset/tnews/dev_{use_index}.json'
    test_fp = 'dataset/tnews/test.json'
    my_test_fp = []
    for ind in range(5):
        if ind != use_index:
            my_test_fp.append(f'dataset/tnews/dev_{ind}.json')
    return train_fp, dev_fp, my_test_fp, test_fp


def main():
    # 参数

    train_fp, dev_fp, my_test_fp, test_fp = get_data_fp(0)
    key_label = 'label_desc'
    key_sentence = 'sentence'
    train_data = load_data(train_fp, key_sentence, key_label)
    dev_data = load_data(dev_fp, key_sentence, key_label)

    # 初始化encoder
    model_path = '../chinese_roberta_wwm_ext_L-12_H-768_A-12'
    prefix = '以下一则关于啊啊的新闻。'
    mask_ind = [6, 7]
    encoder = MlmBertEncoder(model_path, train_data, dev_data, prefix, mask_ind, label_2_desc, 16)

    # fine tune
    data = [LabelData(text, label) for text, label in train_data]
    for epoch in range(20):
        print(f'Training epoch {epoch}')
        encoder.train(1)
        # 加载分类器
        classifier = RetrieverClassifier(encoder, data, n_top=7)

        print('Evel model')
        rst = eval_model(classifier, [dev_fp], key_sentence, key_label)
        print(f'{train_fp} + {dev_fp} -> {rst}')

    classifier = RetrieverClassifier(encoder, data, n_top=3)
    rst = eval_model(classifier, my_test_fp, key_sentence, key_label)
    print(f'{train_fp} + {dev_fp} -> {rst}')
    test_data = load_test_data(test_fp)
    test_data = infer(test_data, classifier)
    dump_result('tnewsf_predict.json', test_data)


if __name__ == "__main__":
    main()