module.exports = {
  apps : [
  {
    name   : "speech_to_text_service",
    script : "./speech_to_text_service/main.py"
  },
  {
    name   : "facial_emotion_recognition_service",
    script : "./facial_emotion_recognition_service/main.py"
  },
  {
    name : "emotional_speech_recognition_service",
    script : "./emotional_speech_recognition_service/main.py"
  },
  {
    name: "emotion_recognition_service",
    script: "./emotion_recognition_service/main.py"
  },
  {
    name: "text_emotion_recognition_service",
    script: "./text_emotion_recognition_service/main.py"
  },
  {
    name: "dialogue_generation_service",
    script: "./dialogue_generation_service/main.py"
  }
]
}
