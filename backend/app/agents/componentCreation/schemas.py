from pydantic import BaseModel


class ComponentCreationInput(BaseModel):
    modelName: str
    modelFamily: str
    source: str
    technicalProfile: dict | str
    implementationContext: str


class ComponentCreationOutput(BaseModel):
    componentName: str
    mainFileContent: str
    requirementsContent: str
    dockerfileContent: str
    imageName: str
    entryPoint: str
    reasoning: str