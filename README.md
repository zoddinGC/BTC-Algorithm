Predict Bitcoin's Price
==============================

This project has been created by @zoddinGC.

I am filled with gratitude for the journey that I have embarked on with my Bitcoin algorithm project. Over the past three months, I have encountered numerous difficulties and challenges, spending countless hours working tirelessly to create a powerful tool that uses neural network models to predict Bitcoin's price. Despite spending many lonely hours studying, searching for solutions, and fixing bugs, I remain committed to bringing this project to completion. With the help of TensorFlow, Python, and my machine learning knowledge, I am confident that this algorithm will help people to trade Bitcoin.

Project Organization
------------

    ├── LICENSE
    ├── README.md 
    ├── data
    │   ├── external       <- Module to download data from third party sources.
    │   └── raw            <- The original, immutable data dump.
    │
    ├── docs               <- A default Sphinx project; see sphinx-doc.org for details
    ├── models             <- Trained and serialized models
    ├── notebooks          <- Jupyter notebooks used to study and create the models
    │
    │                                     @zoddinGC
    │                         `11/2022 - initial data exploration`.
    │
    ├── requirements.txt   <- The requirements file for reproducing the analysis environment, e.g.
    │
    ├── setup.py           <- makes project pip installable (pip install -e .) so src can be imported
    ├── src                <- Source code for use in this project.
    │   ├── data_processing.py        <- Module to process and clean the data
    │   ├── upadte_database.py        <- Module to update the data each 15 minute
    │   │   └── data                  <- Where the live data is saved
    │   │
    │   ├── features       <- Scripts to turn raw data into features for modeling
    │   │   ├── check_condition.py    <- Module to check if the condition fofor a trade is met
    │   │   ├── neural_network.py     <- Module to get the neural network model and predict the future condition
    │   │   ├── operation_control_center.py      <- Module to guarantee the start and end for each operation
    │   │   └── prepross_data.py      <- Module for instantiate all classes to increase operation speed
    │   ├── logs                      <- Folder to keep log files and record every candle
    │   │
    │   ├── resources                 <- Folder to keep last 100 candles data, neural network model and standard scaler
    │   │
    │   └── visualization             <- Future development
    │       └── visualize.py
    │
    └── End
