# cloud-vault

<b>1. Description</b>

Cloud Vault is file hosting site where you can store any type of file inclduing your photos, vidoes, pdf and many other things. 

<b>2. Architecture diagram</b>  

Cloud Vault is a web application built with Flask and deployed on Google Cloud Platform. It's containerized using Docker, images are stored in artifact registry and hosted on Cloud Run. User data is stored in Cloud SQL for PostgreSQL, while secrets are managed with Secret Manager. Cloud Storage is used for file uploads, and Terraform is employed for infrastructure provisioning.

![cv-final drawio-11](https://github.com/atharvjoshi34/cloud-vault/assets/109728276/e0ea34e3-c69d-44b9-8e11-56266e874716)

<b>3. Best Practices</b>

- While using cloud always follow the least privilege principles for services account you are using.
- Never use JSON Key file while you are deploying your application on cloud. Rather use IAM based authentication which are far secure than using a JSON key
- Never hardcode a any secret vaule directly in your application. As a industry practice either insert your secret using environemnt variable through your ci/cd pipeline or use some kind of secret manager (used in our case).
- In cloud vault We are using DB username and password to connect to the database make sure you arr
