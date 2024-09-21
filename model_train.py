# import required libraries
from sklearn.model_selection import train_test_split
import pandas as pd
from sklearn.ensemble import IsolationForest

# import data from CSV file
data = pd.read_csv(r"C:\Users\lucyl\Desktop\University\From Model to Production\streamdata.csv",
                   index_col=False)

# split dataset into training and testing data
train, test = train_test_split(data, test_size=0.2)

# create machine learning model
forest = IsolationForest(random_state=42, contamination=0.1, max_features=3)
forest.fit(train)
anomaly_scores = forest.decision_function(train)
train['scores'] = forest.decision_function(train[['temp', 'humid', 'soundlevel']])
train['anomaly'] = forest.predict(train[['temp', 'humid', 'soundlevel']])

# test accuracy of the model
test_label = (pd.read_csv
              (r"C:\Users\lucyl\Desktop\University\From Model to Production\testwithzandanom.csv",
               index_col=False))
y_predict = forest.predict(test)
y_predictions = pd.DataFrame(y_predict, columns=['anomaly_prediction'])
y_true = test_label['anomaly']
df_test_accuracy = y_predictions.join(y_true, how='right')
df_test_accuracy.loc[df_test_accuracy['anomaly_prediction'] == df_test_accuracy['anomaly'], 'correct?'] = 'Yes'
correct_predictions = df_test_accuracy['correct?'].value_counts()['Yes']
count_row = df_test_accuracy.shape[0]
accuracy_of_test = (correct_predictions/count_row)*100
print("The model's accuracy is:", accuracy_of_test, "%")
