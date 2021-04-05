# This repo is the Backend for my [Automated One Report iOS application](https://github.com/uryyakir/AutomatedOneReportApp).<br>
### The backend is structured in the following manner:
![](https://github.com/uryyakir/AutomatedOneReportServerPublic/blob/master/git/Server%20Side%20Architecture.png?raw=true)
- The backend is composed of three services:
  1. AWS EC2 Linux machine
  2. AWS Elasticsearch cluster
  3. Let's encrypt Certbot service<br>
- When some client is using the app, his requests are processed in the following manner:
  1. The request is first directed to the **NGINX reverse proxy** via HTTPS protocol.<br>HTTP requests to NGINX are automatically redirected to HTTPS.
  2. The proxy redirects the request internally to port 8080.
  3. Listening on port 8080 is a **Docker container** that contains a **Gunicorn webserver**.
  4. The webserver's logic is written using FastAPI - a Python framework for building APIs.<br>
  5. After the server handles the request, it directs the response from port 8080 back to port 443 (proxy).
  6. Finally, the proxy directs the response back to said client.
- As part of the webserver's functionality, the server supports:
    - Data manipulation (via communication with Elasticsearch cluster)
    - Communication with Apple's APN service
    - Hosting of https://automated-one-report.club/support webpage.
    - **Most importantly - sending the actual HTTP requests to one.prat.idf.il API** on behalf of the app's users.
