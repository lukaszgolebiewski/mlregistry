from azure.identity import DefaultAzureCredential
from azure.ai.ml import MLClient
from azure.ai.ml.entities import Model, ManagedOnlineEndpoint, ManagedOnlineDeployment
from azure.ai.ml.constants import AssetTypes

# =========================
# CONFIGURATION
# =========================
SUBSCRIPTION_ID = "a05d42ef-e511-4033-9ece-d4ea89bcd987"
RESOURCE_GROUP = "lukasztest"
WORKSPACE_NAME = "lukasztest"
REGISTRY_NAME = "lukaszTest"

MODEL_NAME = "my-model"
MODEL_PATH = "./model"   # local folder or file

ENDPOINT_NAME = "lukasz-endpoint"
DEPLOYMENT_NAME = "blue"

# =========================
# AUTHENTICATION
# =========================
credential = DefaultAzureCredential()

# Workspace client (for deployment)
ml_client = MLClient(
    credential,
    SUBSCRIPTION_ID,
    RESOURCE_GROUP,
    WORKSPACE_NAME
)

# Registry client (IMPORTANT)
registry_client = MLClient(
    credential,
    SUBSCRIPTION_ID,
    RESOURCE_GROUP,
    registry_name=REGISTRY_NAME
)

# =========================
# STEP 1: REGISTER MODEL IN REGISTRY
# =========================
model = Model(
    path=MODEL_PATH,
    name=MODEL_NAME,
    type=AssetTypes.CUSTOM_MODEL,
    description="Model stored in Azure ML Registry"
)

registered_model = registry_client.models.create_or_update(model)

print(f"Registered model: {registered_model.name}:{registered_model.version}")

# =========================
# STEP 2: CREATE ENDPOINT
# =========================
endpoint = ManagedOnlineEndpoint(
    name=ENDPOINT_NAME,
    auth_mode="key"
)

ml_client.online_endpoints.begin_create_or_update(endpoint).result()

# =========================
# STEP 3: DEPLOY MODEL FROM REGISTRY
# =========================
deployment = ManagedOnlineDeployment(
    name=DEPLOYMENT_NAME,
    endpoint_name=ENDPOINT_NAME,
    model=f"azureml://registries/{REGISTRY_NAME}/models/{MODEL_NAME}/versions/{registered_model.version}",
    instance_type="Standard_DS3_v2",
    instance_count=1
)

ml_client.online_deployments.begin_create_or_update(deployment).result()

# =========================
# STEP 4: ROUTE TRAFFIC
# =========================
endpoint.traffic = {DEPLOYMENT_NAME: 100}
ml_client.online_endpoints.begin_create_or_update(endpoint).result()

print("Deployment completed!")