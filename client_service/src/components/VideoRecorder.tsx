import { useState, useEffect, useRef } from "react";
import RecordRTC, { getSeekableBlob, invokeSaveAsDialog } from "recordrtc";
import { blobToBase64 } from "../utils";
import axios from "axios";

const VideoRecorder = () => {
    const [stream, setStream] = useState<MediaStream | null>(null);
    const refVideo = useRef<any>(null);
    const recorderRef = useRef<RecordRTC | null>(null);
    const handleRecording = async () => {
      const mediaStream = await navigator.mediaDevices.getUserMedia({ video: true, audio: true });
      setStream(mediaStream);
      recorderRef.current = new RecordRTC(mediaStream, { type: 'video', mimeType:'video/webm', numberOfAudioChannels: 1, sampleRate: 44100});
      recorderRef.current.startRecording();
    };
  
    const handleStop = async () => {
      if (recorderRef.current) {
        recorderRef.current.stopRecording(async () => {
            if (recorderRef.current) 
            {
                const blob = recorderRef.current.getBlob();
                getSeekableBlob(blob, async (output) => {
                  invokeSaveAsDialog(output);
                  const file = new File([output], 'video.webm');
                  const formData = new FormData();
                  formData.append('file', file);
                  const result = await axios.post('http://localhost:8000/', formData, {headers: { "Content-Type": "multipart/form-data" }})
                  console.log(result)
                })
            }
        }); 
      }
    };

  
    useEffect(() => {
      if (!refVideo.current) {
        return;
      }
  
    refVideo.current.srcObject = stream;
    }, [stream, refVideo]);
    

    return (
        <div className="flex flex-col">
                <div className="flex justify-evenly p-5">
                    <button onClick={handleRecording} className="text-white border rounded bg-gray-800 py-2 px-4">Start</button>
                    <button onClick={handleStop} className="text-white border rounded bg-gray-800 py-2 px-4">Stop</button>
                </div>

          <video
            controls
            autoPlay
            ref={refVideo}
            style={{ width: '700px', margin: '1em' }}
          />

        </div>
    );
};
export default VideoRecorder;