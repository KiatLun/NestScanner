## Onboarding Workflow

```text
                    [New Research Agent Model]
                               │
                               ▼
                    Known model family?
                      ┌────────┴────────┐
                     Yes                No
                      │                  │
                      ▼                  ▼
          [Use Model-Specific  [Research Evidence + LLM Reasoning
               Downloader]           to determine Download Source]
                      │                  │
                      │                  ▼
                      │      Existing downloader can handle it?
                      │            ┌─────┴─────┐
                      │           Yes          No
                      │            │            │
                      │            ▼            ▼
                      │         [Use It]   Hugging Face?
                      │                      ┌──┴──┐
                      │                     Yes    No
                      │                      │      │
                      │                      ▼      ▼
                      │            [Use Generic HF] [downloader-required]
                      │               Downloader
                      │                      │
                      └──────────────┬───────┘
                                     ▼
                           [Attempt Download]
                                     │
                                     ▼
                           Download succeeds?
                              ┌──────┴──────┐
                             Yes            No
                              │              │
                              ▼              ▼
                         [Verify Cache] [downloader-required]
                              │
                              ▼
                         [Upload Model]
                              │
                              ▼
        [Register in ClearML + Store Files in MinIO]
                              │
                              │ ClearML Model ID
                              ▼
                         [Completed]
```