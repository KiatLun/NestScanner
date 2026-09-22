## Overview of Model Onboarding and Evaluation Workflow

```text
                     [Research Agent]
                            │ 1. Pass a Researched Model
                            ▼
                   [Onboarding Workflow]
                            │
                            │ 1. Download Model
                            │ 2. Upload Model
                            ▼
               [Component Building Workflow]
                            │
                            │ 1. Build new components if needed
                            │ 2. Ensure all component images are available
                            ▼
                [Pipeline Building Workflow]
                            │
                            │ 1. Find all the component images
                            │ 2. Create pipeline yaml
                            ▼
                     [Pipeline Runner]
                            │
                            │ 1. Run pipeline in ClearML
                            ▼
                    [ClearML Execution]
                            │
                            ▼
                  Pipeline succeeds?
                     ┌──────┴──────┐
                    Yes            No
                     │              │
                     ▼              ▼
                [Completed]   [Capture Error]
                                    │
                                    ▼
                             Attempts remaining?
                               ┌────┴────┐
                              Yes        No
                               │          │
                               ▼          ▼
                    [Component Creation Agent] [Failed]
                               │
                               │ Repaired Component
                               └──────────────►
                            [Component Building Workflow]
```