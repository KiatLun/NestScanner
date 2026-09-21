## Pipeline Building Workflow

```text
                    [Pipeline Building Workflow]
                               │
                               │ Component Result
                               │ + ClearML Model ID
                               │ + Dataset ID
                               ▼
                    [Build Inference Stage]
                               │
                               ▼
                   [Build Evaluation Stage]
                               │
                               ▼
                  [Link Stage Dependencies]
                               │
                               ▼
              [Generate EchoForge Pipeline YAML]
                               │
                               ▼
                    [Save Pipeline Config]
                               │ Pipeline YAML
                               ▼
                         [Completed]
```