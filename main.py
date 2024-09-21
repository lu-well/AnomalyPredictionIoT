import mysql.connector
import time
import pandas as pd
import warnings
from model_train import forest

warnings.filterwarnings('ignore')

# Connect to MySQL
conn = mysql.connector.connect(
    host='localhost',
    user='root',
    password='PandaMySQL1992!',
    port='3306',
    database='anomaly_detection'
)
cursor = conn.cursor()


# define function to insert new data to SQL database
def insert_data(temp, humid, sound, defect, anom_score):
    query = ("INSERT INTO predictions_and_scores (temp_value, humid_value, sound_value, defective, anomaly_score)"
             "VALUES (%s, %s, %s, %s, %s)")
    cursor.execute(query, (temp, humid, sound, defect, anom_score))
    conn.commit()


# Simulate data stream
def data_stream():
    try:
        while True:
            # use random values from the sample data to create new data points
            data = pd.read_csv(r"C:\Users\lucyl\Desktop\University\From Model to Production\streamdata.csv",
                               index_col=False)
            temp_value = data['temp'].sample().iloc[0].astype(float)
            humid_value = data['humid'].sample().iloc[0].astype(float)
            sound_value = data['soundlevel'].sample().iloc[0].astype(float)
            # create dataframe from new data points in order to pass it through the prediction model
            new_df = pd.DataFrame(columns=['temp', 'humid', 'soundlevel'])
            new_row = {'temp': temp_value, 'humid': humid_value, 'soundlevel': sound_value}
            new_df = pd.concat([new_df, pd.DataFrame([new_row])], ignore_index=True)
            # predict anomaly and convert these into MySQL readable formats
            score = forest.decision_function(new_df)
            new_score = float(score)
            defective = forest.predict(new_df)
            new_defect = int(defective)
            # insert the data and display the values for each component
            insert_data(temp_value, humid_value, sound_value, new_defect, new_score)
            last_id = cursor.lastrowid
            if defective == 1:
                print(f"Component {last_id} is functional with anomaly score {score}, values are: "
                      f"Temperature: {temp_value}, Humidity: {humid_value}, Sound Level: {sound_value}")
            elif score < -0.099999:
                print(f"Component {last_id} is defective with anomaly score {score}, values are: "
                      f"Temperature: {temp_value}, Humidity: {humid_value}, Sound Level: {sound_value} - HIGH RISK")
            elif -0.099999 < score < -0.009999:
                print(f"Component {last_id} is defective with anomaly score {score}, values are: "
                      f"Temperature: {temp_value}, Humidity: {humid_value}, Sound Level: {sound_value} - MEDIUM RISK")
            elif score > -0.009999:
                print(f"Component {last_id} is defective with anomaly score {score}, values are: "
                      f"Temperature: {temp_value}, Humidity: {humid_value}, Sound Level: {sound_value} - LOW RISK")
            time.sleep(1)  # Wait for 1 second before simulating next data points
    except KeyboardInterrupt:
        print("Data stream simulation stopped.")
        cursor.close()
        conn.close()
