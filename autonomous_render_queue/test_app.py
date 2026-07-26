import unittest
import os
import shutil
import numpy as np
from unittest.mock import patch, MagicMock
from app import process_audio, generate_video_chunks, stitch_videos

class TestApp(unittest.TestCase):
    def setUp(self):
        self.test_dir = "test_env"
        if not os.path.exists(self.test_dir):
            os.makedirs(self.test_dir)
        self.test_wav = os.path.join(self.test_dir, "test.wav")
        # create 10 sec wav (about 20 beats at 120bpm)
        from create_test_wav import create_test_wav
        create_test_wav(self.test_wav, duration=10.0)

    def tearDown(self):
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
        if os.path.exists("audio_chunks"):
            shutil.rmtree("audio_chunks")

    def test_process_audio(self):
        chunks, bpm = process_audio(self.test_wav)
        self.assertTrue(bpm > 0)
        self.assertTrue(len(chunks) > 0)
        for chunk in chunks:
            self.assertTrue(os.path.exists(chunk))

    @patch('app.Client')
    def test_generate_video_chunks(self, MockClient):
        mock_instance = MockClient.return_value
        mock_instance.predict.side_effect = [{"video": "dummy_1.mp4"}, {"video": "dummy_2.mp4"}]

        prompts = ["prompt 1", "prompt 2"]
        audio_chunks = ["chunk1.wav", "chunk2.wav"]

        paths = generate_video_chunks(prompts, audio_chunks)
        self.assertEqual(paths, ["dummy_1.mp4", "dummy_2.mp4"])

    @patch('subprocess.run')
    def test_stitch_videos(self, mock_run):
        mock_run.return_value = MagicMock(returncode=0)

        video_chunks = ["dummy_1.mp4", "dummy_2.mp4"]
        output = stitch_videos(video_chunks, self.test_wav, output_path="test_output.mp4")

        self.assertEqual(output, "test_output.mp4")
        self.assertTrue(os.path.exists("concat.txt"))
        mock_run.assert_called_once()
        args, kwargs = mock_run.call_args
        self.assertIn("ffmpeg", args[0])

if __name__ == "__main__":
    unittest.main()
