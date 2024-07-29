import io
from pydub import AudioSegment
from pydub.playback import play
from google.cloud import texttospeech


def play_wav(file_path):
    audio = AudioSegment.from_file(file_path, format = "wav")
    play(audio)


def text_to_speech(text):
    try:
        client = texttospeech.TextToSpeechClient.from_service_account_json("/home/jimin/voicedesk/google_api.json")

        input_text = texttospeech.SynthesisInput(text=text)
        voice_selection = texttospeech.VoiceSelectionParams(
            language_code= "ko-KR",
            name="ko-KR-Wavenet-A"
        )
        audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.LINEAR16
        )

        response = client.synthesize_speech(
            input=input_text,
            voice=voice_selection,
            audio_config=audio_config
        )

        with open("/home/jimin/voicedesk/output.wav", "wb") as out:
          out.write(response.audio_content)
          print('Audio content written to file')
        play_wav("/home/jimin/voicedesk/output.wav")
        
    except Exception as e:
        print("오류 발생:", str(e))
