# Anomaly Prediction IoT App

This app allows users to predict whether a wind turbine component 
created in an IoT manufacturing setting is functional or
defective, by returning an anomaly score and a prediction.

## What does it do?

The Anomaly Prediction app can predict anomalies using the data
which is fed into it by passing the information through a machine
learning model, which results in a prediction whether the component
is functional or defective, along with an anomaly score and indication
of whether there is a low, medium or high risk of a defect being present.

Users are able to check the model's accuracy from the past week and
will be shown a recommendation to retrain if the rate of defective
components is higher than what can expected under normal operations.

The model can be retrained by the user in the case of data drift or 
changes in the manufacturing process, for which the data from the past
week is used to refit the machine learning model so that it adapts
to the new data and functions better in the future.

Data from the past week or for all time can be viewed by the user
so that they can access historical records as well as check the
defective products in real time.

Finally, the user can clear the database when records are no longer
required, and the predictions will begin again at the next
component serial number to ensure continuity.

## Installation

```shell
pip install -r requirements.txt
```

## Usage

Start

```shell
flask run
```

This runs the flask app, which starts the service on the local machine.
The http:// address shown in the terminal can be used to open the service
and the endpoints within the app can be used to perform the various
actions necessary to monitor the produced components and manage the data.

