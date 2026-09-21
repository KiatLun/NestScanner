from pydantic import BaseModel, Field


class ComponentCreationInput(BaseModel):
    modelName: str
    modelFamily: str
    source: str
    technicalProfile: dict = Field(default_factory=dict)


class ComponentCreationOutput(BaseModel):
    componentName: str

    mainFileContent: str
    requirementsContent: str
    dockerfileContent: str

    imageName: str
    entryPoint: str

    reasoning: str = ""
