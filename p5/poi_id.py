#!/usr/bin/python

import sys
import pickle
sys.path.append("../tools/")

from feature_format import featureFormat, targetFeatureSplit
from tester import dump_classifier_and_data

### Task 1: Select what features you'll use.
### features_list is a list of strings, each of which is a feature name.
### The first feature must be "poi".


### Load the dictionary containing the dataset
with open("final_project_dataset.pkl", "rb") as data_file:
    data_dict = pickle.load(data_file)

### Task 2: Remove outliers
data_dict.pop( 'TOTAL', 0 )

### Task 3: Create new feature(s)
def computeFraction( poi_messages, all_messages ):
    """ given a number messages to/from POI (numerator) 
        and number of all messages to/from a person (denominator),
        return the fraction of messages to/from that person
        that are from/to a POI
   """


    ### you fill in this code, so that it returns either
    ###     the fraction of all messages to this person that come from POIs
    ###     or
    ###     the fraction of all messages from this person that are sent to POIs
    ### the same code can be used to compute either quantity

    ### beware of "NaN" when there is no known email address (and so
    ### no filled email features), and integer division!
    ### in case of poi_messages or all_messages having "NaN" value, return 0.
    fraction = 0.
    if poi_messages =="NaN" or all_messages =="NaN":
        return 0
    fraction = float(poi_messages)/all_messages


    return fraction

submit_dict = {}
for name in data_dict:

    data_point = data_dict[name]

    from_poi_to_this_person = data_point["from_poi_to_this_person"]
    to_messages = data_point["to_messages"]
    fraction_from_poi = computeFraction( from_poi_to_this_person, to_messages )
    #print (fraction_from_poi)
    data_point["fraction_from_poi"] = fraction_from_poi


    from_this_person_to_poi = data_point["from_this_person_to_poi"]
    from_messages = data_point["from_messages"]
    fraction_to_poi = computeFraction( from_this_person_to_poi, from_messages )
    #print (fraction_to_poi)
    submit_dict[name]={"from_poi_to_this_person":fraction_from_poi,
                       "from_this_person_to_poi":fraction_to_poi,
                      "poi":data_point["poi"]}
    data_point["fraction_to_poi"] = fraction_to_poi
### Store to my_dataset for easy export below.
my_dataset = data_dict
#features_list=['poi','to_messages', 'deferral_payments', 'total_payments', 'loan_advances',
#                'bonus',  'restricted_stock_deferred', 'deferred_income',
#                'total_stock_value', 'expenses', 'from_poi_to_this_person', 'exercised_stock_options', 
#                'from_messages', 'other', 'from_this_person_to_poi', 'salary', 'long_term_incentive',
#                'shared_receipt_with_poi', 'restricted_stock', 'director_fees','fraction_from_poi','fraction_to_poi']
### Extract features and labels from dataset for local testing
#data = featureFormat(my_dataset, features_list, sort_keys = True)
#labels, features = targetFeatureSplit(data)

### Task 4: Try a varity of classifiers
### Please name your classifier clf for easy export below.
### Note that if you want to do PCA or other multi-stage operations,
### you'll need to use Pipelines. For more info:
### http://scikit-learn.org/stable/modules/pipeline.html

#from sklearn.cross_validation import train_test_split
#features_train, features_test, labels_train, labels_test = \
#    train_test_split(features, labels, test_size=0.3, random_state=42)
#
#from sklearn.feature_selection import SelectKBest,f_classif
#
#
#selector = SelectKBest(f_classif, k=5).fit(features_train, labels_train)

### 生成SelectKBest选择出的K个特征列表，选出使得朴素贝叶斯算法最优的特征features_list_NB

#feature = features_list[1:]
#feature_dict ={}
#for i,j in zip(feature,selector.scores_):
#    feature_dict[i]=j
#
#
#kbest_feature = sorted(feature_dict.items(),key=lambda asd:asd[1] ,reverse =True)[:14]
#print(kbest_feature)
#features_list_NB = ['poi']
#for elem in kbest_feature:
#    if elem[0]=='total_payments':
#        continue
#    elif elem[0]=='long_term_incentive':
#        continue
#    elif elem[0]=='loan_advances':
#        continue
#    elif elem[0]=='from_poi_to_this_person':
#        continue
#    elif elem[0]=='other':
#        continue
#    elif elem[0]=='to_messages':
#        continue
#    features_list_NB.append(elem[0])

# Provided to give you a starting point. Try a variety of classifiers.
#from sklearn.naive_bayes import GaussianNB
#clf = GaussianNB()
#test_classifier(clf, my_dataset, features_list_new)

### Task 5: Tune your classifier to achieve better than .3 precision and recall 
### using our testing script. Check the tester.py script in the final project
### folder for details on the evaluation method, especially the test_classifier
### function. Because of the small size of the dataset, the script uses
### stratified shuffle split cross validation. For more info: 
### http://scikit-learn.org/stable/modules/generated/sklearn.cross_validation.StratifiedShuffleSplit.html

# Example starting point. Try investigating other evaluation techniques!

from sklearn.tree import DecisionTreeClassifier
clf = DecisionTreeClassifier(min_samples_split=5, random_state=0)
features_list=['poi','bonus','shared_receipt_with_poi','fraction_to_poi']
### Task 6: Dump your classifier, dataset, and features_list so anyone can
### check your results. You do not need to change anything below, but make sure
### that the version of poi_id.py that you submit can be run on its own and
### generates the necessary .pkl files for validating your results.

dump_classifier_and_data(clf, my_dataset, features_list)