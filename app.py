from flask import Flask
import pandas as pd
from main import cursor, conn
from model_train import forest
import json


app = Flask(__name__)


def check_defects():
    cursor.execute("SELECT defective FROM predictions_and_scores WHERE timestamp "
                   "BETWEEN date_sub(now(),INTERVAL 1 WEEK) and now()")
    defects_last_week = cursor.fetchall()
    str_list = []
    for Tuple in defects_last_week:
        str_list.append(Tuple[0])
    defects = str_list.count(-1)/(len(str_list))*100
    print(f"There were {defects}% defective components produced in the last week")


def insert_data(temp, humid, sound, defect, anom_score):
    query = ("INSERT INTO predictions_and_scores (temp_value, humid_value, sound_value, defective, anomaly_score)"
             "VALUES (%s, %s, %s, %s, %s)")
    cursor.execute(query, (temp, humid, sound, defect, anom_score))
    conn.commit()


@app.route('/predict', methods=['GET'])
def predict():
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
        response = {
            "Serial number": last_id,
            "Temperature": temp_value,
            "Humidity": humid_value,
            "Sound Level": sound_value,
            "Defective": "No",
            "Anomaly Score": new_score
            }
        return json.dumps(response)
    elif score < -0.099999:
        response = {
            "Serial number": last_id,
            "Temperature": temp_value,
            "Humidity": humid_value,
            "Sound Level": sound_value,
            "Defective": "Yes - HIGH RISK",
            "Anomaly Score": new_score
        }
        return json.dumps(response)
    elif -0.099999 < score < -0.009999:
        response = {
            "Serial number": last_id,
            "Temperature": temp_value,
            "Humidity": humid_value,
            "Sound Level": sound_value,
            "Defective": "Yes - MEDIUM RISK",
            "Anomaly Score": new_score
        }
        return json.dumps(response)
    elif score > -0.009999:
        response = {
            "Serial number": last_id,
            "Temperature": temp_value,
            "Humidity": humid_value,
            "Sound Level": sound_value,
            "Defective": "Yes - LOW RISK",
            "Anomaly Score": new_score
        }
        return json.dumps(response)
    cursor.close()
    conn.close()


@app.route('/checkdefects', methods=['GET'])
def defect_check():
    cursor.execute("SELECT defective FROM predictions_and_scores WHERE timestamp "
                   "BETWEEN date_sub(now(),INTERVAL 1 WEEK) and now()")
    defects_last_week = cursor.fetchall()
    str_list = []
    for Tuple in defects_last_week:
        str_list.append(Tuple[0])
    defects = str_list.count(-1) / (len(str_list)) * 100
    if defects > 15:
        response = {
            "% of defective items produced in the last week": defects,
            "Suggestion": "Retrain model"
        }
        return json.dumps(response)
    else:
        response = {
            "% of defective items produced in the last week": defects
        }
        return json.dumps(response)


@app.route('/downloadall', methods=['GET'])
def download_file_all():
    query = "SELECT * FROM predictions_and_scores"
    data_frame = pd.read_sql(query, conn)
    return json.dumps(json.loads(data_frame.to_json(orient="records")))


@app.route('/downloadlastweek', methods=['GET'])
def download_file_last_week():
    query = "SELECT * FROM predictions_and_scores  WHERE timestamp BETWEEN date_sub(now(),INTERVAL 1 WEEK) and now()"
    data_frame = pd.read_sql(query, conn)
    return json.dumps(json.loads(data_frame.to_json(orient="records")))


@app.route('/retrain', methods=['GET'])
def retrain_from_last_week_data():
    query = ("SELECT temp_value, humid_value, sound_value FROM predictions_and_scores  "
             "WHERE timestamp BETWEEN date_sub(now(),INTERVAL 1 WEEK) and now()")
    data_frame = pd.read_sql(query, conn)
    forest.fit(data_frame)
    response = {
            "Message": "Model has been successfully retrained using the data from last week"
        }
    return json.dumps(response)


@app.route('/clearalldata', methods=['GET'])
def clear_data():
    cursor.execute("SELECT serial_number FROM predictions_and_scores ORDER BY serial_number DESC LIMIT 1")
    last_id = cursor.fetchone()
    int_last_id = int(last_id[0])
    new_serial_number = int_last_id + 1
    cursor.execute("DELETE FROM predictions_and_scores")
    query = "ALTER TABLE predictions_and_scores AUTO_INCREMENT = %s"
    cursor.execute(query, (new_serial_number,))
    response = {
            "Message": "Historical data cleared",
            "Next component serial number": new_serial_number
        }
    return json.dumps(response)
