import dataclasses
import logging

import torch

from transformers import (
    AutoModelForSpeechSeq2Seq,
    AutoProcessor,
)

from base_classes.base_inference import (
    BaseInferencePipeline,
)

from base_classes.base_segment_schema import (
    BaseSegmentSchema,
)

logging.basicConfig()


class SttInferenceWhisper(BaseInferencePipeline):

    def __init__(
        self,
        project_name: str,
        task_name: str,
    ):

        super().__init__(
            project_name,
            task_name,
        )

        self.device = "cuda" if torch.cuda.is_available() else "cpu"

    @property
    def model_task(
        self,
    ) -> str:

        return "stt"

    def load_model(
        self,
        model_path: str,
        **kwargs,
    ):

        self.processor = AutoProcessor.from_pretrained(model_path)

        self.model = AutoModelForSpeechSeq2Seq.from_pretrained(model_path)

        self.model.eval()

        self.model.to(self.device)

    def preprocess(
        self,
        audio_path: str,
        item: dict,
        **kwargs,
    ) -> dict:

        waveform, sampleRate = self.safe_load_audio(audio_path)

        segments = [
            BaseSegmentSchema.from_dict(segment)
            for segment in item.get(
                "segments",
                [],
            )
        ]

        language = None

        if len(segments) > 0 and segments[0].language != "":
            language = segments[0].language

        inputs = self.processor(
            waveform,
            sampling_rate=sampleRate,
            return_tensors="pt",
        )

        return {
            "inputs": inputs,
            "language": language,
        }

    def infer(
        self,
        inputs: dict,
        **kwargs,
    ) -> list[BaseSegmentSchema]:

        processorInputs = inputs["inputs"]

        language = inputs.get("language")

        inputFeatures = processorInputs["input_features"].to(self.device)

        generateKwargs = {
            "return_timestamps": True,
        }

        if language:

            generateKwargs["language"] = language

        with torch.no_grad():

            outputIds = self.model.generate(
                inputFeatures,
                **generateKwargs,
            )

        decoded = self.processor.batch_decode(
            outputIds,
            return_timestamps=True,
        )[0]

        segmentList = []

        if isinstance(decoded, dict) and "chunks" in decoded:

            for chunk in decoded["chunks"]:

                timestamp = chunk.get(
                    "timestamp",
                    (
                        0.0,
                        0.0,
                    ),
                )

                start = timestamp[0] if timestamp[0] is not None else 0.0

                end = timestamp[1] if timestamp[1] is not None else 0.0

                text = chunk.get(
                    "text",
                    "",
                ).strip()

                segmentList.append(
                    BaseSegmentSchema(
                        start=start,
                        end=end,
                        processed_transcript=text,
                    )
                )

        else:

            if isinstance(
                decoded,
                str,
            ):
                text = decoded.strip()

            else:
                text = decoded.get("text", "").strip()

            segmentList.append(
                BaseSegmentSchema(
                    start=0.0,
                    end=0.0,
                    processed_transcript=text,
                )
            )

        return segmentList

    def to_segments(
        self,
        inferred: list[BaseSegmentSchema],
        **kwargs,
    ) -> list[dict]:

        return [dataclasses.asdict(segment) for segment in inferred]


if __name__ == "__main__":

    SttInferenceWhisper(
        "echoforge",
        "stt_inference_whisper",
    ).run()
