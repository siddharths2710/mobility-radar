# Mobility-Radar for Microsoft Azure Hackathon

This repository provides the source files to run the mobility-radar solution, with the intention of deploying the server code onto Azure Serverless based Python App Service. The below UML diagram describes the basic workflow between Azure components and the client.

The ideation is attributed to being shortlisted as a semi-finalist in the Microsoft Azure Hackathon 2020.

**Team Name:** GreenCorridor

**URI**: [Microsoft Azure Hackathon 2020](https://www.hackerearth.com/challenges/hackathon/microsoft-azure-java-hackathon)

## Use Case Diagram

<img src="https://i.imgur.com/FfHcjle.png" width="800px"/>
----------------------

It has been noticed that standard queries took quite a long time ( close to a minute to be precise ) when the App service was made to read the vantage points directly from Cosmos DB. For the sake of the prototype, a Blob file is being used instead since it stores a **K-D Tree** which can efficiently retrieve the nearest neighbours for the current location in a matter of seconds.


## Quickstart

 - To test the app service locally, you must have Python 3.x with `pip` installed.
 - You may use virtual environment to install dependencies privately: `python3 -m venv venv`
 - Install the required Python modules: `pip install -r requirements.txt`
 - Set the script runtime: `export FLASK_APP=application.py`
 - Run the service locally using the cmd `flask run`
 - On your browser, navigate to `http://machine_IP:<running_port>`
 - You should see the landing page. You may choose to either find services in your area ( Grant **location** permission ) or you can choose to view the existing regions that are stored in the Cosmos DB collection.
 - To provide ease of convenience in adding a newly available service vantage point into Cosmos DB, a helper script is provided to achieve the same: `python helper_write_data_model_cosmos.py`
 - Once an update is done in Cosmos, the Blob File must be updated as well for the App service to read the same: `python helper_gen_pickle_frm_cosmos.py`
 - Deploy the web app using Azure CLI: `az webapp up -n <webapp-name> --sku <tier>`, or through a CI workflow using [GitHub Actions](https://github.com/Azure/webapps-deploy)
