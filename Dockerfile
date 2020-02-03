FROM tensorflow/tensorflow:latest-py3
ADD . /code
WORKDIR /code
RUN pip install flask \
&& pip install tensorflow-hub \
&& pip install pandas \
&& pip install scikit-learn \
&& pip install tensorflow==2.0.0   \
&& pip install tensorflow-estimator==2.0.1  \
&& pip install tensorflow-text==2.0.1  \
&& pip install tensorflow-hub==0.7.0   \
&& pip install tensorflow-gpu==2.0.0 \
&& pip install tensorflow-addons==0.6.0 \
&& pip install streamlit \
&& curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add - \
&& curl https://packages.microsoft.com/config/ubuntu/18.04/prod.list > /etc/apt/sources.list.d/mssql-release.list \
&& apt-get update \
&& ACCEPT_EULA=Y apt-get -y install msodbcsql17 \
&& apt-get -y install unixodbc unixodbc-dev \
&& pip install pyodbc \
&& apt-get -y install wget \
&& wget https://finetunedweights.blob.core.windows.net/finetuned01/google_use_nrf_pdpa_tuned.tar.gz \
&& tar -zxvf google_use_nrf_pdpa_tuned.tar.gz
CMD ["streamlit", "run", "--server.port", "5000","--server.headless","true", "--browser.serverAddress","0.0.0.0", "--server.enableCORS", "false",  "app2.py"]