# Databricks notebook source
# DBTITLE 1,Databricks Input Widgets for Project Setup
# Input Widgets for the Repo URL, Project Name, and Workspace URL
dbutils.widgets.text(name = "repo_url", defaultValue="")
dbutils.widgets.text(name = "project", defaultValue="")
dbutils.widgets.text(name = "workspace_url", defaultValue="")

# Add a widget for the Databricks Secret representing the Databricks Personal Access Token  
dbutils.widgets.text("pat_secret", "databricks_pat", "DB Secret for PAT")

# COMMAND ----------

# DBTITLE 1,Retrieve inputs from Dataricks Widgets
repo_url = dbutils.widgets.get(name="repo_url")
project = dbutils.widgets.get(name="project")
workspace_url = dbutils.widgets.get(name="workspace_url")
print(
f"""
  repo_url = {repo_url}
  project = {project}
  workspace_url = {workspace_url}
"""
)

# COMMAND ----------

# DBTITLE 1,Generating Secret Scope from Current User in Spark
user_name = spark.sql("select current_user()").collect()[0][0]
secret_scope = user_name.split(sep="@")[0].replace(".", "-")
secret_scope

# COMMAND ----------

# DBTITLE 1,Get Personal Access Token from Secrets
db_pat = dbutils.secrets.get(
  scope = secret_scope
  ,key = dbutils.widgets.get("pat_secret")
)

db_pat

# COMMAND ----------

# DBTITLE 1,Create the DAB inititization config file
import json

# Create dab_init_config json 
# note that this is the default-python specificiation based on https://github.com/databricks/cli/blob/a13d77f8eb29a6c7587509721217a137039f20d6/libs/template/templates/default-python/databricks_template_schema.json#L3
dab_init_config = {
    "project_name": project
    ,"include_notebook": "yes"
    ,"include_dlt": "no"
    ,"include_python": "no"
}
dab_init_config = json.dumps(dab_init_config)

# Print dab_init_config as formatted JSON
print(json.dumps(json.loads(dab_init_config), indent=4))

# COMMAND ----------

# DBTITLE 1,Creating a Temporary Directory in Python
from tempfile import TemporaryDirectory

Dir = TemporaryDirectory()
temp_directory = Dir.name

temp_directory

# COMMAND ----------

# DBTITLE 1,Writing Configuration to JSON in Python
with open(f"{temp_directory}/dab_init_config.json", "w") as file:
    file.write(dab_init_config)

# COMMAND ----------

# DBTITLE 1,Use shell to cat the file
import subprocess

result = subprocess.run(f"cat {temp_directory}/dab_init_config.json", shell=True, capture_output=True)
result.stdout.decode("utf-8")

# COMMAND ----------

# DBTITLE 1,Import the dabAssist classes
import dabAssist

# COMMAND ----------

# DBTITLE 1,Create the databricks CLI object
dc = dabAssist.databricksCli(
  workspace_url = workspace_url
  ,db_pat = db_pat
)
dc

# COMMAND ----------

# DBTITLE 1,Install the CLI
dc.install()

# COMMAND ----------

# DBTITLE 1,Configure the CLI Using PAT
dc.configure().returncode

# COMMAND ----------

# DBTITLE 1,Create a Databricks Asset Bundle object
bundle = dabAssist.assetBundle(
  directory = temp_directory
  ,repo_url = repo_url
  ,project = project
  ,cli_path = dc.cli_path
  ,target = "dev"
)

# COMMAND ----------

bundle.initialize(
  template = "default-python"
  ,config_file = "dab_init_config.json"
)

# COMMAND ----------

# MAGIC %environment
# MAGIC "client": "1"
# MAGIC "base_environment": ""
