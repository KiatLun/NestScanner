## Component Building Workflow

```text
                 [Component Building Workflow]
                            │
                            ▼
                 [Resolve Model Family]
                            │
                            ▼
          [Find Existing Inference Component]
                            │
                            ▼
                 Existing component found?
                     ┌──────┴──────┐
                    Yes            No
                     │              │
                     ▼              ▼
              [Use Existing] [Component Creation Agent]
                     │              │
                     └──────┬───────┘
                            │ Inference Component
                            ▼
                 [Resolve Docker Config]
                            │
                            ▼
                  Docker image exists?
                     ┌──────┴──────┐
                    Yes            No
                     │              │
                     │              ▼
                     │      [Build Docker Image]
                     │              │
                     └──────┬───────┘
                            │ Inference Image
                            ▼
             [Resolve Evaluation Component]
                            │
                            ▼
              [Ensure Evaluation Image]
                            │ Component Result
                            ▼
                       [Completed]
```